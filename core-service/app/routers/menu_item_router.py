from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import MenuItem, Restaurant
from app.schemas.menu_item import MenuItemCreate, MenuItemResponse, MenuItemUpdate

router = APIRouter(tags=["Menu Items"])


@router.post("/menu-items", response_model=MenuItemResponse)
def create_menu_item(payload: MenuItemCreate, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == payload.restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    menu_item = MenuItem(
        restaurant_id=payload.restaurant_id,
        name=payload.name,
        description=payload.description,
        price=payload.price,
        is_available=payload.is_available,
        image_url=payload.image_url,
    )

    db.add(menu_item)
    db.commit()
    db.refresh(menu_item)

    return menu_item


@router.get("/menu-items", response_model=List[MenuItemResponse])
def list_menu_items(
    restaurant_id: Optional[int] = Query(default=None),
    is_available: Optional[bool] = Query(default=None),
    keyword: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(MenuItem)

    if restaurant_id is not None:
        query = query.filter(MenuItem.restaurant_id == restaurant_id)

    if is_available is not None:
        query = query.filter(MenuItem.is_available == is_available)

    if keyword:
        query = query.filter(MenuItem.name.ilike(f"%{keyword}%"))

    menu_items = query.order_by(MenuItem.id.asc()).all()
    return menu_items


@router.get("/menu-items/search", response_model=List[MenuItemResponse])
def search_menu_items(keyword: str, db: Session = Depends(get_db)):
    menu_items = (
        db.query(MenuItem)
        .filter(MenuItem.name.ilike(f"%{keyword}%"))
        .order_by(MenuItem.id.asc())
        .all()
    )
    return menu_items


@router.get("/menu-items/{menu_item_id}", response_model=MenuItemResponse)
def get_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    return menu_item


@router.get("/restaurants/{restaurant_id}/menu-items", response_model=List[MenuItemResponse])
def list_menu_items_by_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    menu_items = (
        db.query(MenuItem)
        .filter(MenuItem.restaurant_id == restaurant_id)
        .order_by(MenuItem.id.asc())
        .all()
    )
    return menu_items


@router.put("/menu-items/{menu_item_id}", response_model=MenuItemResponse)
def update_menu_item(menu_item_id: int, payload: MenuItemUpdate, db: Session = Depends(get_db)):
    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    menu_item.name = payload.name
    menu_item.description = payload.description
    menu_item.price = payload.price
    menu_item.is_available = payload.is_available
    menu_item.image_url = payload.image_url

    db.commit()
    db.refresh(menu_item)

    return menu_item