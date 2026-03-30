from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import OrderHeader, Restaurant, User
from app.repositories.review_repository import ReviewRepository


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.review_repo = ReviewRepository(db)

    def create_review(
        self,
        order_id: int,
        user_id: int,
        restaurant_id: int,
        rating: int,
        comment: str | None,
    ):
        existing_review = self.review_repo.get_by_order_id(order_id)
        if existing_review:
            raise HTTPException(
                status_code=400,
                detail="This order has already been reviewed"
            )

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        restaurant = self.db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        order = self.db.query(OrderHeader).filter(OrderHeader.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.user_id != user_id:
            raise HTTPException(
                status_code=400,
                detail="User can only review their own order"
            )

        if order.restaurant_id != restaurant_id:
            raise HTTPException(
                status_code=400,
                detail="Restaurant does not match the order"
            )

        if order.order_status != "delivered":
            raise HTTPException(
                status_code=400,
                detail="Only delivered orders can be reviewed"
            )

        return self.review_repo.create_review(
            order_id=order_id,
            user_id=user_id,
            restaurant_id=restaurant_id,
            rating=rating,
            comment=comment,
        )

    def get_reviews_by_restaurant(self, restaurant_id: int):
        restaurant = self.db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        return self.review_repo.get_reviews_by_restaurant(restaurant_id)

    def get_reviews_by_user(self, user_id: int):
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return self.review_repo.get_reviews_by_user(user_id)

    def get_restaurant_summary(self, restaurant_id: int):
        restaurant = self.db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        return self.review_repo.get_restaurant_summary(restaurant_id)