from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.orchestration_router import router as orchestration_router

app = FastAPI(
    title="Integration Service",
    description="ESB / Orchestration service for food delivery SOA demo",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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