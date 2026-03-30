from typing import Optional

from pydantic import BaseModel


class CreatePaymentRequest(BaseModel):
    order_id: int
    user_id: int
    amount: float
    payment_method: str = "demo_gateway"


class PaymentCallbackRequest(BaseModel):
    payment_status: str
    gateway_transaction_id: Optional[str] = None
    callback_message: Optional[str] = None


class RefundPaymentRequest(BaseModel):
    reason: str


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