from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_review_success_for_delivered_order():
    response = client.post(
        "/reviews",
        json={
            "order_id": 1,
            "user_id": 1,
            "restaurant_id": 1,
            "rating": 5,
            "comment": "Do an ngon, giao nhanh"
        }
    )

    assert response.status_code in [200, 201]
    data = response.json()
    assert data["order_id"] == 1
    assert data["user_id"] == 1
    assert data["restaurant_id"] == 1
    assert data["rating"] == 5


def test_duplicate_review_should_fail():
    first_response = client.post(
        "/reviews",
        json={
            "order_id": 2,
            "user_id": 1,
            "restaurant_id": 1,
            "rating": 4,
            "comment": "Lan review dau"
        }
    )

    # Nếu order_id=2 chưa đúng seed delivered thì bạn đổi sang 1 order delivered khác
    assert first_response.status_code in [200, 201]

    second_response = client.post(
        "/reviews",
        json={
            "order_id": 2,
            "user_id": 1,
            "restaurant_id": 1,
            "rating": 5,
            "comment": "Lan review thu hai"
        }
    )

    assert second_response.status_code == 400
    assert "already been reviewed" in second_response.json()["detail"]


def test_get_reviews_by_restaurant():
    response = client.get("/reviews/restaurant/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_restaurant_summary():
    response = client.get("/reviews/restaurant/1/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["restaurant_id"] == 1
    assert "total_reviews" in data
    assert "average_rating" in data


def test_get_reviews_by_user():
    response = client.get("/reviews/user/1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)