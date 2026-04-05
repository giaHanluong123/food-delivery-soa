import httpx

from app.core.config import (
    INTEGRATION_SERVICE_URL,
    REALTIME_ENABLED,
    REALTIME_HTTP_TIMEOUT,
)


def publish_delivery_status_event(
    *,
    order_id: int,
    delivery_id: int,
    user_id: int,
    restaurant_id: int,
    shipper_id: int | None,
    delivery_status: str,
    event_type: str,
    message: str | None = None,
) -> dict:
    payload = {
        "event_type": event_type,
        "order_id": str(order_id),
        "source_service": "delivery-service",
        "status": delivery_status,
        "message": message,
        "metadata": {
            "delivery_id": delivery_id,
            "user_id": user_id,
            "restaurant_id": restaurant_id,
            "shipper_id": shipper_id,
            "delivery_status": delivery_status,
        },
    }

    if not REALTIME_ENABLED:
        return {
            "published": False,
            "reason": "realtime_disabled",
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
        # Với đồ án demo, không để realtime lỗi làm fail business flow delivery.
        return {
            "published": False,
            "reason": str(exc),
            "payload": payload,
        }