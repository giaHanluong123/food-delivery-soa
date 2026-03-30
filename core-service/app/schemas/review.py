from typing import Optional

from pydantic import BaseModel, Field


class ReviewCreateRequest(BaseModel):
    order_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    restaurant_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=2000)


class ReviewResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    restaurant_id: int
    rating: int
    comment: Optional[str] = None

    class Config:
        from_attributes = True


class RestaurantReviewSummaryResponse(BaseModel):
    restaurant_id: int
    total_reviews: int
    average_rating: float