from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.sql import func

from app.db.base import Base


class OrderItemTopping(Base):
    __tablename__ = "order_item_toppings"

    id = Column(Integer, primary_key=True, index=True)
    order_item_id = Column(Integer, ForeignKey("order_items.id"), nullable=False, index=True)
    topping_id = Column(Integer, ForeignKey("toppings.id"), nullable=False, index=True)
    topping_name = Column(String(255), nullable=False)
    topping_price = Column(Numeric(12, 2), nullable=False, default=0)
    quantity = Column(Integer, nullable=False, default=1)
    line_total = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)