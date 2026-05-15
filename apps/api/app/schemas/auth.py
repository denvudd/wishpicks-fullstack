import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class RegisterRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "securepassword",
                "display_name": "Jane Doe",
            }
        }
    )

    email: EmailStr
    password: str
    display_name: str | None = None

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Must be at least 8 characters.")
        return v


class LoginRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "user@example.com", "password": "securepassword"}}
    )

    email: EmailStr
    password: str


class VerifyEmailRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"code": "123456"}})

    code: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    username: str | None
    display_name: str | None
    avatar_url: str | None
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    updated_at: datetime


class AuthResponse(BaseModel):
    data: UserResponse
