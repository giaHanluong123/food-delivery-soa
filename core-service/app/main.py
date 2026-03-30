from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy import inspect, text

from app.core.config import DATABASE_URL, DB_FILE
from app.db.base import Base
from app.db.init_db import init_db
from app.db.session import SessionLocal, engine
from app.routers.address_router import router as address_router
from app.routers.auth_router import router as auth_router
from app.routers.menu_item_router import router as menu_item_router
from app.routers.order_router import router as order_router
from app.routers.restaurant_router import router as restaurant_router
from app.routers.topping_router import router as topping_router
from app.routers.user_router import router as user_router
from app.seed.seed_data import seed_core_data
from app.routers.review_router import router as review_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Core Service",
    description="Core business service for users, restaurants, menus, orders and reviews",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(address_router)
app.include_router(restaurant_router)
app.include_router(menu_item_router)
app.include_router(topping_router)
app.include_router(order_router)
app.include_router(review_router)

@app.get("/")
def root():
    return {
        "message": "Core Service is running",
        "service": "core-service"
    }


@app.get("/health")
def health_check():
    return {
        "service": "core-service",
        "status": "ok"
    }


@app.get("/db-check")
def db_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {
        "service": "core-service",
        "database": "connected"
    }


@app.get("/db-info")
def db_info():
    return {
        "service": "core-service",
        "database_url": DATABASE_URL,
        "database_file": str(DB_FILE),
        "db_file_exists": Path(DB_FILE).exists(),
        "metadata_tables": list(Base.metadata.tables.keys())
    }


@app.post("/init-db")
def initialize_database():
    init_db()
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    return {
        "service": "core-service",
        "message": "Database initialized successfully",
        "tables_after_init": tables
    }


@app.get("/tables")
def list_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return {
        "service": "core-service",
        "tables": tables
    }


@app.post("/seed-data")
def seed_data():
    db = SessionLocal()
    try:
        result = seed_core_data(db)
        return {
            "service": "core-service",
            **result
        }
    finally:
        db.close()