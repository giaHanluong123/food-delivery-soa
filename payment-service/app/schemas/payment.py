from typing import Literal, Optional
from pydantic import BaseModel, Field


class CreatePaymentRequest(BaseModel):
    order_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    amount: float = Field(..., gt=0)
    payment_method: str = Field(default="demo_gateway", min_length=2, max_length=50)


class PaymentCallbackRequest(BaseModel):
    payment_status: Literal["paid", "failed"]
    gateway_transaction_id: Optional[str] = Field(default=None, max_length=100)
    callback_message: Optional[str] = Field(default=None, max_length=1000)


class RefundPaymentRequest(BaseModel):
    reason: str = Field(..., min_length=3, max_length=1000)


class PaymentResponse(BaseModel):
    id: int
    transaction_code: str
    order_id: int
    user_id: int
    amount: float
    payment_method: str
    payment_status: str
    gateway_transaction_id: Optional[str] = None
    callback_message: Optional[str] = None
    refund_reason: Optional[str] = None

    class Config:
        from_attributes = True