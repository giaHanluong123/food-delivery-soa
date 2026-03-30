
from fastapi.testclient import TestClient

from app.main import app
import app.routers.delivery_router as delivery_router_module


class FakeRedis:
    def __init__(self):
        self.store = {}

    def setex(self, key, ttl, value):
        self.store[key] = value

    def get(self, key):
        return self.store.get(key)


fake_redis = FakeRedis()


def fake_get_redis_client():
    return fake_redis


delivery_router_module.get_redis_client = fake_get_redis_client

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "delivery-service"
    assert data["status"] == "ok"


def test_create_shipper_success():
    payload = {
        "full_name": "Nguyen Van A",
        "phone": "0900000001",
        "vehicle_type": "motorbike",
        "is_active": True
    }

    response = client.post("/shippers", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Nguyen Van A"
    assert data["phone"] == "0900000001"


def test_create_delivery_success():
    payload = {
        "order_id": 2001,
        "user_id": 1,
        "restaurant_id": 1,
        "pickup_address": "1 Nguyen Trai",
        "dropoff_address": "2 Le Loi",
        "shipping_fee": 18000,
        "note": "Giao gio hanh chinh"
    }

    response = client.post("/deliveries", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 2001
    assert data["delivery_status"] == "waiting_assignment"


def test_assign_delivery_success():
    shipper_payload = {
        "full_name": "Tran Van B",
        "phone": "0900000002",
        "vehicle_type": "motorbike",
        "is_active": True
    }
    shipper_response = client.post("/shippers", json=shipper_payload)
    assert shipper_response.status_code == 200
    shipper_id = shipper_response.json()["id"]

    delivery_payload = {
        "order_id": 2002,
        "user_id": 2,
        "restaurant_id": 2,
        "pickup_address": "Quan 1",
        "dropoff_address": "Quan 3",
        "shipping_fee": 25000,
        "note": "Khong lay dua"
    }
    delivery_response = client.post("/deliveries", json=delivery_payload)
    assert delivery_response.status_code == 200
    delivery_id = delivery_response.json()["id"]

    assign_payload = {"shipper_id": shipper_id}
    assign_response = client.put(f"/deliveries/{delivery_id}/assign", json=assign_payload)

    assert assign_response.status_code == 200
    data = assign_response.json()
    assert data["shipper_id"] == shipper_id
    assert data["delivery_status"] == "assigned"


def test_invalid_status_transition_should_fail():
    shipper_payload = {
        "full_name": "Le Van C",
        "phone": "0900000003",
        "vehicle_type": "motorbike",
        "is_active": True
    }
    shipper_response = client.post("/shippers", json=shipper_payload)
    assert shipper_response.status_code == 200
    shipper_id = shipper_response.json()["id"]

    delivery_payload = {
        "order_id": 2003,
        "user_id": 3,
        "restaurant_id": 3,
        "pickup_address": "A",
        "dropoff_address": "B",
        "shipping_fee": 15000,
        "note": "Demo"
    }
    delivery_response = client.post("/deliveries", json=delivery_payload)
    assert delivery_response.status_code == 200
    delivery_id = delivery_response.json()["id"]

    assign_response = client.put(
        f"/deliveries/{delivery_id}/assign",
        json={"shipper_id": shipper_id}
    )
    assert assign_response.status_code == 200

    invalid_status_response = client.put(
        f"/deliveries/{delivery_id}/status",
        json={"delivery_status": "delivered"}
    )
    assert invalid_status_response.status_code == 400
    assert "Invalid status transition" in invalid_status_response.json()["detail"]


def test_full_status_flow_and_tracking_success():
    shipper_payload = {
        "full_name": "Pham Van D",
        "phone": "0900000004",
        "vehicle_type": "motorbike",
        "is_active": True
    }
    shipper_response = client.post("/shippers", json=shipper_payload)
    assert shipper_response.status_code == 200
    shipper_id = shipper_response.json()["id"]

    delivery_payload = {
        "order_id": 2004,
        "user_id": 4,
        "restaurant_id": 4,
        "pickup_address": "Restaurant ABC",
        "dropoff_address": "Customer XYZ",
        "shipping_fee": 22000,
        "note": "Call before arrive"
    }
    delivery_response = client.post("/deliveries", json=delivery_payload)
    assert delivery_response.status_code == 200
    delivery_id = delivery_response.json()["id"]

    assign_response = client.put(
        f"/deliveries/{delivery_id}/assign",
        json={"shipper_id": shipper_id}
    )
    assert assign_response.status_code == 200

    for status in [
        "accepted",
        "on_the_way_to_restaurant",
        "picked_up",
        "delivering",
    ]:
        response = client.put(
            f"/deliveries/{delivery_id}/status",
            json={"delivery_status": status}
        )
        assert response.status_code == 200
        assert response.json()["delivery_status"] == status

    tracking_response = client.post(
        "/tracking/update",
        json={
            "order_id": 2004,
            "shipper_id": shipper_id,
            "latitude": 10.7769,
            "longitude": 106.7009,
            "status": "delivering"
        }
    )
    assert tracking_response.status_code == 200
    tracking_data = tracking_response.json()
    assert tracking_data["order_id"] == 2004
    assert tracking_data["shipper_id"] == shipper_id

    get_tracking_response = client.get("/tracking/order/2004")
    assert get_tracking_response.status_code == 200
    get_tracking_data = get_tracking_response.json()
    assert get_tracking_data["status"] == "delivering"

    delivered_response = client.put(
        f"/deliveries/{delivery_id}/status",
        json={"delivery_status": "delivered"}
    )
    assert delivered_response.status_code == 200
    assert delivered_response.json()["delivery_status"] == "delivered"