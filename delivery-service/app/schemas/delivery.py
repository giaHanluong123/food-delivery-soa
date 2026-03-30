from typing import Optional

from pydantic import BaseModel


class ShipperCreate(BaseModel):
    full_name: str
    phone: str
    vehicle_type: str = "motorbike"
    is_active: bool = True


class ShipperResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    vehicle_type: str
    is_active: bool

    class Config:
        from_attributes = True


class DeliveryCreateRequest(BaseModel):
    order_id: int
    user_id: int
    restaurant_id: int
    pickup_address: Optional[str] = None
    dropoff_address: Optional[str] = None
    shipping_fee: float = 0
    note: Optional[str] = None


class DeliveryAssignRequest(BaseModel):
    shipper_id: int


class DeliveryStatusUpdateRequest(BaseModel):
    delivery_status: str


class DeliveryResponse(BaseModel):
    id: int
    order_id: int
    user_id: int
    restaurant_id: int
    shipper_id: Optional[int] = None
    delivery_status: str
    pickup_address: Optional[str] = None
    dropoff_address: Optional[str] = None
    shipping_fee: float
    note: Optional[str] = None

    class Config:
        from_attributes = True


class TrackingUpdateRequest(BaseModel):
    order_id: int
    shipper_id: int
    latitude: float
    longitude: float
    status: str


class TrackingResponse(BaseModel):
    order_id: int
    shipper_id: int
    latitude: float
    longitude: float
    status: str