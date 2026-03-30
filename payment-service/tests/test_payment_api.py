from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "payment-service"
    assert data["status"] == "ok"


def test_create_payment_success():
    payload = {
        "order_id": 1001,
        "user_id": 1,
        "amount": 120000,
        "payment_method": "demo_gateway"
    }

    response = client.post("/payments/create", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["order_id"] == 1001
    assert data["user_id"] == 1
    assert data["amount"] == 120000
    assert data["payment_status"] == "pending"
    assert data["transaction_code"].startswith("PAY-")


def test_create_payment_duplicate_order_should_fail():
    payload = {
        "order_id": 1002,
        "user_id": 1,
        "amount": 150000,
        "payment_method": "demo_gateway"
    }

    first_response = client.post("/payments/create", json=payload)
    assert first_response.status_code == 200

    second_response = client.post("/payments/create", json=payload)
    assert second_response.status_code == 400
    assert "pending or paid" in second_response.json()["detail"]


def test_payment_callback_paid_success():
    create_payload = {
        "order_id": 1003,
        "user_id": 2,
        "amount": 99000,
        "payment_method": "demo_gateway"
    }

    create_response = client.post("/payments/create", json=create_payload)
    assert create_response.status_code == 200
    payment_id = create_response.json()["id"]

    callback_payload = {
        "payment_status": "paid",
        "gateway_transaction_id": "GW-PAID-1003",
        "callback_message": "Payment success"
    }

    callback_response = client.post(
        f"/payments/{payment_id}/callback",
        json=callback_payload
    )
    assert callback_response.status_code == 200

    data = callback_response.json()
    assert data["payment_status"] == "paid"
    assert data["gateway_transaction_id"] == "GW-PAID-1003"


def test_refund_paid_payment_success():
    create_payload = {
        "order_id": 1004,
        "user_id": 3,
        "amount": 88000,
        "payment_method": "demo_gateway"
    }

    create_response = client.post("/payments/create", json=create_payload)
    assert create_response.status_code == 200
    payment_id = create_response.json()["id"]

    callback_payload = {
        "payment_status": "paid",
        "gateway_transaction_id": "GW-PAID-1004",
        "callback_message": "Payment success"
    }

    callback_response = client.post(
        f"/payments/{payment_id}/callback",
        json=callback_payload
    )
    assert callback_response.status_code == 200

    refund_payload = {
        "reason": "Customer requested cancellation"
    }

    refund_response = client.post(
        f"/payments/{payment_id}/refund",
        json=refund_payload
    )
    assert refund_response.status_code == 200

    data = refund_response.json()
    assert data["payment_status"] == "refunded"
    assert data["refund_reason"] == "Customer requested cancellation"


def test_refund_pending_payment_should_fail():
    create_payload = {
        "order_id": 1005,
        "user_id": 4,
        "amount": 50000,
        "payment_method": "demo_gateway"
    }

    create_response = client.post("/payments/create", json=create_payload)
    assert create_response.status_code == 200
    payment_id = create_response.json()["id"]

    refund_payload = {
        "reason": "Try refund too early"
    }

    refund_response = client.post(
        f"/payments/{payment_id}/refund",
        json=refund_payload
    )
    assert refund_response.status_code == 400
    assert "Only paid transaction can be refunded" in refund_response.json()["detail"]