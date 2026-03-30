from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_code = Column(String(50), unique=True, nullable=False, index=True)
    order_id = Column(Integer, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False, default="demo_gateway")
    payment_status = Column(String(50), nullable=False, default="pending")

    gateway_transaction_id = Column(String(100), nullable=True)
    callback_message = Column(Text, nullable=True)
    refund_reason = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)