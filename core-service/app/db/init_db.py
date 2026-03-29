from app.db.base import Base
from app.db.session import engine

# Import models để SQLAlchemy biết tất cả bảng trước khi create_all
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


def init_db():
    Base.metadata.create_all(bind=engine)