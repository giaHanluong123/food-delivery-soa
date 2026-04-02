from pydantic import BaseModel, Field
from typing import Optional


class NormalizeAddressRequest(BaseModel):
    address: str = Field(..., min_length=3, max_length=255)
    country_code: Optional[str] = Field(default="vn", min_length=2, max_length=2)


class NormalizeAddressResponse(BaseModel):
    success: bool
    original_address: str
    normalized_address: str
    lat: float
    lon: float
    source: str


class EstimateDeliveryRequest(BaseModel):
    pickup_lat: float
    pickup_lon: float
    dropoff_lat: float
    dropoff_lon: float


class EstimateDeliveryResponse(BaseModel):
    success: bool
    distance_km: float
    estimated_minutes: int
    suggested_shipping_fee: float
    calculation_mode: str