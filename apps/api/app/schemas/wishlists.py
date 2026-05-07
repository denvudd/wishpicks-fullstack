import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import EventType, ReservationMode, WishlistVisibility


class WishlistCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str | None = None
    visibility: WishlistVisibility = WishlistVisibility.link_only
    event_type: EventType | None = None
    event_date: date | None = None
    reservation_mode: ReservationMode = ReservationMode.anonymous

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "My Birthday Wishlist",
                "description": "Things I'd love for my birthday",
                "visibility": "link_only",
                "event_type": "birthday",
                "event_date": "2026-08-15",
                "reservation_mode": "anonymous",
            }
        }
    )


class WishlistUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    visibility: WishlistVisibility | None = None
    event_type: EventType | None = None
    event_date: date | None = None
    reservation_mode: ReservationMode | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated Title",
                "visibility": "public",
            }
        }
    )


class WishlistResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    visibility: WishlistVisibility
    event_type: EventType | None
    event_date: date | None
    reservation_mode: ReservationMode
    slug: str
    cover_url: str | None
    item_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "My Birthday Wishlist",
                "description": "Things I'd love for my birthday",
                "visibility": "link_only",
                "event_type": "birthday",
                "event_date": "2026-08-15",
                "reservation_mode": "anonymous",
                "slug": "abc12345xyz",
                "cover_url": None,
                "item_count": 5,
                "created_at": "2026-05-07T10:00:00Z",
                "updated_at": "2026-05-07T10:00:00Z",
            }
        },
    )


class WishlistListData(BaseModel):
    items: list[WishlistResponse]
    total: int
    limit: int
    offset: int


class WishlistListResponse(BaseModel):
    data: WishlistListData


class WishlistSingleResponse(BaseModel):
    data: WishlistResponse


class WishlistInviteCreate(BaseModel):
    email: EmailStr

    model_config = ConfigDict(
        json_schema_extra={"example": {"email": "friend@example.com"}}
    )


class WishlistInviteResponse(BaseModel):
    id: uuid.UUID
    wishlist_id: uuid.UUID
    email: str
    invited_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "wishlist_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "friend@example.com",
                "invited_at": "2026-05-07T10:00:00Z",
            }
        },
    )


class WishlistInviteListData(BaseModel):
    items: list[WishlistInviteResponse]


class WishlistInviteListResponse(BaseModel):
    data: WishlistInviteListData
