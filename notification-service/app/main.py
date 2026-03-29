from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine

app = FastAPI(
    title="Notification Service",
    description="Demo notification service",
    version="1.0.0"
)


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