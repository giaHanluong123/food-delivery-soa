from typing import Optional

from pydantic import BaseModel


class AddressCreate(BaseModel):
    user_id: int
    contact_name: str
    phone: str
    address_line: str
    ward: Optional[str] = None
    district: Optional[str] = None
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool = False


class AddressResponse(BaseModel):
    id: int
    user_id: int
    contact_name: str
    phone: str
    address_line: str
    ward: Optional[str] = None
    district: Optional[str] = None
    city: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_default: bool

    class Config:
        from_attributes = True