from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantResponse, RestaurantUpdate

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.post("", response_model=RestaurantResponse)
def create_restaurant(payload: RestaurantCreate, db: Session = Depends(get_db)):
    restaurant = Restaurant(
        name=payload.name,
        description=payload.description,
        phone=payload.phone,
        address_line=payload.address_line,
        ward=payload.ward,
        district=payload.district,
        city=payload.city,
        latitude=payload.latitude,
        longitude=payload.longitude,
        rating_avg=payload.rating_avg,
        is_active=payload.is_active,
    )

    db.add(restaurant)
    db.commit()
    db.refresh(restaurant)

    return restaurant


@router.get("", response_model=List[RestaurantResponse])
def list_restaurants(
    city: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    keyword: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Restaurant)

    if city:
        query = query.filter(Restaurant.city.ilike(f"%{city}%"))

    if is_active is not None:
        query = query.filter(Restaurant.is_active == is_active)

    if keyword:
        query = query.filter(Restaurant.name.ilike(f"%{keyword}%"))

    restaurants = query.order_by(Restaurant.id.asc()).all()
    return restaurants


@router.get("/active/list", response_model=List[RestaurantResponse])
def list_active_restaurants(db: Session = Depends(get_db)):
    restaurants = (
        db.query(Restaurant)
        .filter(Restaurant.is_active == True)
        .order_by(Restaurant.id.asc())
        .all()
    )
    return restaurants


@router.get("/search", response_model=List[RestaurantResponse])
def search_restaurants(keyword: str, db: Session = Depends(get_db)):
    restaurants = (
        db.query(Restaurant)
        .filter(Restaurant.name.ilike(f"%{keyword}%"))
        .order_by(Restaurant.id.asc())
        .all()
    )
    return restaurants


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    return restaurant


@router.put("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(restaurant_id: int, payload: RestaurantUpdate, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    restaurant.name = payload.name
    restaurant.description = payload.description
    restaurant.phone = payload.phone
    restaurant.address_line = payload.address_line
    restaurant.ward = payload.ward
    restaurant.district = payload.district
    restaurant.city = payload.city
    restaurant.latitude = payload.latitude
    restaurant.longitude = payload.longitude
    restaurant.rating_avg = payload.rating_avg
    restaurant.is_active = payload.is_active

    db.commit()
    db.refresh(restaurant)

    return restaurant