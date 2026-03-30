from typing import Optional

from pydantic import BaseModel


class OrderHeaderCreate(BaseModel):
    order_code: str
    user_id: int
    restaurant_id: int
    address_id: int
    order_status: str = "pending"
    payment_status: str = "unpaid"
    delivery_status: str = "waiting_assignment"
    subtotal_amount: float = 0
    shipping_fee: float = 0
    total_amount: float = 0
    note: Optional[str] = None


class OrderHeaderResponse(BaseModel):
    id: int
    order_code: str
    user_id: int
    restaurant_id: int
    address_id: int
    order_status: str
    payment_status: str
    delivery_status: str
    subtotal_amount: float
    shipping_fee: float
    total_amount: float
    note: Optional[str] = None

    class Config:
        from_attributes = True