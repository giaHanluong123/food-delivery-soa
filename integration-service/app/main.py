from fastapi import FastAPI
from app.routers.orchestration_router import router as orchestration_router

app = FastAPI(
    title="Integration Service",
    description="ESB / Orchestration service for food delivery SOA demo",
    version="1.0.0"
)

app.include_router(orchestration_router)


@app.get("/")
def root():
    return {
        "message": "Integration Service is running",
        "service": "integration-service"
    }


@app.get("/health")
def health_check():
    return {
        "service": "integration-service",
        "status": "ok"
    }


from fastapi import FastAPI
from app.routers.orchestration_router import router as orchestration_router
from app.routers.external_api_router import router as external_api_router

app = FastAPI(
    title="Integration Service",
    description="ESB / Orchestration service for food delivery SOA demo",
    version="1.0.0"
)

app.include_router(orchestration_router)
app.include_router(external_api_router)


@app.get("/")
def root():
    return {
        "message": "Integration Service is running",
        "service": "integration-service"
    }


@app.get("/health")
def health_check():
    return {
        "service": "integration-service",
        "status": "ok"
    }

from fastapi import FastAPI
from app.routers.orchestration_router import router as orchestration_router
from app.routers.external_api_router import router as external_api_router
from app.routers.delivery_helper_router import router as delivery_helper_router

app = FastAPI(
    title="Integration Service",
    description="ESB / Orchestration service for food delivery SOA demo",
    version="1.0.0"
)

app.include_router(orchestration_router)
app.include_router(external_api_router)
app.include_router(delivery_helper_router)


@app.get("/")
def root():
    return {
        "message": "Integration Service is running",
        "service": "integration-service"
    }


@app.get("/health")
def health_check():
    return {
        "service": "integration-service",
        "status": "ok"
    }