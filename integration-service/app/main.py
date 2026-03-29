from fastapi import FastAPI

app = FastAPI(
    title="Integration Service",
    description="ESB / Orchestration service for food delivery SOA demo",
    version="1.0.0"
)


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