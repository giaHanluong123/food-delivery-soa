from fastapi import APIRouter

from app.core.config import (
    CORE_SERVICE_URL,
    DELIVERY_SERVICE_URL,
    NOTIFICATION_SERVICE_URL,
    PAYMENT_SERVICE_URL,
)
from app.schemas.orchestration import (
    CreateOrderFlowRequest,
    DeliveryDeliveredFlowRequest,
    OrchestrationResponse,
    PaymentCallbackFlowRequest,
)
from app.services.orchestration_service import OrchestrationService

router = APIRouter(prefix="/orchestrations", tags=["Orchestrations"])
service = OrchestrationService()


@router.get("/health")
def orchestration_health():
    return {
        "message": "Integration service is running",
        "core_service_url": CORE_SERVICE_URL,
        "payment_service_url": PAYMENT_SERVICE_URL,
        "delivery_service_url": DELIVERY_SERVICE_URL,
        "notification_service_url": NOTIFICATION_SERVICE_URL,
    }


@router.post("/create-order", response_model=OrchestrationResponse)
def create_order_flow(payload: CreateOrderFlowRequest):
    result = service.create_order_flow(payload.model_dump())
    return {
        "success": True,
        "message": "Create order flow completed successfully",
        "data": result,
    }


@router.post("/payment-callback", response_model=OrchestrationResponse)
def payment_callback_flow(payload: PaymentCallbackFlowRequest):
    result = service.payment_callback_flow(payload.model_dump())
    return {
        "success": True,
        "message": "Payment callback flow completed successfully",
        "data": result,
    }


@router.post("/delivery-delivered", response_model=OrchestrationResponse)
def delivery_delivered_flow(payload: DeliveryDeliveredFlowRequest):
    result = service.delivery_delivered_flow(payload.model_dump())
    return {
        "success": True,
        "message": "Delivery delivered flow completed successfully",
        "data": result,
    }