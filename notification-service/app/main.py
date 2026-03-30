from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.core.config import DATABASE_URL, DB_FILE
from app.db.base import Base
from app.db.init_db import init_db
from app.db.session import engine
from app.routers.notification_router import router as notification_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Notification Service",
    description="Demo notification service for food delivery SOA project",
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

app.include_router(notification_router)


@app.get("/")
def root():
    return {
        "message": "Notification Service is running",
        "service": "notification-service"
    }


@app.get("/health")
def health_check():
    return {
        "service": "notification-service",
        "status": "ok"
    }


@app.get("/db-check")
def db_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "service": "notification-service",
        "database": "connected"
    }


@app.get("/db-info")
def db_info():
    return {
        "service": "notification-service",
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
        "service": "notification-service",
        "tables": tables
    }