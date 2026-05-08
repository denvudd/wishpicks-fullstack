import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import EventType, ReservationMode, WishlistVisibility


class Wishlist(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "wishlists"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_url: Mapped[str | None] = mapped_column(String, nullable=True)
    event_type: Mapped[EventType | None] = mapped_column(
        Enum(EventType, native_enum=False), nullable=True
    )
    event_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    visibility: Mapped[WishlistVisibility] = mapped_column(
        Enum(WishlistVisibility, native_enum=False),
        nullable=False,
        server_default=WishlistVisibility.link_only.value,
    )
    reservation_mode: Mapped[ReservationMode] = mapped_column(
        Enum(ReservationMode, native_enum=False),
        nullable=False,
        server_default=ReservationMode.anonymous.value,
    )
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    owner: Mapped["User"] = relationship("User", back_populates="wishlists")
    items: Mapped[list["WishItem"]] = relationship(
        "WishItem", back_populates="wishlist", cascade="all, delete-orphan"
    )
    saved_by: Mapped[list["SavedWishlist"]] = relationship(
        "SavedWishlist", back_populates="wishlist", cascade="all, delete-orphan"
    )
    invites: Mapped[list["WishlistInvite"]] = relationship(
        "WishlistInvite", back_populates="wishlist", cascade="all, delete-orphan"
    )
