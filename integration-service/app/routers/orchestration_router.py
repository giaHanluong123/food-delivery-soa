from fastapi import APIRouter

from app.schemas.orchestration import (
    CreateOrderFlowRequest,
    DeliveryDeliveredFlowRequest,
    OrchestrationResponse,
    PaymentCallbackFlowRequest,
)
from app.services.orchestration_service import OrchestrationService

router = APIRouter(prefix="/orchestrations", tags=["Orchestrations"])


@router.post("/create-order", response_model=OrchestrationResponse)
def create_order_flow(payload: CreateOrderFlowRequest):
    service = OrchestrationService()
    result = service.create_order_flow(payload.model_dump())

    return {
        "success": True,
        "message": "Create order flow completed successfully",
        "data": result,
    }


@router.post("/payment-callback", response_model=OrchestrationResponse)
def payment_callback_flow(payload: PaymentCallbackFlowRequest):
    service = OrchestrationService()
    result = service.payment_callback_flow(payload.model_dump())

    return {
        "success": True,
        "message": "Payment callback flow completed successfully",
        "data": result,
    }


@router.post("/delivery-delivered", response_model=OrchestrationResponse)
def delivery_delivered_flow(payload: DeliveryDeliveredFlowRequest):
    service = OrchestrationService()
    result = service.delivery_delivered_flow(payload.model_dump())

    return {
        "success": True,
        "message": "Delivery delivered flow completed successfully",
        "data": result,
    }