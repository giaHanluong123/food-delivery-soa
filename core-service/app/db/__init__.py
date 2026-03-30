from app.db.base import Base
from app.db.session import engine

# Import toàn bộ model để SQLAlchemy đăng ký metadata
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
    print("=== INIT DB START ===")
    print("Registered tables in metadata:", list(Base.metadata.tables.keys()))
    Base.metadata.create_all(bind=engine)
    print("=== INIT DB DONE ===")