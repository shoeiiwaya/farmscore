from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")
    password: str = Field(..., min_length=8, max_length=128)
    name: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    plan: str
    api_calls_month: int

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: str
    password: str


class ApiKeyResponse(BaseModel):
    key: str
    prefix: str
    name: str
    message: str = "APIキーは一度だけ表示されます。安全に保管してください。"
