from fastapi import FastAPI
from sqlalchemy import inspect, text

from app.db.init_db import init_db
from app.db.session import engine

app = FastAPI(
    title="Core Service",
    description="Core business service for users, restaurants, menus, orders and reviews",
    version="1.0.0"
)


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


@app.post("/init-db")
def initialize_database():
    init_db()
    return {
        "service": "core-service",
        "message": "Database initialized successfully"
    }


@app.get("/tables")
def list_tables():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return {
        "service": "core-service",
        "tables": tables
    }