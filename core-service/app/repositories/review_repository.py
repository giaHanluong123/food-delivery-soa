from typing import List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.review import Review


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_order_id(self, order_id: int) -> Optional[Review]:
        return self.db.query(Review).filter(Review.order_id == order_id).first()

    def create_review(
        self,
        order_id: int,
        user_id: int,
        restaurant_id: int,
        rating: int,
        comment: Optional[str],
    ) -> Review:
        review = Review(
            order_id=order_id,
            user_id=user_id,
            restaurant_id=restaurant_id,
            rating=rating,
            comment=comment,
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_reviews_by_restaurant(self, restaurant_id: int) -> List[Review]:
        return (
            self.db.query(Review)
            .filter(Review.restaurant_id == restaurant_id)
            .order_by(Review.id.desc())
            .all()
        )

    def get_reviews_by_user(self, user_id: int) -> List[Review]:
        return (
            self.db.query(Review)
            .filter(Review.user_id == user_id)
            .order_by(Review.id.desc())
            .all()
        )

    def get_restaurant_summary(self, restaurant_id: int):
        total_reviews, average_rating = (
            self.db.query(
                func.count(Review.id),
                func.avg(Review.rating),
            )
            .filter(Review.restaurant_id == restaurant_id)
            .first()
        )

        return {
            "restaurant_id": restaurant_id,
            "total_reviews": total_reviews or 0,
            "average_rating": round(float(average_rating or 0), 2),
        }