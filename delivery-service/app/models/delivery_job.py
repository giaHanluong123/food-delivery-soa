from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class DeliveryJob(Base):
    __tablename__ = "delivery_jobs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False, unique=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    restaurant_id = Column(Integer, nullable=False, index=True)
    shipper_id = Column(Integer, nullable=True, index=True)

    delivery_status = Column(String(50), nullable=False, default="waiting_assignment")
    pickup_address = Column(String(500), nullable=True)
    dropoff_address = Column(String(500), nullable=True)
    shipping_fee = Column(Float, nullable=False, default=0)
    note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)