import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ReservationCreate(BaseModel):
    reserver_name: str | None = None

    model_config = ConfigDict(json_schema_extra={"example": {"reserver_name": "Олена"}})


class ReservationResponse(BaseModel):
    id: uuid.UUID
    item_id: uuid.UUID
    reserver_name: str | None
    is_fulfilled: bool
    anon_token: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440001",
                "item_id": "770e8400-e29b-41d4-a716-446655440000",
                "reserver_name": "Олена",
                "is_fulfilled": False,
                "anon_token": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "created_at": "2026-05-10T12:00:00Z",
            }
        },
    )


class ReservationSingleResponse(BaseModel):
    data: ReservationResponse


class FulfillRequest(BaseModel):
    is_fulfilled: bool

    model_config = ConfigDict(json_schema_extra={"example": {"is_fulfilled": True}})


class MyReservationResponse(BaseModel):
    item_id: uuid.UUID
    item_title: str
    item_image_url: str | None
    item_images: list[str] | None
    item_product_url: str | None
    item_price_min: Decimal | None
    item_price_max: Decimal | None
    item_currency: str
    wishlist_id: uuid.UUID
    wishlist_title: str
    wishlist_slug: str
    owner_display_name: str
    is_fulfilled: bool
    reserved_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "550e8400-e29b-41d4-a716-446655440000",
                "item_title": "Sony WH-1000XM5",
                "item_image_url": "https://example.com/image.jpg",
                "item_images": [],
                "item_product_url": "https://example.com/product",
                "item_price_min": "12499.00",
                "item_price_max": None,
                "item_currency": "UAH",
                "wishlist_id": "660e8400-e29b-41d4-a716-446655440001",
                "wishlist_title": "Elena's Birthday",
                "wishlist_slug": "elena-birthday",
                "owner_display_name": "Elena",
                "is_fulfilled": False,
                "reserved_at": "2026-05-10T12:00:00Z",
            }
        }
    )


class MyReservationListData(BaseModel):
    items: list[MyReservationResponse]
    total: int
    limit: int
    offset: int


class MyReservationListResponse(BaseModel):
    data: MyReservationListData
