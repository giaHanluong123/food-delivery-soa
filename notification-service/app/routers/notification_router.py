from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.notification import (
    CreateNotificationRequest,
    MarkAsReadResponse,
    NotificationResponse,
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=NotificationResponse)
def create_notification(payload: CreateNotificationRequest, db: Session = Depends(get_db)):
    service = NotificationService(db)
    return service.create_notification(
        user_id=payload.user_id,
        notification_type=payload.notification_type,
        title=payload.title,
        message=payload.message,
        reference_type=payload.reference_type,
        reference_id=payload.reference_id,
    )


@router.get("", response_model=List[NotificationResponse])
def list_notifications(db: Session = Depends(get_db)):
    service = NotificationService(db)
    return service.list_notifications()


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    service = NotificationService(db)
    return service.get_notification(notification_id)


@router.get("/user/{user_id}", response_model=List[NotificationResponse])
def get_notifications_by_user(
    user_id: int,
    is_read: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
):
    service = NotificationService(db)
    return service.get_notifications_by_user(user_id=user_id, is_read=is_read)


@router.put("/{notification_id}/read", response_model=MarkAsReadResponse)
def mark_notification_as_read(notification_id: int, db: Session = Depends(get_db)):
    service = NotificationService(db)
    notification = service.mark_as_read(notification_id)
    return {
        "id": notification.id,
        "is_read": notification.is_read,
        "message": "Notification marked as read"
    }