from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "notification-service"
    assert data["status"] == "ok"


def test_create_notification_success():
    payload = {
        "user_id": 1,
        "notification_type": "order_created",
        "title": "Don hang da duoc tao",
        "message": "Don hang #1001 cua ban da duoc tao thanh cong",
        "reference_type": "order",
        "reference_id": 1001
    }

    response = client.post("/notifications", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["notification_type"] == "order_created"
    assert data["is_read"] is False


def test_list_notifications():
    response = client.get("/notifications")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_notifications_by_user():
    response = client.get("/notifications/user/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_mark_notification_as_read():
    create_payload = {
        "user_id": 2,
        "notification_type": "payment_paid",
        "title": "Thanh toan thanh cong",
        "message": "Don hang #1002 da duoc thanh toan",
        "reference_type": "payment",
        "reference_id": 2002
    }

    create_response = client.post("/notifications", json=create_payload)
    assert create_response.status_code == 200
    notification_id = create_response.json()["id"]

    read_response = client.put(f"/notifications/{notification_id}/read")
    assert read_response.status_code == 200
    data = read_response.json()
    assert data["id"] == notification_id
    assert data["is_read"] is True