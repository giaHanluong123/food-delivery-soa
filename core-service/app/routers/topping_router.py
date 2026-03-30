from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import MenuItem, Topping
from app.schemas.topping import ToppingCreate, ToppingResponse

router = APIRouter(tags=["Toppings"])


@router.post("/toppings", response_model=ToppingResponse)
def create_topping(payload: ToppingCreate, db: Session = Depends(get_db)):
    menu_item = db.query(MenuItem).filter(MenuItem.id == payload.menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    topping = Topping(
        menu_item_id=payload.menu_item_id,
        name=payload.name,
        price=payload.price,
        is_available=payload.is_available,
    )

    db.add(topping)
    db.commit()
    db.refresh(topping)

    return topping


@router.get("/toppings", response_model=List[ToppingResponse])
def list_toppings(db: Session = Depends(get_db)):
    toppings = db.query(Topping).order_by(Topping.id.asc()).all()
    return toppings


@router.get("/toppings/{topping_id}", response_model=ToppingResponse)
def get_topping(topping_id: int, db: Session = Depends(get_db)):
    topping = db.query(Topping).filter(Topping.id == topping_id).first()
    if not topping:
        raise HTTPException(status_code=404, detail="Topping not found")

    return topping


@router.get("/menu-items/{menu_item_id}/toppings", response_model=List[ToppingResponse])
def list_toppings_by_menu_item(menu_item_id: int, db: Session = Depends(get_db)):
    menu_item = db.query(MenuItem).filter(MenuItem.id == menu_item_id).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    toppings = (
        db.query(Topping)
        .filter(Topping.menu_item_id == menu_item_id)
        .order_by(Topping.id.asc())
        .all()
    )
    return toppings