import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base, UUIDMixin


class WishlistInvite(Base, UUIDMixin):
    __tablename__ = "wishlist_invites"
    __table_args__ = (UniqueConstraint("wishlist_id", "email", name="uq_wishlist_invites_wishlist_id_email"),)

    wishlist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("wishlists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(String, nullable=False)
    invited_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    wishlist: Mapped["Wishlist"] = relationship("Wishlist", back_populates="invites")
