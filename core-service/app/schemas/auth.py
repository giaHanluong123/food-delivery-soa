from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    role: str = "customer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    role: str
    is_active: bool
    message: str