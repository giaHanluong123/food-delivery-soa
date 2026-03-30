from typing import Literal, Optional

from pydantic import BaseModel, Field


class CreateNotificationRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    notification_type: Literal[
        "order_created",
        "payment_paid",
        "payment_failed",
        "delivery_assigned",
        "delivery_delivered",
        "review_created",
        "system"
    ]
    title: str = Field(..., min_length=2, max_length=255)
    message: str = Field(..., min_length=2, max_length=2000)
    reference_type: Optional[str] = Field(default=None, max_length=50)
    reference_id: Optional[int] = Field(default=None, gt=0)


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    notification_type: str
    title: str
    message: str
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    is_read: bool

    class Config:
        from_attributes = True


class MarkAsReadResponse(BaseModel):
    id: int
    is_read: bool
    message: str