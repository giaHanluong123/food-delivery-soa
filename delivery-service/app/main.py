from fastapi import FastAPI
from sqlalchemy import text

from app.db.session import engine
from app.redis_client.client import redis_client

app = FastAPI(
    title="Delivery Service",
    description="Delivery and shipper tracking service",
    version="1.0.0"
)


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


@app.get("/redis/set")
def set_value():
    redis_client.set("test_key", "hello_redis")
    return {"message": "Value set in Redis"}


@app.get("/redis/get")
def get_value():
    value = redis_client.get("test_key")
    return {"value": value}