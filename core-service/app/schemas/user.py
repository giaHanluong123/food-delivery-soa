from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password_hash: str
    role: str = "customer"
    is_active: bool = True


class UserUpdateProfile(BaseModel):
    full_name: str
    phone: str
    is_active: bool = True


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True