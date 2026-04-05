from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.delivery_helper_router import router as delivery_helper_router
from app.routers.external_api_router import router as external_api_router
from app.routers.orchestration_router import router as orchestration_router
from app.routers.realtime_router import router as realtime_router

app = FastAPI(
    title="Integration Service",
    description="ESB / Orchestration service for food delivery SOA demo",
    version="1.1.0",
)

origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orchestration_router)
app.include_router(external_api_router)
app.include_router(delivery_helper_router)
app.include_router(realtime_router)


@app.get("/")
def root():
    return {
        "message": "Integration Service is running",
        "service": "integration-service",
    }


@app.get("/health")
def health_check():
    return {
        "service": "integration-service",
        "status": "ok",
    }