from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(min_length=5, max_length=255)
    full_name: str = Field(min_length=2, max_length=150)
    password: str = Field(min_length=8, max_length=128)
    organization_name: str = Field(min_length=2, max_length=150)


class LoginRequest(BaseModel):
    email: EmailStr = Field(min_length=5, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: EmailStr
    full_name: str
    organization_id: int
    organization_name: str
    role: str
