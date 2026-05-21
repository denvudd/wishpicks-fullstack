import uuid
from decimal import Decimal

from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class WishItem(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "wish_items"

    wishlist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wishlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    price_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    price_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="UAH", nullable=False)
    product_url: Mapped[str | None] = mapped_column(String, nullable=True)
    store_domain: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    priority: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    is_surprise: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    images: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    image_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    image_height: Mapped[int | None] = mapped_column(Integer, nullable=True)

    wishlist: Mapped["Wishlist"] = relationship("Wishlist", back_populates="items")
    reservation: Mapped["Reservation | None"] = relationship(
        "Reservation",
        back_populates="item",
        uselist=False,
        cascade="all, delete-orphan",
    )
    saved_by: Mapped[list["SavedItem"]] = relationship("SavedItem", back_populates="item", cascade="all, delete-orphan")
