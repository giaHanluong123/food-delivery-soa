from fastapi.testclient import TestClient
from app.main import app
from app.services.geocoding_service import GeocodingService

client = TestClient(app)


def test_geocode_search_mock_mode(monkeypatch):
    def fake_search(self, query, limit=5, country_code="vn"):
        return {
            "success": True,
            "mode": "mock",
            "query": query,
            "results": [
                {
                    "display_name": "Mock address 1",
                    "lat": 10.123,
                    "lon": 106.123,
                    "source": "mock",
                    "place_id": "mock-1",
                }
            ],
        }

    monkeypatch.setattr(GeocodingService, "search_address", fake_search)

    response = client.post(
        "/external/geocode/search",
        json={
            "query": "227 Nguyen Van Cu Quan 5",
            "limit": 1,
            "country_code": "vn"
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["success"] is True
    assert body["mode"] == "mock"
    assert body["query"] == "227 Nguyen Van Cu Quan 5"
    assert len(body["results"]) == 1
    assert body["results"][0]["source"] == "mock"


def test_geocode_search_validation():
    response = client.post(
        "/external/geocode/search",
        json={
            "query": "ab",
            "limit": 1,
            "country_code": "vn"
        },
    )

    assert response.status_code == 422