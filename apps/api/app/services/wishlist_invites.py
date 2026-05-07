import uuid

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import WishlistVisibility
from app.models.wishlist import Wishlist
from app.models.wishlist_invite import WishlistInvite
from app.services.email import send_wishlist_invite_email


async def list_invites(db: AsyncSession, wishlist: Wishlist) -> list[WishlistInvite]:
    result = await db.execute(
        select(WishlistInvite)
        .where(WishlistInvite.wishlist_id == wishlist.id)
        .order_by(WishlistInvite.invited_at.desc())
    )
    return list(result.scalars().all())


async def create_invite(
    db: AsyncSession, wishlist: Wishlist, email: str
) -> WishlistInvite:
    if wishlist.visibility != WishlistVisibility.private:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "INVITE_NOT_APPLICABLE", "message": "Invites are only applicable to private wishlists."}},
        )

    existing = await db.execute(
        select(WishlistInvite).where(
            WishlistInvite.wishlist_id == wishlist.id,
            WishlistInvite.email == email,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "INVITE_ALREADY_SENT", "message": "This email has already been invited."}},
        )

    invite = WishlistInvite(wishlist_id=wishlist.id, email=email)
    db.add(invite)
    await db.commit()
    await db.refresh(invite)

    try:
        await send_wishlist_invite_email(email=email, wishlist_title=wishlist.title)
    except Exception:
        pass  # email failure must not break the response

    return invite


async def delete_invite(
    db: AsyncSession, wishlist: Wishlist, invite_id: uuid.UUID
) -> None:
    result = await db.execute(
        select(WishlistInvite).where(
            WishlistInvite.id == invite_id,
            WishlistInvite.wishlist_id == wishlist.id,
        )
    )
    invite = result.scalar_one_or_none()
    if invite is None:
        return  # idempotent — not an error
    await db.delete(invite)
    await db.commit()
