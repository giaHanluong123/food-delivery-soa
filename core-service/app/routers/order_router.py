from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import (
    Address,
    MenuItem,
    OrderHeader,
    OrderItem,
    OrderItemTopping,
    Restaurant,
    Topping,
    User,
)
from app.schemas.order import (
    CreateFullOrderRequest,
    OrderDetailResponse,
    OrderItemResponse,
    OrderItemToppingResponse,
    UpdateOrderStatusRequest,
)

router = APIRouter(tags=["Orders"])


def build_order_detail_response(order: OrderHeader, db: Session) -> OrderDetailResponse:
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).order_by(OrderItem.id.asc()).all()

    item_responses = []
    for item in order_items:
        item_toppings = (
            db.query(OrderItemTopping)
            .filter(OrderItemTopping.order_item_id == item.id)
            .order_by(OrderItemTopping.id.asc())
            .all()
        )

        topping_responses = [
            OrderItemToppingResponse(
                id=t.id,
                topping_id=t.topping_id,
                topping_name=t.topping_name,
                topping_price=float(t.topping_price),
                quantity=t.quantity,
                line_total=float(t.line_total),
            )
            for t in item_toppings
        ]

        item_responses.append(
            OrderItemResponse(
                id=item.id,
                menu_item_id=item.menu_item_id,
                item_name=item.item_name,
                unit_price=float(item.unit_price),
                quantity=item.quantity,
                line_total=float(item.line_total),
                toppings=topping_responses,
            )
        )

    return OrderDetailResponse(
        id=order.id,
        order_code=order.order_code,
        user_id=order.user_id,
        restaurant_id=order.restaurant_id,
        address_id=order.address_id,
        order_status=order.order_status,
        payment_status=order.payment_status,
        delivery_status=order.delivery_status,
        subtotal_amount=float(order.subtotal_amount),
        shipping_fee=float(order.shipping_fee),
        total_amount=float(order.total_amount),
        note=order.note,
        items=item_responses,
    )


@router.post("/orders/create-full", response_model=OrderDetailResponse)
def create_full_order(payload: CreateFullOrderRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    restaurant = db.query(Restaurant).filter(Restaurant.id == payload.restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    address = db.query(Address).filter(Address.id == payload.address_id).first()
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")

    if address.user_id != payload.user_id:
        raise HTTPException(status_code=400, detail="Address does not belong to user")

    if not payload.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    subtotal_amount = 0

    order_code = f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    order = OrderHeader(
        order_code=order_code,
        user_id=payload.user_id,
        restaurant_id=payload.restaurant_id,
        address_id=payload.address_id,
        order_status="pending",
        payment_status="unpaid",
        delivery_status="waiting_assignment",
        subtotal_amount=0,
        shipping_fee=payload.shipping_fee,
        total_amount=0,
        note=payload.note,
    )
    db.add(order)
    db.flush()

    for req_item in payload.items:
        menu_item = db.query(MenuItem).filter(MenuItem.id == req_item.menu_item_id).first()
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {req_item.menu_item_id} not found")

        if menu_item.restaurant_id != payload.restaurant_id:
            raise HTTPException(status_code=400, detail=f"Menu item {req_item.menu_item_id} does not belong to restaurant")

        if not menu_item.is_available:
            raise HTTPException(status_code=400, detail=f"Menu item {req_item.menu_item_id} is not available")

        if req_item.quantity <= 0:
            raise HTTPException(status_code=400, detail="Item quantity must be greater than 0")

        base_line_total = float(menu_item.price) * req_item.quantity

        order_item = OrderItem(
            order_id=order.id,
            menu_item_id=menu_item.id,
            item_name=menu_item.name,
            unit_price=menu_item.price,
            quantity=req_item.quantity,
            line_total=base_line_total,
        )
        db.add(order_item)
        db.flush()

        item_total = base_line_total

        for req_topping in req_item.toppings:
            topping = db.query(Topping).filter(Topping.id == req_topping.topping_id).first()
            if not topping:
                raise HTTPException(status_code=404, detail=f"Topping {req_topping.topping_id} not found")

            if topping.menu_item_id != menu_item.id:
                raise HTTPException(status_code=400, detail=f"Topping {req_topping.topping_id} does not belong to menu item")

            if not topping.is_available:
                raise HTTPException(status_code=400, detail=f"Topping {req_topping.topping_id} is not available")

            if req_topping.quantity <= 0:
                raise HTTPException(status_code=400, detail="Topping quantity must be greater than 0")

            topping_line_total = float(topping.price) * req_topping.quantity

            order_item_topping = OrderItemTopping(
                order_item_id=order_item.id,
                topping_id=topping.id,
                topping_name=topping.name,
                topping_price=topping.price,
                quantity=req_topping.quantity,
                line_total=topping_line_total,
            )
            db.add(order_item_topping)

            item_total += topping_line_total

        order_item.line_total = item_total
        subtotal_amount += item_total

    order.subtotal_amount = subtotal_amount
    order.total_amount = subtotal_amount + payload.shipping_fee

    db.commit()
    db.refresh(order)

    return build_order_detail_response(order, db)


@router.get("/orders", response_model=List[OrderDetailResponse])
def list_orders(db: Session = Depends(get_db)):
    orders = db.query(OrderHeader).order_by(OrderHeader.id.asc()).all()
    return [build_order_detail_response(order, db) for order in orders]


@router.get("/orders/{order_id}", response_model=OrderDetailResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(OrderHeader).filter(OrderHeader.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return build_order_detail_response(order, db)


@router.get("/users/{user_id}/orders", response_model=List[OrderDetailResponse])
def list_orders_by_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    orders = (
        db.query(OrderHeader)
        .filter(OrderHeader.user_id == user_id)
        .order_by(OrderHeader.id.asc())
        .all()
    )
    return [build_order_detail_response(order, db) for order in orders]


@router.put("/orders/{order_id}/status", response_model=OrderDetailResponse)
def update_order_status(order_id: int, payload: UpdateOrderStatusRequest, db: Session = Depends(get_db)):
    order = db.query(OrderHeader).filter(OrderHeader.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.order_status = payload.order_status
    order.payment_status = payload.payment_status
    order.delivery_status = payload.delivery_status

    db.commit()
    db.refresh(order)

    return build_order_detail_response(order, db)