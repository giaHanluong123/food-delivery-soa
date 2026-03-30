from pydantic import BaseModel


class ToppingCreate(BaseModel):
    menu_item_id: int
    name: str
    price: float
    is_available: bool = True


class ToppingResponse(BaseModel):
    id: int
    menu_item_id: int
    name: str
    price: float
    is_available: bool

    class Config:
        from_attributes = True