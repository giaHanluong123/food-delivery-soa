from fastapi.testclient import TestClient

from app.main import app
import app.services.orchestration_service as orchestration_module


class FakeOrchestrationService:
    def create_order_flow(self, payload):
        return {
            "order": {"id": 1001, "order_status": "pending"},
            "payment": {"id": 501, "payment_status": "pending"},
            "delivery": {"id": 301, "delivery_status": "waiting_assignment"},
            "notification": {"id": 1, "is_read": False},
        }

    def payment_callback_flow(self, payload):
        return {
            "payment_callback": {"id": 501, "payment_status": "paid"},
            "order_update": {"id": 1001, "order_status": "confirmed"},
            "notification": {"id": 2, "is_read": False},
        }

    def delivery_delivered_flow(self, payload):
        return {
            "delivery_update": {"id": 301, "delivery_status": "delivered"},
            "order_update": {"id": 1001, "order_status": "delivered"},
            "notification": {"id": 3, "is_read": False},
        }


orchestration_module.OrchestrationService = FakeOrchestrationService

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "integration-service"


def test_create_order_flow():
    payload = {
        "user_id": 1,
        "restaurant_id": 1,
        "delivery_address": "123 Nguyen Trai",
        "payment_method": "demo_gateway",
        "shipping_fee": 15000,
        "note": "Giao nhanh",
        "items": [
            {
                "menu_item_id": 1,
                "quantity": 2,
                "unit_price": 45000,
                "note": "it da",
                "toppings": []
            }
        ]
    }

    response = client.post("/orchestrations/create-order", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["order"]["id"] == 1001


def test_payment_callback_flow():
    payload = {
        "payment_id": 501,
        "payment_status": "paid",
        "gateway_transaction_id": "GW-123",
        "callback_message": "Payment success",
        "order_id": 1001,
        "user_id": 1
    }

    response = client.post("/orchestrations/payment-callback", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["payment_callback"]["payment_status"] == "paid"


def test_delivery_delivered_flow():
    payload = {
        "delivery_id": 301,
        "order_id": 1001,
        "user_id": 1
    }

    response = client.post("/orchestrations/delivery-delivered", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["delivery_update"]["delivery_status"] == "delivered"