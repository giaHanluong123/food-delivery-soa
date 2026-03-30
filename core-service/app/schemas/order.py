from typing import List, Optional

from pydantic import BaseModel


class CreateOrderItemToppingRequest(BaseModel):
    topping_id: int
    quantity: int = 1


class CreateOrderItemRequest(BaseModel):
    menu_item_id: int
    quantity: int
    toppings: List[CreateOrderItemToppingRequest] = []


class CreateFullOrderRequest(BaseModel):
    user_id: int
    restaurant_id: int
    address_id: int
    note: Optional[str] = None
    shipping_fee: float = 15000
    items: List[CreateOrderItemRequest]


class OrderItemToppingResponse(BaseModel):
    id: int
    topping_id: int
    topping_name: str
    topping_price: float
    quantity: int
    line_total: float

    class Config:
        from_attributes = True


class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    item_name: str
    unit_price: float
    quantity: int
    line_total: float
    toppings: List[OrderItemToppingResponse] = []

    class Config:
        from_attributes = True


class OrderDetailResponse(BaseModel):
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
    items: List[OrderItemResponse]

    class Config:
        from_attributes = True


class UpdateOrderStatusRequest(BaseModel):
    order_status: str
    payment_status: str
    delivery_status: str