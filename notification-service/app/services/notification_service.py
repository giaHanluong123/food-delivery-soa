from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Notification


class NotificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        reference_type: str | None = None,
        reference_id: int | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            reference_type=reference_type,
            reference_id=reference_id,
            is_read=False,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def list_notifications(self):
        return (
            self.db.query(Notification)
            .order_by(Notification.id.desc())
            .all()
        )

    def get_notification(self, notification_id: int):
        notification = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return notification

    def get_notifications_by_user(self, user_id: int, is_read: bool | None = None):
        query = self.db.query(Notification).filter(Notification.user_id == user_id)

        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)

        return query.order_by(Notification.id.desc()).all()

    def mark_as_read(self, notification_id: int):
        notification = (
            self.db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        notification.is_read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification