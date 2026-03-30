from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy import inspect, text

from .core.config import DATABASE_URL, DB_FILE
from .db.base import Base
from .db.init_db import init_db
from .db.session import engine
from .routers.payment_router import router as payment_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Payment Service",
    description="Demo payment service for food delivery SOA project",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(payment_router)


@app.get("/")
def root():
    return {
        "message": "Payment Service is running",
        "service": "payment-service"
    }


@app.get("/health")
def health_check():
    return {
        "service": "payment-service",
        "status": "ok"
    }


@app.get("/db-check")
def db_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return {
        "service": "payment-service",
        "database": "connected"
    }


@app.get("/db-info")
def db_info():
    return {
        "service": "payment-service",
        "database_url": DATABASE_URL,
        "database_file": str(DB_FILE),
        "db_file_exists": Path(DB_FILE).exists(),
        "metadata_tables": list(Base.metadata.tables.keys())
    }


@app.get("/tables")
def list_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return {
        "service": "payment-service",
        "tables": tables
    }