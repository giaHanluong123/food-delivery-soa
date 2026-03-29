from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine

app = FastAPI(
    title="Payment Service",
    description="Demo payment service",
    version="1.0.0"
)


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