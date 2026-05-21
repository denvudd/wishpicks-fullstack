import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ItemPriority, WishlistVisibility


class SavedWishlistResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    visibility: WishlistVisibility
    slug: str
    cover_url: str | None
    item_count: int
    preview_images: list[str]
    owner_display_name: str | None
    saved_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Birthday Wishlist",
                "description": "Things I'd love",
                "visibility": "link_only",
                "slug": "abc12345xyz",
                "cover_url": None,
                "item_count": 3,
                "preview_images": ["https://res.cloudinary.com/example/image1.jpg"],
                "owner_display_name": "Jane Doe",
                "saved_at": "2026-05-15T10:00:00Z",
            }
        }
    )


class SavedWishlistListData(BaseModel):
    items: list[SavedWishlistResponse]
    total: int
    limit: int
    offset: int


class SavedWishlistListResponse(BaseModel):
    data: SavedWishlistListData


class SavedWishlistSingleResponse(BaseModel):
    data: SavedWishlistResponse


class CopyItemRequest(BaseModel):
    wishlist_id: uuid.UUID = Field(..., description="Target wishlist (must be owned by the current user)")
    priority: ItemPriority = Field(ItemPriority.normal, description="0=normal, 1=high, 2=must-have")
    notes: str | None = Field(None, description="Personal note about this wish")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "wishlist_id": "550e8400-e29b-41d4-a716-446655440000",
                "priority": 1,
                "notes": "Any colour is fine",
            }
        }
    )


class SavedItemResponse(BaseModel):
    item_id: uuid.UUID
    wishlist_id: uuid.UUID
    title: str
    image_url: str | None
    images: list[str] | None
    product_url: str | None
    price_min: Decimal | None
    price_max: Decimal | None
    currency: str
    saved_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "item_id": "770e8400-e29b-41d4-a716-446655440000",
                "wishlist_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Sony WH-1000XM5",
                "image_url": "https://res.cloudinary.com/example/image.jpg",
                "images": None,
                "product_url": "https://example.com/product",
                "price_min": "5000.00",
                "price_max": "7000.00",
                "currency": "UAH",
                "saved_at": "2026-05-15T10:00:00Z",
            }
        }
    )


class SavedItemListData(BaseModel):
    items: list[SavedItemResponse]
    total: int
    limit: int
    offset: int


class SavedItemListResponse(BaseModel):
    data: SavedItemListData
