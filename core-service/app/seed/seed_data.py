from sqlalchemy.orm import Session

from app.models import (
    Address,
    MenuItem,
    OrderHeader,
    OrderItem,
    OrderItemTopping,
    Restaurant,
    Review,
    Topping,
    User,
)


def seed_core_data(db: Session):
    existing_user = db.query(User).filter(User.email == "customer1@example.com").first()
    if existing_user:
        return {"message": "Seed data already exists"}

    user = User(
        full_name="Nguyen Van A",
        email="customer1@example.com",
        phone="0900000001",
        password_hash="hashed_password_123",
        role="customer",
        is_active=True,
    )
    db.add(user)
    db.flush()

    address = Address(
        user_id=user.id,
        contact_name="Nguyen Van A",
        phone="0900000001",
        address_line="123 Le Loi",
        ward="Ben Thanh",
        district="District 1",
        city="Ho Chi Minh City",
        latitude=10.7769,
        longitude=106.7009,
        is_default=True,
    )
    db.add(address)
    db.flush()

    restaurant = Restaurant(
        name="Com Ga Sai Gon",
        description="Quan com ga ngon",
        phone="0900000002",
        address_line="456 Nguyen Hue",
        ward="Ben Nghe",
        district="District 1",
        city="Ho Chi Minh City",
        latitude=10.7731,
        longitude=106.7041,
        rating_avg=4.5,
        is_active=True,
    )
    db.add(restaurant)
    db.flush()

    menu_item = MenuItem(
        restaurant_id=restaurant.id,
        name="Com Ga Xoi Mo",
        description="Com ga gion ngon",
        price=45000,
        is_available=True,
        image_url=None,
    )
    db.add(menu_item)
    db.flush()

    topping = Topping(
        menu_item_id=menu_item.id,
        name="Trung Non",
        price=10000,
        is_available=True,
    )
    db.add(topping)
    db.flush()

    order_header = OrderHeader(
        order_code="ORD001",
        user_id=user.id,
        restaurant_id=restaurant.id,
        address_id=address.id,
        order_status="pending",
        payment_status="unpaid",
        delivery_status="waiting_assignment",
        subtotal_amount=45000,
        shipping_fee=15000,
        total_amount=60000,
        note="Giao truoc 12h",
    )
    db.add(order_header)
    db.flush()

    order_item = OrderItem(
        order_id=order_header.id,
        menu_item_id=menu_item.id,
        item_name="Com Ga Xoi Mo",
        unit_price=45000,
        quantity=1,
        line_total=45000,
    )
    db.add(order_item)
    db.flush()

    order_item_topping = OrderItemTopping(
        order_item_id=order_item.id,
        topping_id=topping.id,
        topping_name="Trung Non",
        topping_price=10000,
        quantity=1,
        line_total=10000,
    )
    db.add(order_item_topping)
    db.flush()

    review = Review(
        order_id=order_header.id,
        user_id=user.id,
        restaurant_id=restaurant.id,
        shipper_id=None,
        restaurant_rating=5,
        shipper_rating=None,
        comment="Mon an rat ngon",
    )
    db.add(review)

    db.commit()

    return {
        "message": "Seed data inserted successfully"
    }