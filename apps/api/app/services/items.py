import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reservation import Reservation
from app.models.user import User
from app.models.wish_item import WishItem
from app.models.wishlist import Wishlist
from app.schemas.items import (
    WishItemCreate,
    WishItemResponse,
    WishItemUpdate,
)


async def list_items(
    db: AsyncSession, wishlist: Wishlist, limit: int, offset: int
) -> tuple[list, int]:
    is_reserved_col = (
        select(func.count(Reservation.id))
        .where(Reservation.item_id == WishItem.id)
        .correlate(WishItem)
        .scalar_subquery()
        .label("is_reserved")
    )
    stmt = (
        select(WishItem, is_reserved_col)
        .where(WishItem.wishlist_id == wishlist.id)
        .order_by(WishItem.position.asc())
        .limit(limit)
        .offset(offset)
    )
    count_stmt = (
        select(func.count())
        .select_from(WishItem)
        .where(WishItem.wishlist_id == wishlist.id)
    )
    rows = (await db.execute(stmt)).all()
    total = (await db.execute(count_stmt)).scalar_one()
    return rows, total


async def create_item(db: AsyncSession, wishlist: Wishlist, data: WishItemCreate) -> WishItem:
    max_pos = (
        await db.execute(
            select(func.max(WishItem.position)).where(WishItem.wishlist_id == wishlist.id)
        )
    ).scalar_one_or_none()

    item = WishItem(
        wishlist_id=wishlist.id,
        title=data.title,
        description=data.description,
        image_url=data.image_url,
        product_url=data.product_url,
        price_min=data.price_min,
        price_max=data.price_max,
        currency=data.currency,
        priority=data.priority,
        is_surprise=data.is_surprise,
        notes=data.notes,
        tags=data.tags,
        position=(max_pos + 1) if max_pos is not None else 0,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def get_item_by_id(db: AsyncSession, item_id: uuid.UUID) -> WishItem:
    item = (
        await db.execute(select(WishItem).where(WishItem.id == item_id))
    ).scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "ITEM_NOT_FOUND", "message": "Wish item not found."}},
        )
    return item


async def get_item_for_owner(
    db: AsyncSession, item_id: uuid.UUID, user: User
) -> WishItem:
    item = (
        await db.execute(select(WishItem).where(WishItem.id == item_id))
    ).scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=404,
            detail={"error": {"code": "ITEM_NOT_FOUND", "message": "Wish item not found."}},
        )
    owner_id = (
        await db.execute(select(Wishlist.user_id).where(Wishlist.id == item.wishlist_id))
    ).scalar_one_or_none()
    if owner_id != user.id:
        raise HTTPException(
            status_code=403,
            detail={"error": {"code": "FORBIDDEN", "message": "You do not own this wish item."}},
        )
    return item


async def update_item(db: AsyncSession, item: WishItem, data: WishItemUpdate) -> WishItem:
    for field in data.model_fields_set:
        setattr(item, field, getattr(data, field))
    await db.commit()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, item: WishItem) -> None:
    await db.delete(item)
    await db.commit()


async def update_position(db: AsyncSession, item: WishItem, position: int) -> WishItem:
    item.position = position
    await db.commit()
    await db.refresh(item)
    return item


async def get_is_reserved(db: AsyncSession, item_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(func.count(Reservation.id)).where(Reservation.item_id == item_id)
    )
    return result.scalar_one() > 0


def build_item_response(item: WishItem, is_reserved: bool) -> WishItemResponse:
    return WishItemResponse(
        id=item.id,
        wishlist_id=item.wishlist_id,
        title=item.title,
        description=item.description,
        image_url=item.image_url,
        product_url=item.product_url,
        price_min=item.price_min,
        price_max=item.price_max,
        currency=item.currency,
        priority=item.priority,
        is_surprise=item.is_surprise,
        position=item.position,
        notes=item.notes,
        tags=item.tags,
        is_reserved=is_reserved,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )
