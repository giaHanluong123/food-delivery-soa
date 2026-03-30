from typing import Optional

from pydantic import BaseModel


class MenuItemCreate(BaseModel):
    restaurant_id: int
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True
    image_url: Optional[str] = None


class MenuItemUpdate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool = True
    image_url: Optional[str] = None


class MenuItemResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: Optional[str] = None
    price: float
    is_available: bool
    image_url: Optional[str] = None

    class Config:
        from_attributes = True