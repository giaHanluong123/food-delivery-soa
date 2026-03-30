from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class OrderHeader(Base):
    __tablename__ = "order_headers"

    id = Column(Integer, primary_key=True, index=True)
    order_code = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False, index=True)
    address_id = Column(Integer, ForeignKey("addresses.id"), nullable=False, index=True)

    order_status = Column(String(50), nullable=False, default="pending")
    payment_status = Column(String(50), nullable=False, default="unpaid")
    delivery_status = Column(String(50), nullable=False, default="waiting_assignment")

    subtotal_amount = Column(Numeric(12, 2), nullable=False, default=0)
    shipping_fee = Column(Numeric(12, 2), nullable=False, default=0)
    total_amount = Column(Numeric(12, 2), nullable=False, default=0)

    note = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)