from fastapi.testclient import TestClient

from app.main import app
from app.services.delivery_helper_service import DeliveryHelperService

client = TestClient(app)


def test_normalize_address_success(monkeypatch):
    def fake_normalize(self, address, country_code="vn"):
        return {
            "success": True,
            "original_address": address,
            "normalized_address": "227 Nguyen Van Cu, Quan 5, Ho Chi Minh City, Vietnam",
            "lat": 10.762622,
            "lon": 106.660172,
            "source": "mock",
        }

    monkeypatch.setattr(DeliveryHelperService, "normalize_address", fake_normalize)

    response = client.post(
        "/delivery-helper/normalize-address",
        json={
            "address": "227 Nguyen Van Cu Q5",
            "country_code": "vn",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["original_address"] == "227 Nguyen Van Cu Q5"
    assert data["source"] == "mock"


def test_estimate_delivery_success():
    response = client.post(
        "/delivery-helper/estimate-delivery",
        json={
            "pickup_lat": 10.762622,
            "pickup_lon": 106.660172,
            "dropoff_lat": 10.7756587,
            "dropoff_lon": 106.7004238,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["distance_km"] > 0
    assert data["estimated_minutes"] > 0
    assert data["suggested_shipping_fee"] >= 15000


def test_normalize_address_validation():
    response = client.post(
        "/delivery-helper/normalize-address",
        json={
            "address": "a",
            "country_code": "vn",
        },
    )

    assert response.status_code == 422