import uuid

from fastapi import HTTPException
from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.saved import SavedItem, SavedWishlist
from app.models.user import User
from app.models.wish_item import WishItem
from app.models.wishlist import Wishlist
from app.schemas.saved import CopyItemRequest
from app.services.items import _extract_store_domain
from app.services.wishlists import _fetch_preview_images

# ── Saved wishlists ──────────────────────────────────────────────────────────


async def list_saved_wishlists(
    db: AsyncSession, user: User, limit: int, offset: int
) -> tuple[list, int]:
    item_count_subq = (
        select(WishItem.wishlist_id, func.count(WishItem.id).label("item_count"))
        .group_by(WishItem.wishlist_id)
        .subquery()
    )

    stmt = (
        select(
            SavedWishlist.saved_at,
            Wishlist,
            func.coalesce(item_count_subq.c.item_count, 0).label("item_count"),
        )
        .join(Wishlist, SavedWishlist.wishlist_id == Wishlist.id)
        .outerjoin(item_count_subq, Wishlist.id == item_count_subq.c.wishlist_id)
        .options(selectinload(Wishlist.owner))
        .where(SavedWishlist.user_id == user.id)
        .order_by(SavedWishlist.saved_at.desc())
        .limit(limit)
        .offset(offset)
    )
    count_stmt = (
        select(func.count())
        .select_from(SavedWishlist)
        .where(SavedWishlist.user_id == user.id)
    )

    rows = (await db.execute(stmt)).all()
    total = (await db.execute(count_stmt)).scalar_one()

    wishlist_ids = [row.Wishlist.id for row in rows]
    preview_map = await _fetch_preview_images(db, wishlist_ids)

    return [(row.Wishlist, row.item_count, preview_map[row.Wishlist.id], row.saved_at) for row in rows], total


async def save_wishlist(db: AsyncSession, user: User, wishlist_id: uuid.UUID) -> tuple[Wishlist, SavedWishlist]:
    wishlist = (
        await db.execute(
            select(Wishlist).where(Wishlist.id == wishlist_id).options(selectinload(Wishlist.owner))
        )
    ).scalar_one_or_none()
    if wishlist is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "WISHLIST_NOT_FOUND", "message": "Wishlist not found."}},
        )
    if wishlist.user_id == user.id:
        raise HTTPException(
            status_code=403,
            detail={"error": {"code": "FORBIDDEN", "message": "Cannot save your own wishlist."}},
        )

    existing = (
        await db.execute(
            select(SavedWishlist).where(
                SavedWishlist.user_id == user.id,
                SavedWishlist.wishlist_id == wishlist_id,
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail={"error": {"code": "ALREADY_SAVED", "message": "Wishlist already saved."}},
        )

    saved = SavedWishlist(user_id=user.id, wishlist_id=wishlist_id)
    db.add(saved)
    await db.commit()
    await db.refresh(saved)
    return wishlist, saved


async def unsave_wishlist(db: AsyncSession, user: User, wishlist_id: uuid.UUID) -> None:
    result = await db.execute(
        delete(SavedWishlist).where(
            SavedWishlist.user_id == user.id,
            SavedWishlist.wishlist_id == wishlist_id,
        )
    )
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_SAVED", "message": "Wishlist is not in saved list."}},
        )
    await db.commit()


# ── Saved items (copy) ───────────────────────────────────────────────────────


async def list_saved_items(
    db: AsyncSession, user: User, limit: int, offset: int
) -> tuple[list, int]:
    stmt = (
        select(SavedItem.saved_at, WishItem)
        .join(WishItem, SavedItem.item_id == WishItem.id)
        .where(SavedItem.user_id == user.id)
        .order_by(SavedItem.saved_at.desc())
        .limit(limit)
        .offset(offset)
    )
    count_stmt = (
        select(func.count())
        .select_from(SavedItem)
        .where(SavedItem.user_id == user.id)
    )

    rows = (await db.execute(stmt)).all()
    total = (await db.execute(count_stmt)).scalar_one()

    return [(row.WishItem, row.saved_at) for row in rows], total


async def copy_and_save_item(
    db: AsyncSession, user: User, source_item_id: uuid.UUID, data: CopyItemRequest
) -> WishItem:
    # Load source item
    source = (
        await db.execute(select(WishItem).where(WishItem.id == source_item_id))
    ).scalar_one_or_none()
    if source is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "ITEM_NOT_FOUND", "message": "Wish item not found."}},
        )

    # Must NOT be the current user's item
    source_owner_id = (
        await db.execute(select(Wishlist.user_id).where(Wishlist.id == source.wishlist_id))
    ).scalar_one_or_none()
    if source_owner_id == user.id:
        raise HTTPException(
            status_code=403,
            detail={"error": {"code": "FORBIDDEN", "message": "Cannot copy your own wish item."}},
        )

    # Target wishlist must belong to the current user
    target = (
        await db.execute(
            select(Wishlist).where(Wishlist.id == data.wishlist_id, Wishlist.user_id == user.id)
        )
    ).scalar_one_or_none()
    if target is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "WISHLIST_NOT_FOUND", "message": "Target wishlist not found."}},
        )

    # Next position in target wishlist
    max_pos = (
        await db.execute(
            select(func.max(WishItem.position)).where(WishItem.wishlist_id == target.id)
        )
    ).scalar_one_or_none()

    copy = WishItem(
        wishlist_id=target.id,
        title=source.title,
        description=source.description,
        image_url=source.image_url,
        images=source.images,
        product_url=source.product_url,
        store_domain=_extract_store_domain(source.product_url),
        price_min=source.price_min,
        price_max=source.price_max,
        currency=source.currency,
        priority=data.priority,
        notes=data.notes,
        position=(max_pos + 1) if max_pos is not None else 0,
    )
    db.add(copy)

    # Record bookmark; ignore if already bookmarked
    await db.execute(
        pg_insert(SavedItem)
        .values(user_id=user.id, item_id=source_item_id)
        .on_conflict_do_nothing()
    )

    await db.commit()
    await db.refresh(copy)
    return copy


async def unsave_item(db: AsyncSession, user: User, source_item_id: uuid.UUID) -> None:
    result = await db.execute(
        delete(SavedItem).where(
            SavedItem.user_id == user.id,
            SavedItem.item_id == source_item_id,
        )
    )
    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "NOT_SAVED", "message": "Item is not in saved list."}},
        )
    await db.commit()
