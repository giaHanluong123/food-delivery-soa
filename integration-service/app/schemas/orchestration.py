from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OrderItemToppingInput(BaseModel):
    topping_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)


class OrderItemInput(BaseModel):
    menu_item_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    note: Optional[str] = None
    toppings: List[OrderItemToppingInput] = []


class CreateOrderFlowRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    restaurant_id: int = Field(..., gt=0)
    address_id: int = Field(..., gt=0)
    delivery_address: Optional[str] = Field(default=None, min_length=3, max_length=500)
    payment_method: str = Field(default="demo_gateway", min_length=2, max_length=50)
    shipping_fee: float = Field(default=0, ge=0)
    note: Optional[str] = None
    items: List[OrderItemInput]


class PaymentCallbackFlowRequest(BaseModel):
    payment_id: int = Field(..., gt=0)
    payment_status: str = Field(..., min_length=2, max_length=30)
    gateway_transaction_id: Optional[str] = None
    callback_message: Optional[str] = None
    order_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)


class DeliveryDeliveredFlowRequest(BaseModel):
    delivery_id: int = Field(..., gt=0)
    order_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)


class OrchestrationResponse(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any]