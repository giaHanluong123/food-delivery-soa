from datetime import datetime
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


@router.post("/create", response_model=PaymentResponse)
def create_payment(payload: CreatePaymentRequest, db: Session = Depends(get_db)):
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    transaction_code = f"PAY-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    payment = PaymentTransaction(
        transaction_code=transaction_code,
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
    payments = db.query(PaymentTransaction).order_by(PaymentTransaction.id.asc()).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    payment = db.query(PaymentTransaction).filter(PaymentTransaction.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment


@router.post("/{payment_id}/callback", response_model=PaymentResponse)
def payment_callback(payment_id: int, payload: PaymentCallbackRequest, db: Session = Depends(get_db)):
    payment = db.query(PaymentTransaction).filter(PaymentTransaction.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    allowed_statuses = ["paid", "failed"]
    if payload.payment_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="payment_status must be 'paid' or 'failed'")

    payment.payment_status = payload.payment_status
    payment.gateway_transaction_id = payload.gateway_transaction_id
    payment.callback_message = payload.callback_message

    db.commit()
    db.refresh(payment)

    return payment


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(payment_id: int, payload: RefundPaymentRequest, db: Session = Depends(get_db)):
    payment = db.query(PaymentTransaction).filter(PaymentTransaction.id == payment_id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.payment_status != "paid":
        raise HTTPException(status_code=400, detail="Only paid transaction can be refunded")

    payment.payment_status = "refunded"
    payment.refund_reason = payload.reason

    db.commit()
    db.refresh(payment)

    return payment