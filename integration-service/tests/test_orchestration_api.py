from fastapi.testclient import TestClient

from app.main import app
from app.core.config import (
    CORE_SERVICE_URL,
    PAYMENT_SERVICE_URL,
    DELIVERY_SERVICE_URL,
    NOTIFICATION_SERVICE_URL,
)
from app.services.http_client import ServiceHttpClient

client = TestClient(app)


def test_create_order_flow_success(monkeypatch):
    calls = []

    def fake_request(self, method, url, json=None):
        calls.append({"method": method, "url": url, "json": json})

        if url == f"{CORE_SERVICE_URL}/orders/create-full":
            return {
                "id": 101,
                "order_code": "ORD-TEST-101",
                "user_id": 1,
                "restaurant_id": 1,
                "address_id": 1,
                "order_status": "pending",
                "payment_status": "unpaid",
                "delivery_status": "waiting_assignment",
                "subtotal_amount": 100000,
                "shipping_fee": 15000,
                "total_amount": 115000,
                "note": "Test order",
                "items": [],
            }

        if url == f"{PAYMENT_SERVICE_URL}/payments/create":
            return {
                "id": 201,
                "order_id": 101,
                "user_id": 1,
                "amount": 115000,
                "payment_method": "cash",
                "payment_status": "pending",
            }

        if url == f"{DELIVERY_SERVICE_URL}/deliveries/create":
            return {
                "id": 301,
                "order_id": 101,
                "user_id": 1,
                "restaurant_id": 1,
                "shipper_id": None,
                "delivery_status": "waiting_assignment",
                "pickup_address": "Restaurant #1",
                "dropoff_address": "Address ID #1",
                "shipping_fee": 15000,
                "note": "Test order",
            }

        if url == f"{NOTIFICATION_SERVICE_URL}/notifications":
            return {
                "id": 401,
                "user_id": 1,
                "notification_type": "order_created",
                "title": "Đơn hàng đã được tạo",
                "message": "Đơn hàng #101 đã được tạo thành công",
                "reference_type": "order",
                "reference_id": 101,
                "is_read": False,
            }

        raise AssertionError(f"Unexpected call: {method} {url}")

    monkeypatch.setattr(ServiceHttpClient, "request", fake_request)

    payload = {
    "user_id": 1,
    "restaurant_id": 1,
    "address_id": 1,
    "payment_method": "demo_gateway",
    "shipping_fee": 15000,
    "note": "Test order",
    "items": [
        {
            "menu_item_id": 1,
            "quantity": 2,
            "toppings": []
        }
    ]
    }

    response = client.post("/orchestrations/create-order", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    assert calls[0]["method"] == "POST"
    assert calls[0]["url"] == f"{CORE_SERVICE_URL}/orders/create-full"
    assert calls[0]["json"]["address_id"] == 1
    assert "delivery_address" not in calls[0]["json"]
    assert "unit_price" not in calls[0]["json"]["items"][0]

    assert calls[1]["url"] == f"{PAYMENT_SERVICE_URL}/payments/create"
    assert calls[1]["json"]["amount"] == 115000

    assert calls[2]["url"] == f"{DELIVERY_SERVICE_URL}/deliveries"
    assert calls[2]["json"]["dropoff_address"] == "Address ID #1"

    assert calls[3]["url"] == f"{NOTIFICATION_SERVICE_URL}/notifications"


def test_payment_callback_flow_paid_success(monkeypatch):
    calls = []

    def fake_request(self, method, url, json=None):
        calls.append({"method": method, "url": url, "json": json})

        if url == f"{PAYMENT_SERVICE_URL}/payments/201/callback":
            return {
                "id": 201,
                "order_id": 101,
                "payment_status": "paid",
            }

        if url == f"{CORE_SERVICE_URL}/orders/101":
            return {
                "id": 101,
                "order_status": "pending",
                "payment_status": "unpaid",
                "delivery_status": "waiting_assignment",
            }

        if url == f"{CORE_SERVICE_URL}/orders/101/status":
            return {
                "id": 101,
                "order_status": "confirmed",
                "payment_status": "paid",
                "delivery_status": "waiting_assignment",
            }

        if url == f"{NOTIFICATION_SERVICE_URL}/notifications":
            return {
                "id": 402,
                "user_id": 1,
                "notification_type": "payment_paid",
                "title": "Thanh toán thành công",
                "message": "Đơn hàng #101 đã thanh toán thành công",
                "reference_type": "payment",
                "reference_id": 201,
                "is_read": False,
            }

        raise AssertionError(f"Unexpected call: {method} {url}")

    monkeypatch.setattr(ServiceHttpClient, "request", fake_request)

    payload = {
        "payment_id": 201,
        "payment_status": "paid",
        "gateway_transaction_id": "DEMO-TXN-001",
        "callback_message": "Thanh toán thành công",
        "order_id": 101,
        "user_id": 1,
    }

    response = client.post("/orchestrations/payment-callback", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    assert calls[0]["url"] == f"{PAYMENT_SERVICE_URL}/payments/201/callback"
    assert calls[1]["url"] == f"{CORE_SERVICE_URL}/orders/101"
    assert calls[2]["url"] == f"{CORE_SERVICE_URL}/orders/101/status"
    assert calls[2]["json"] == {
        "order_status": "confirmed",
        "payment_status": "paid",
        "delivery_status": "waiting_assignment",
    }
    assert calls[3]["url"] == f"{NOTIFICATION_SERVICE_URL}/notifications"


def test_delivery_delivered_flow_success(monkeypatch):
    calls = []

    def fake_request(self, method, url, json=None):
        calls.append({"method": method, "url": url, "json": json})

        if url == f"{DELIVERY_SERVICE_URL}/deliveries/301/status":
            return {
                "id": 301,
                "order_id": 101,
                "delivery_status": "delivered",
            }

        if url == f"{CORE_SERVICE_URL}/orders/101":
            return {
                "id": 101,
                "order_status": "confirmed",
                "payment_status": "paid",
                "delivery_status": "in_transit",
            }

        if url == f"{CORE_SERVICE_URL}/orders/101/status":
            return {
                "id": 101,
                "order_status": "delivered",
                "payment_status": "paid",
                "delivery_status": "delivered",
            }

        if url == f"{NOTIFICATION_SERVICE_URL}/notifications":
            return {
                "id": 403,
                "user_id": 1,
                "notification_type": "delivery_delivered",
                "title": "Đơn hàng đã giao thành công",
                "message": "Đơn hàng #101 đã được giao thành công",
                "reference_type": "delivery",
                "reference_id": 301,
                "is_read": False,
            }

        raise AssertionError(f"Unexpected call: {method} {url}")

    monkeypatch.setattr(ServiceHttpClient, "request", fake_request)

    payload = {
        "delivery_id": 301,
        "order_id": 101,
        "user_id": 1,
    }

    response = client.post("/orchestrations/delivery-delivered", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    assert calls[0]["url"] == f"{DELIVERY_SERVICE_URL}/deliveries/301/status"
    assert calls[1]["url"] == f"{CORE_SERVICE_URL}/orders/101"
    assert calls[2]["url"] == f"{CORE_SERVICE_URL}/orders/101/status"
    assert calls[2]["json"] == {
        "order_status": "delivered",
        "payment_status": "paid",
        "delivery_status": "delivered",
    }
    assert calls[3]["url"] == f"{NOTIFICATION_SERVICE_URL}/notifications"