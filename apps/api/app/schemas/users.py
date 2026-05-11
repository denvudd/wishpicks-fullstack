import re

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, TypeAdapter, field_validator

from app.schemas.auth import UserResponse

_USERNAME_RE = re.compile(r"^[a-z0-9_-]{3,30}$")
_url_adapter = TypeAdapter(AnyHttpUrl)


class UserUpdateRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "jane_doe",
                "display_name": "Jane Doe",
                "avatar_url": "https://res.cloudinary.com/wishpicks/image/upload/avatars/sample.jpg",
            }
        }
    )

    username: str | None = Field(
        default=None,
        description="3–30 chars, lowercase letters, digits, _ or -",
    )
    display_name: str | None = Field(default=None)
    avatar_url: str | None = Field(default=None, description="Must be a valid HTTP or HTTPS URL")

    @field_validator("username")
    @classmethod
    def username_format(cls, v: str | None) -> str | None:
        if v is not None and not _USERNAME_RE.match(v):
            raise ValueError(
                "Must be 3–30 characters: lowercase letters, digits, _ or -"
            )
        return v

    @field_validator("avatar_url")
    @classmethod
    def avatar_url_is_http(cls, v: str | None) -> str | None:
        if v is not None:
            _url_adapter.validate_python(v)
        return v


class UserProfileResponse(BaseModel):
    data: UserResponse
