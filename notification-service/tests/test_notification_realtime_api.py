from fastapi.testclient import TestClient

from app.main import app
import app.routers.notification_router as notification_router_module

client = TestClient(app)


def test_create_notification_should_publish_realtime(monkeypatch):
    published_events = []

    def fake_publish_notification_event(**kwargs):
        published_events.append(kwargs)
        return {"published": True, "payload": kwargs}

    monkeypatch.setattr(
        notification_router_module,
        "publish_notification_event",
        fake_publish_notification_event,
    )

    payload = {
        "user_id": 1,
        "notification_type": "order_created",
        "title": "Đơn hàng đã được tạo",
        "message": "Đơn hàng #5001 đã được tạo thành công",
        "reference_type": "order",
        "reference_id": 5001,
        "order_id": 5001,
    }

    response = client.post("/notifications", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["user_id"] == 1
    assert body["is_read"] is False

    assert len(published_events) == 1
    assert published_events[0]["event_type"] == "notification_created"
    assert published_events[0]["notification_type"] == "order_created"
    assert published_events[0]["order_id"] == 5001
    assert published_events[0]["is_read"] is False


def test_mark_notification_as_read_should_publish_realtime(monkeypatch):
    published_events = []

    def fake_publish_notification_event(**kwargs):
        published_events.append(kwargs)
        return {"published": True, "payload": kwargs}

    monkeypatch.setattr(
        notification_router_module,
        "publish_notification_event",
        fake_publish_notification_event,
    )

    create_payload = {
        "user_id": 2,
        "notification_type": "order_created",
        "title": "Đơn hàng đã được tạo",
        "message": "Đơn hàng #5002 đã được tạo thành công",
        "reference_type": "order",
        "reference_id": 5002,
        "order_id": 5002,
    }

    create_response = client.post("/notifications", json=create_payload)
    assert create_response.status_code == 200
    notification_id = create_response.json()["id"]

    published_events.clear()

    read_response = client.put(f"/notifications/{notification_id}/read")
    assert read_response.status_code == 200

    body = read_response.json()
    assert body["id"] == notification_id
    assert body["is_read"] is True

    assert len(published_events) == 1
    assert published_events[0]["event_type"] == "notification_read"
    assert published_events[0]["notification_type"] == "order_created"
    assert published_events[0]["order_id"] == 5002
    assert published_events[0]["is_read"] is True