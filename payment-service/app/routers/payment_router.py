from datetime import datetime
from uuid import uuid4
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import PaymentTransaction
from app.schemas.payment import (
    CreatePaymentRequest,
    PaymentCallbackRequest,
    PaymentResponse,
    RefundPaymentRequest,
)

router = APIRouter(prefix="/payments", tags=["Payments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_transaction_code() -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    short_uuid = uuid4().hex[:8].upper()
    return f"PAY-{timestamp}-{short_uuid}"


@router.post("/create", response_model=PaymentResponse)
def create_payment(payload: CreatePaymentRequest, db: Session = Depends(get_db)):
    existing_pending_payment = (
        db.query(PaymentTransaction)
        .filter(
            PaymentTransaction.order_id == payload.order_id,
            PaymentTransaction.payment_status.in_(["pending", "paid"])
        )
        .first()
    )

    if existing_pending_payment:
        raise HTTPException(
            status_code=400,
            detail="Order already has a pending or paid payment transaction"
        )

    payment = PaymentTransaction(
        transaction_code=generate_transaction_code(),
        order_id=payload.order_id,
        user_id=payload.user_id,
        amount=payload.amount,
        payment_method=payload.payment_method,
        payment_status="pending",
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("", response_model=List[PaymentResponse])
def list_payments(db: Session = Depends(get_db)):
    payments = (
        db.query(PaymentTransaction)
        .order_by(PaymentTransaction.id.asc())
        .all()
    )
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = (
        db.query(PaymentTransaction)
        .filter(PaymentTransaction.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment


@router.post("/{payment_id}/callback", response_model=PaymentResponse)
def payment_callback(
    payment_id: int,
    payload: PaymentCallbackRequest,
    db: Session = Depends(get_db)
):
    payment = (
        db.query(PaymentTransaction)
        .filter(PaymentTransaction.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.payment_status == "refunded":
        raise HTTPException(
            status_code=400,
            detail="Refunded payment cannot receive callback"
        )

    if payment.payment_status in ["paid", "failed"]:
        raise HTTPException(
            status_code=400,
            detail="Payment callback already processed"
        )

    payment.payment_status = payload.payment_status
    payment.gateway_transaction_id = payload.gateway_transaction_id
    payment.callback_message = payload.callback_message

    db.commit()
    db.refresh(payment)
    return payment


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(
    payment_id: int,
    payload: RefundPaymentRequest,
    db: Session = Depends(get_db)
):
    payment = (
        db.query(PaymentTransaction)
        .filter(PaymentTransaction.id == payment_id)
        .first()
    )

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.payment_status != "paid":
        raise HTTPException(
            status_code=400,
            detail="Only paid transaction can be refunded"
        )

    payment.payment_status = "refunded"
    payment.refund_reason = payload.reason

    db.commit()
    db.refresh(payment)
    return payment