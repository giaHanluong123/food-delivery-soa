import httpx

from app.core.config import (
    INTEGRATION_SERVICE_URL,
    REALTIME_ENABLED,
    REALTIME_HTTP_TIMEOUT,
)


def resolve_order_id_for_notification(
    *,
    explicit_order_id: int | None,
    reference_type: str | None,
    reference_id: int | None,
) -> int | None:
    if explicit_order_id:
        return explicit_order_id

    if reference_type == "order" and reference_id:
        return reference_id

    return None


def publish_notification_event(
    *,
    event_type: str,
    notification_id: int,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    is_read: bool,
    reference_type: str | None = None,
    reference_id: int | None = None,
    order_id: int | None = None,
) -> dict:
    resolved_order_id = resolve_order_id_for_notification(
        explicit_order_id=order_id,
        reference_type=reference_type,
        reference_id=reference_id,
    )

    payload = {
        "event_type": event_type,
        "order_id": str(resolved_order_id) if resolved_order_id is not None else "",
        "source_service": "notification-service",
        "status": "read" if is_read else "unread",
        "message": message,
        "metadata": {
            "notification_id": notification_id,
            "user_id": user_id,
            "notification_type": notification_type,
            "title": title,
            "reference_type": reference_type,
            "reference_id": reference_id,
            "is_read": is_read,
            "resolved_order_id": resolved_order_id,
        },
    }

    if not REALTIME_ENABLED:
        return {
            "published": False,
            "reason": "realtime_disabled",
            "payload": payload,
        }

    if resolved_order_id is None:
        return {
            "published": False,
            "reason": "order_id_not_resolved",
            "payload": payload,
        }

    try:
        with httpx.Client(timeout=REALTIME_HTTP_TIMEOUT) as client:
            response = client.post(
                f"{INTEGRATION_SERVICE_URL}/realtime/publish",
                json=payload,
            )
            response.raise_for_status()

        return {
            "published": True,
            "payload": payload,
        }
    except Exception as exc:
        # Không để lỗi realtime làm fail business flow notification
        return {
            "published": False,
            "reason": str(exc),
            "payload": payload,
        }