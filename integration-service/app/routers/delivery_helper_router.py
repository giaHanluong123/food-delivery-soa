from fastapi import APIRouter

from app.schemas.delivery_helper import (
    NormalizeAddressRequest,
    NormalizeAddressResponse,
    EstimateDeliveryRequest,
    EstimateDeliveryResponse,
)
from app.services.delivery_helper_service import DeliveryHelperService

router = APIRouter(prefix="/delivery-helper", tags=["Delivery Helper"])

delivery_helper_service = DeliveryHelperService()


@router.post("/normalize-address", response_model=NormalizeAddressResponse)
def normalize_address(payload: NormalizeAddressRequest):
    return delivery_helper_service.normalize_address(
        address=payload.address,
        country_code=payload.country_code or "vn",
    )


@router.post("/estimate-delivery", response_model=EstimateDeliveryResponse)
def estimate_delivery(payload: EstimateDeliveryRequest):
    return delivery_helper_service.estimate_delivery(
        pickup_lat=payload.pickup_lat,
        pickup_lon=payload.pickup_lon,
        dropoff_lat=payload.dropoff_lat,
        dropoff_lon=payload.dropoff_lon,
    )