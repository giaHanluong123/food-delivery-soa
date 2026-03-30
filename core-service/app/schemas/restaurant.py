from typing import Optional

from pydantic import BaseModel


class RestaurantCreate(BaseModel):
    name: str
    description: Optional[str] = None
    phone: str
    address_line: str
    ward: Optional[str] = None
    district: Optional[str] = None
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating_avg: float = 0
    is_active: bool = True


class RestaurantUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    phone: str
    address_line: str
    ward: Optional[str] = None
    district: Optional[str] = None
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating_avg: float = 0
    is_active: bool = True


class RestaurantResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    phone: str
    address_line: str
    ward: Optional[str] = None
    district: Optional[str] = None
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    rating_avg: float
    is_active: bool

    class Config:
        from_attributes = True