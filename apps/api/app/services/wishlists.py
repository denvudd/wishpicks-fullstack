import secrets
import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.wish_item import WishItem
from app.models.wishlist import Wishlist
from app.schemas.wishlists import WishlistCreate, WishlistUpdate

MAX_WISHLISTS_PER_USER = 10


async def _fetch_preview_images(db: AsyncSession, wishlist_ids: list[uuid.UUID]) -> dict[uuid.UUID, list[str]]:
    """Return up to 3 non-null image_urls per wishlist, ordered by position."""
    if not wishlist_ids:
        return {}
    stmt = (
        select(WishItem.wishlist_id, WishItem.image_url)
        .where(WishItem.wishlist_id.in_(wishlist_ids))
        .where(WishItem.image_url.is_not(None))
        .order_by(WishItem.wishlist_id, WishItem.position.asc())
    )
    rows = (await db.execute(stmt)).all()
    result: dict[uuid.UUID, list[str]] = {wid: [] for wid in wishlist_ids}
    for row in rows:
        bucket = result[row.wishlist_id]
        if len(bucket) < 3:
            bucket.append(row.image_url)
    return result


async def _generate_slug(db: AsyncSession) -> str:
    for _ in range(3):
        slug = secrets.token_urlsafe(8)
        result = await db.execute(select(Wishlist).where(Wishlist.slug == slug))
        if result.scalar_one_or_none() is None:
            return slug
    raise HTTPException(
        status_code=500,
        detail={"error": {"code": "SLUG_GENERATION_FAILED", "message": "Could not generate a unique slug."}},
    )


async def list_wishlists(
    db: AsyncSession, user: User, limit: int, offset: int
) -> tuple[list[tuple[Wishlist, int, list[str]]], int]:
    item_count_subq = (
        select(WishItem.wishlist_id, func.count(WishItem.id).label("item_count"))
        .group_by(WishItem.wishlist_id)
        .subquery()
    )

    stmt = (
        select(Wishlist, func.coalesce(item_count_subq.c.item_count, 0).label("item_count"))
        .outerjoin(item_count_subq, Wishlist.id == item_count_subq.c.wishlist_id)
        .where(Wishlist.user_id == user.id)
        .order_by(Wishlist.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    count_stmt = select(func.count()).select_from(Wishlist).where(Wishlist.user_id == user.id)

    results = await db.execute(stmt)
    total_result = await db.execute(count_stmt)

    rows = [(row.Wishlist, row.item_count) for row in results.all()]
    total = total_result.scalar_one()

    wishlist_ids = [w.id for w, _ in rows]
    preview_map = await _fetch_preview_images(db, wishlist_ids)

    return [(w, count, preview_map[w.id]) for w, count in rows], total


async def create_wishlist(db: AsyncSession, user: User, data: WishlistCreate) -> Wishlist:
    count_result = await db.execute(select(func.count()).select_from(Wishlist).where(Wishlist.user_id == user.id))
    if count_result.scalar_one() >= MAX_WISHLISTS_PER_USER:
        raise HTTPException(
            status_code=409,
            detail={
                "error": {"code": "WISHLIST_LIMIT_REACHED", "message": "You have reached the maximum of 10 wishlists."}
            },  # noqa: E501
        )

    slug = await _generate_slug(db)

    wishlist = Wishlist(
        user_id=user.id,
        title=data.title,
        description=data.description,
        visibility=data.visibility,
        event_type=data.event_type,
        event_date=data.event_date,
        reservation_mode=data.reservation_mode,
        slug=slug,
    )
    db.add(wishlist)
    await db.commit()
    await db.refresh(wishlist)
    return wishlist


async def get_wishlist(db: AsyncSession, wishlist_id: uuid.UUID, user: User) -> Wishlist:
    result = await db.execute(select(Wishlist).where(Wishlist.id == wishlist_id))
    wishlist = result.scalar_one_or_none()

    if wishlist is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "WISHLIST_NOT_FOUND", "message": "Wishlist not found."}},
        )
    if wishlist.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail={"error": {"code": "FORBIDDEN", "message": "You do not own this wishlist."}},
        )
    return wishlist


async def get_item_count(db: AsyncSession, wishlist_id: uuid.UUID) -> int:
    result = await db.execute(select(func.count()).select_from(WishItem).where(WishItem.wishlist_id == wishlist_id))
    return result.scalar_one()


async def update_wishlist(db: AsyncSession, wishlist: Wishlist, data: WishlistUpdate) -> Wishlist:
    for field in data.model_fields_set:
        setattr(wishlist, field, getattr(data, field))
    await db.commit()
    await db.refresh(wishlist)
    return wishlist


async def delete_wishlist(db: AsyncSession, wishlist: Wishlist) -> None:
    await db.delete(wishlist)
    await db.commit()


async def get_preview_images(db: AsyncSession, wishlist_id: uuid.UUID) -> list[str]:
    stmt = (
        select(WishItem.image_url)
        .where(WishItem.wishlist_id == wishlist_id)
        .where(WishItem.image_url.is_not(None))
        .order_by(WishItem.position.asc())
        .limit(3)
    )
    return list((await db.execute(stmt)).scalars().all())
