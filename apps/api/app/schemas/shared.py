import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.enums import EventType, ItemPriority, ReservationMode


class SharedAuthor(BaseModel):
    display_name: str | None
    avatar_url: str | None


class SharedWishlistSchema(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    cover_url: str | None
    event_type: EventType | None
    event_date: date | None
    reservation_mode: ReservationMode
    slug: str
    created_at: datetime
    author: SharedAuthor


class MyReservation(BaseModel):
    anon_token: str | None


class SharedItemResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    image_url: str | None
    product_url: str | None
    price_min: Decimal | None
    price_max: Decimal | None
    currency: str
    priority: ItemPriority
    position: int
    notes: str | None
    tags: list[str] | None
    is_reserved: bool
    is_fulfilled: bool
    my_reservation: MyReservation | None

    model_config = ConfigDict(from_attributes=True)


class SharedWishlistData(BaseModel):
    wishlist: SharedWishlistSchema
    items: list[SharedItemResponse]


class SharedWishlistResponse(BaseModel):
    data: SharedWishlistData
