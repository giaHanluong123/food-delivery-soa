from fastapi.testclient import TestClient

from app.main import app
import app.routers.delivery_router as delivery_router_module

client = TestClient(app)


def test_assign_delivery_should_publish_realtime(monkeypatch):
    published_events = []

    def fake_publish_delivery_status_event(**kwargs):
        published_events.append(kwargs)
        return {"published": True, "payload": kwargs}

    monkeypatch.setattr(
        delivery_router_module,
        "publish_delivery_status_event",
        fake_publish_delivery_status_event,
    )

    shipper_payload = {
        "full_name": "Realtime Shipper A",
        "phone": "0999000001",
        "vehicle_type": "motorbike",
        "is_active": True,
    }
    shipper_response = client.post("/shippers", json=shipper_payload)
    assert shipper_response.status_code == 200
    shipper_id = shipper_response.json()["id"]

    delivery_payload = {
        "order_id": 3101,
        "user_id": 10,
        "restaurant_id": 20,
        "pickup_address": "Restaurant A",
        "dropoff_address": "Customer A",
        "shipping_fee": 15000,
        "note": "Realtime assign test",
    }
    delivery_response = client.post("/deliveries", json=delivery_payload)
    assert delivery_response.status_code == 200
    delivery_id = delivery_response.json()["id"]

    assign_response = client.put(
        f"/deliveries/{delivery_id}/assign",
        json={"shipper_id": shipper_id},
    )

    assert assign_response.status_code == 200
    assert assign_response.json()["delivery_status"] == "assigned"

    assert len(published_events) == 1
    assert published_events[0]["event_type"] == "delivery_assigned"
    assert published_events[0]["order_id"] == 3101
    assert published_events[0]["delivery_status"] == "assigned"
    assert published_events[0]["shipper_id"] == shipper_id


def test_full_delivery_status_flow_should_publish_realtime(monkeypatch):
    published_events = []

    def fake_publish_delivery_status_event(**kwargs):
        published_events.append(kwargs)
        return {"published": True, "payload": kwargs}

    monkeypatch.setattr(
        delivery_router_module,
        "publish_delivery_status_event",
        fake_publish_delivery_status_event,
    )

    shipper_payload = {
        "full_name": "Realtime Shipper B",
        "phone": "0999000002",
        "vehicle_type": "motorbike",
        "is_active": True,
    }
    shipper_response = client.post("/shippers", json=shipper_payload)
    assert shipper_response.status_code == 200
    shipper_id = shipper_response.json()["id"]

    delivery_payload = {
        "order_id": 3102,
        "user_id": 11,
        "restaurant_id": 21,
        "pickup_address": "Restaurant B",
        "dropoff_address": "Customer B",
        "shipping_fee": 18000,
        "note": "Realtime status flow test",
    }
    delivery_response = client.post("/deliveries", json=delivery_payload)
    assert delivery_response.status_code == 200
    delivery_id = delivery_response.json()["id"]

    assign_response = client.put(
        f"/deliveries/{delivery_id}/assign",
        json={"shipper_id": shipper_id},
    )
    assert assign_response.status_code == 200

    for status in [
        "accepted",
        "on_the_way_to_restaurant",
        "picked_up",
        "delivering",
        "delivered",
    ]:
        response = client.put(
            f"/deliveries/{delivery_id}/status",
            json={"delivery_status": status},
        )
        assert response.status_code == 200
        assert response.json()["delivery_status"] == status

    event_types = [event["event_type"] for event in published_events]

    assert event_types == [
        "delivery_assigned",
        "delivery_accepted",
        "delivery_on_the_way_to_restaurant",
        "delivery_picked_up",
        "delivery_delivering",
        "delivery_delivered",
    ]

    assert published_events[-1]["order_id"] == 3102
    assert published_events[-1]["delivery_status"] == "delivered"
    assert published_events[-1]["shipper_id"] == shipper_id