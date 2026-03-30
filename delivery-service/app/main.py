from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.core.config import DATABASE_URL, DB_FILE
from app.db.base import Base
from app.db.init_db import init_db
from app.db.session import engine
from app.routers.delivery_router import router as delivery_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Delivery Service",
    description="Demo delivery service for food delivery SOA project",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(delivery_router)


@app.get("/")
def root():
    return {
        "message": "Delivery Service is running",
        "service": "delivery-service"
    }


@app.get("/health")
def health_check():
    return {
        "service": "delivery-service",
        "status": "ok"
    }


@app.get("/db-check")
def db_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "service": "delivery-service",
        "database": "connected"
    }


@app.get("/db-info")
def db_info():
    return {
        "service": "delivery-service",
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
        "service": "delivery-service",
        "tables": tables
    }