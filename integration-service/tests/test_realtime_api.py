from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_realtime_stats_endpoint():
    response = client.get("/realtime/stats")
    assert response.status_code == 200

    data = response.json()
    assert data["service"] == "integration-service"
    assert "realtime" in data
    assert "tracked_orders" in data["realtime"]
    assert "total_connections" in data["realtime"]


def test_publish_realtime_event():
    payload = {
        "event_type": "order_status_updated",
        "order_id": "101",
        "source_service": "core-service",
        "status": "confirmed",
        "message": "Đơn hàng đã được xác nhận",
        "metadata": {
            "order_status": "confirmed"
        },
    }

    response = client.post("/realtime/publish", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["success"] is True
    assert data["order_id"] == "101"
    assert data["event_type"] == "order_status_updated"
    assert data["status"] == "confirmed"


def test_websocket_connect_and_receive_connected_event():
    with client.websocket_connect("/realtime/ws/orders/101") as websocket:
        first_message = websocket.receive_json()

        assert first_message["event_type"] == "connected"
        assert first_message["order_id"] == "101"
        assert first_message["source_service"] == "integration-service"
        assert first_message["status"] == "CONNECTED"