from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.schemas.review import (
    RestaurantReviewSummaryResponse,
    ReviewCreateRequest,
    ReviewResponse,
)
from app.services.review_service import ReviewService

router = APIRouter(prefix="/reviews", tags=["Reviews"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=ReviewResponse)
def create_review(payload: ReviewCreateRequest, db: Session = Depends(get_db)):
    service = ReviewService(db)
    return service.create_review(
        order_id=payload.order_id,
        user_id=payload.user_id,
        restaurant_id=payload.restaurant_id,
        rating=payload.rating,
        comment=payload.comment,
    )


@router.get("/restaurant/{restaurant_id}", response_model=List[ReviewResponse])
def get_reviews_by_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    service = ReviewService(db)
    return service.get_reviews_by_restaurant(restaurant_id)


@router.get("/restaurant/{restaurant_id}/summary", response_model=RestaurantReviewSummaryResponse)
def get_restaurant_summary(restaurant_id: int, db: Session = Depends(get_db)):
    service = ReviewService(db)
    return service.get_restaurant_summary(restaurant_id)


@router.get("/user/{user_id}", response_model=List[ReviewResponse])
def get_reviews_by_user(user_id: int, db: Session = Depends(get_db)):
    service = ReviewService(db)
    return service.get_reviews_by_user(user_id)