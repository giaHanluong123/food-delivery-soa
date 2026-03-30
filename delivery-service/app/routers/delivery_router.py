import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import DeliveryJob, Shipper
from app.schemas.delivery import (
    DeliveryAssignRequest,
    DeliveryCreateRequest,
    DeliveryResponse,
    DeliveryStatusUpdateRequest,
    ShipperCreate,
    ShipperResponse,
    TrackingResponse,
    TrackingUpdateRequest,
)
from app.services.redis_client import get_redis_client

router = APIRouter(tags=["Delivery"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/shippers", response_model=ShipperResponse)
def create_shipper(payload: ShipperCreate, db: Session = Depends(get_db)):
    existing_shipper = db.query(Shipper).filter(Shipper.phone == payload.phone).first()
    if existing_shipper:
        raise HTTPException(status_code=400, detail="Phone already exists")

    shipper = Shipper(
        full_name=payload.full_name,
        phone=payload.phone,
        vehicle_type=payload.vehicle_type,
        is_active=payload.is_active,
    )

    db.add(shipper)
    db.commit()
    db.refresh(shipper)

    return shipper


@router.get("/shippers", response_model=List[ShipperResponse])
def list_shippers(db: Session = Depends(get_db)):
    shippers = db.query(Shipper).order_by(Shipper.id.asc()).all()
    return shippers


@router.get("/shippers/{shipper_id}", response_model=ShipperResponse)
def get_shipper(shipper_id: int, db: Session = Depends(get_db)):
    shipper = db.query(Shipper).filter(Shipper.id == shipper_id).first()
    if not shipper:
        raise HTTPException(status_code=404, detail="Shipper not found")

    return shipper


@router.post("/deliveries/create", response_model=DeliveryResponse)
def create_delivery_job(payload: DeliveryCreateRequest, db: Session = Depends(get_db)):
    existing_delivery = db.query(DeliveryJob).filter(DeliveryJob.order_id == payload.order_id).first()
    if existing_delivery:
        raise HTTPException(status_code=400, detail="Delivery job for this order already exists")

    if payload.shipping_fee < 0:
        raise HTTPException(status_code=400, detail="Shipping fee cannot be negative")

    delivery = DeliveryJob(
        order_id=payload.order_id,
        user_id=payload.user_id,
        restaurant_id=payload.restaurant_id,
        shipper_id=None,
        delivery_status="waiting_assignment",
        pickup_address=payload.pickup_address,
        dropoff_address=payload.dropoff_address,
        shipping_fee=payload.shipping_fee,
        note=payload.note,
    )

    db.add(delivery)
    db.commit()
    db.refresh(delivery)

    return delivery


@router.get("/deliveries", response_model=List[DeliveryResponse])
def list_deliveries(db: Session = Depends(get_db)):
    deliveries = db.query(DeliveryJob).order_by(DeliveryJob.id.asc()).all()
    return deliveries


@router.get("/deliveries/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(delivery_id: int, db: Session = Depends(get_db)):
    delivery = db.query(DeliveryJob).filter(DeliveryJob.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery job not found")

    return delivery


@router.get("/deliveries/order/{order_id}", response_model=DeliveryResponse)
def get_delivery_by_order(order_id: int, db: Session = Depends(get_db)):
    delivery = db.query(DeliveryJob).filter(DeliveryJob.order_id == order_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery job not found")

    return delivery


@router.get("/shippers/{shipper_id}/deliveries", response_model=List[DeliveryResponse])
def list_deliveries_by_shipper(shipper_id: int, db: Session = Depends(get_db)):
    shipper = db.query(Shipper).filter(Shipper.id == shipper_id).first()
    if not shipper:
        raise HTTPException(status_code=404, detail="Shipper not found")

    deliveries = (
        db.query(DeliveryJob)
        .filter(DeliveryJob.shipper_id == shipper_id)
        .order_by(DeliveryJob.id.asc())
        .all()
    )
    return deliveries


@router.put("/deliveries/{delivery_id}/assign", response_model=DeliveryResponse)
def assign_delivery(delivery_id: int, payload: DeliveryAssignRequest, db: Session = Depends(get_db)):
    delivery = db.query(DeliveryJob).filter(DeliveryJob.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery job not found")

    shipper = db.query(Shipper).filter(Shipper.id == payload.shipper_id).first()
    if not shipper:
        raise HTTPException(status_code=404, detail="Shipper not found")

    if not shipper.is_active:
        raise HTTPException(status_code=400, detail="Shipper is inactive")

    delivery.shipper_id = shipper.id
    delivery.delivery_status = "assigned"

    db.commit()
    db.refresh(delivery)

    return delivery


@router.put("/deliveries/{delivery_id}/status", response_model=DeliveryResponse)
def update_delivery_status(delivery_id: int, payload: DeliveryStatusUpdateRequest, db: Session = Depends(get_db)):
    delivery = db.query(DeliveryJob).filter(DeliveryJob.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery job not found")

    allowed_statuses = [
        "waiting_assignment",
        "assigned",
        "accepted",
        "on_the_way_to_restaurant",
        "picked_up",
        "delivering",
        "delivered",
        "cancelled",
    ]
    if payload.delivery_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid delivery status")

    delivery.delivery_status = payload.delivery_status

    db.commit()
    db.refresh(delivery)

    return delivery


@router.post("/tracking/update", response_model=TrackingResponse)
def update_tracking(payload: TrackingUpdateRequest, db: Session = Depends(get_db)):
    delivery = db.query(DeliveryJob).filter(DeliveryJob.order_id == payload.order_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery job not found")

    if delivery.shipper_id != payload.shipper_id:
        raise HTTPException(status_code=400, detail="Shipper is not assigned to this order")

    redis_client = get_redis_client()

    tracking_key = f"tracking:order:{payload.order_id}"
    tracking_data = {
        "order_id": payload.order_id,
        "shipper_id": payload.shipper_id,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "status": payload.status,
    }

    redis_client.set(tracking_key, json.dumps(tracking_data))

    return TrackingResponse(**tracking_data)


@router.get("/tracking/order/{order_id}", response_model=TrackingResponse)
def get_tracking(order_id: int):
    redis_client = get_redis_client()

    tracking_key = f"tracking:order:{order_id}"
    raw_data = redis_client.get(tracking_key)

    if not raw_data:
        raise HTTPException(status_code=404, detail="Tracking not found")

    tracking_data = json.loads(raw_data)
    return TrackingResponse(**tracking_data)