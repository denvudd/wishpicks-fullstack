import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

from app.models.enums import ItemPriority

_url_adapter = TypeAdapter(AnyHttpUrl)


class WishItemCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    image_url: str | None = None
    product_url: str | None = None
    price_min: Decimal | None = None
    price_max: Decimal | None = None
    currency: str = "UAH"
    priority: ItemPriority = ItemPriority.normal
    is_surprise: bool = False
    notes: str | None = None
    tags: list[str] | None = None
    images: list[str] | None = None

    @model_validator(mode="after")
    def validate_price_range(self) -> "WishItemCreate":
        if self.price_min is not None and self.price_max is not None:
            if self.price_max < self.price_min:
                raise ValueError("price_max must be >= price_min")
        return self

    @field_validator("image_url", mode="before")
    @classmethod
    def image_url_is_http(cls, v: str | None) -> str | None:
        if v is None:
            return v
        _url_adapter.validate_python(v)
        return str(v)

    @field_validator("images", mode="before")
    @classmethod
    def images_are_http(cls, v: list | None) -> list[str] | None:
        if v is None:
            return v
        for url in v:
            _url_adapter.validate_python(url)
        return [str(u) for u in v]

    @field_validator("images", mode="after")
    @classmethod
    def images_max_five(cls, v: list[str] | None) -> list[str] | None:
        if v and len(v) > 5:
            raise ValueError("images: max 5 allowed")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Sony WH-1000XM5",
                "description": "Noise-cancelling headphones",
                "product_url": "https://example.com/product",
                "price_min": "5000.00",
                "price_max": "7000.00",
                "currency": "UAH",
                "priority": 1,
                "is_surprise": False,
                "notes": "Any colour is fine",
                "tags": ["electronics", "audio"],
            }
        }
    )


class WishItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    image_url: str | None = None
    product_url: str | None = None
    price_min: Decimal | None = None
    price_max: Decimal | None = None
    currency: str | None = None
    priority: ItemPriority | None = None
    is_surprise: bool | None = None
    notes: str | None = None
    tags: list[str] | None = None
    images: list[str] | None = None

    @model_validator(mode="after")
    def validate_price_range(self) -> "WishItemUpdate":
        if self.price_min is not None and self.price_max is not None:
            if self.price_max < self.price_min:
                raise ValueError("price_max must be >= price_min")
        return self

    @field_validator("image_url", mode="before")
    @classmethod
    def image_url_is_http(cls, v: str | None) -> str | None:
        if v is None:
            return v
        _url_adapter.validate_python(v)
        return str(v)

    @field_validator("images", mode="before")
    @classmethod
    def images_are_http(cls, v: list | None) -> list[str] | None:
        if v is None:
            return v
        for url in v:
            _url_adapter.validate_python(url)
        return [str(u) for u in v]

    @field_validator("images", mode="after")
    @classmethod
    def images_max_five(cls, v: list[str] | None) -> list[str] | None:
        if v and len(v) > 5:
            raise ValueError("images: max 5 allowed")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated title",
                "price_min": "6000.00",
                "tags": ["electronics"],
            }
        }
    )


class WishItemPositionUpdate(BaseModel):
    position: int = Field(..., ge=0)

    model_config = ConfigDict(json_schema_extra={"example": {"position": 2}})


class WishItemResponse(BaseModel):
    id: uuid.UUID
    wishlist_id: uuid.UUID
    title: str
    description: str | None
    image_url: str | None
    product_url: str | None
    price_min: Decimal | None
    price_max: Decimal | None
    currency: str
    priority: ItemPriority
    is_surprise: bool
    position: int
    notes: str | None
    tags: list[str] | None
    images: list[str] | None
    is_reserved: bool
    is_fulfilled: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "wishlist_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Sony WH-1000XM5",
                "description": "Noise-cancelling headphones",
                "image_url": None,
                "product_url": "https://example.com/product",
                "price_min": "5000.00",
                "price_max": "7000.00",
                "currency": "UAH",
                "priority": 1,
                "is_surprise": False,
                "position": 0,
                "notes": "Any colour is fine",
                "tags": ["electronics", "audio"],
                "is_reserved": False,
                "is_fulfilled": False,
                "created_at": "2026-05-08T10:00:00Z",
                "updated_at": "2026-05-08T10:00:00Z",
            }
        },
    )


class WishItemListData(BaseModel):
    items: list[WishItemResponse]
    total: int
    limit: int
    offset: int
    available_stores: list[str]


class WishItemListResponse(BaseModel):
    data: WishItemListData


class WishItemSingleResponse(BaseModel):
    data: WishItemResponse


class ParseUrlRequest(BaseModel):
    url: str = Field(..., min_length=1)

    model_config = ConfigDict(
        json_schema_extra={"example": {"url": "https://rozetka.com.ua/sony_wh1000xm5/p289749744/"}}
    )


class ParseUrlData(BaseModel):
    title: str | None
    description: str | None
    image_url: str | None
    price: Decimal | None
    currency: str | None
    product_url: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Sony WH-1000XM5",
                "description": "Noise-cancelling headphones",
                "image_url": "https://res.cloudinary.com/wishpicks/items/abc123.jpg",
                "price": "5500.00",
                "currency": "UAH",
                "product_url": "https://rozetka.com.ua/sony_wh1000xm5/p289749744/",
            }
        }
    )


class ParseUrlResponse(BaseModel):
    data: ParseUrlData
