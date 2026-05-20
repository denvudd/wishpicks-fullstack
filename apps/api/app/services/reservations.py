import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ReservationMode
from app.models.reservation import Reservation
from app.models.user import User
from app.models.wish_item import WishItem
from app.models.wishlist import Wishlist
from app.schemas.reservations import MyReservationResponse, ReservationCreate


async def _get_item_and_wishlist(db: AsyncSession, item_id: uuid.UUID) -> tuple[WishItem, Wishlist]:
    result = await db.execute(
        select(WishItem, Wishlist).join(Wishlist, WishItem.wishlist_id == Wishlist.id).where(WishItem.id == item_id)
    )
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Item not found."}},
        )
    return row.WishItem, row.Wishlist


def _authorize_action(
    reservation: Reservation,
    wishlist: Wishlist,
    current_user: User | None,
    anon_token: str | None,
) -> None:
    if current_user:
        if reservation.reserver_id == current_user.id:
            return
        if wishlist.user_id == current_user.id:
            return
    elif anon_token and reservation.anon_token == anon_token:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"error": {"code": "FORBIDDEN", "message": "Not authorized to modify this reservation."}},
    )


async def create_reservation(
    db: AsyncSession,
    item_id: uuid.UUID,
    body: ReservationCreate,
    current_user: User | None,
) -> Reservation:
    item, wishlist = await _get_item_and_wishlist(db, item_id)

    if wishlist.reservation_mode == ReservationMode.registered_only and not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "AUTH_REQUIRED", "message": "Sign in to reserve this item."}},
        )

    if not current_user and not body.reserver_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "NAME_REQUIRED", "message": "Provide your name to reserve anonymously."}},
        )

    existing = await db.scalar(select(Reservation).where(Reservation.item_id == item_id))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "ALREADY_RESERVED", "message": "This item is already reserved."}},
        )

    anon_token = None if current_user else str(uuid.uuid4())
    reservation = Reservation(
        item_id=item_id,
        reserver_id=current_user.id if current_user else None,
        reserver_name=current_user.display_name if current_user else body.reserver_name,
        is_fulfilled=False,
        anon_token=anon_token,
    )
    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)
    return reservation


async def delete_reservation(
    db: AsyncSession,
    item_id: uuid.UUID,
    current_user: User | None,
    anon_token: str | None,
) -> None:
    item, wishlist = await _get_item_and_wishlist(db, item_id)
    reservation = await db.scalar(select(Reservation).where(Reservation.item_id == item_id))
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "No reservation found."}},
        )
    _authorize_action(reservation, wishlist, current_user, anon_token)
    await db.delete(reservation)
    await db.commit()


async def fulfill_reservation(
    db: AsyncSession,
    item_id: uuid.UUID,
    is_fulfilled: bool,
    current_user: User | None,
    anon_token: str | None,
) -> None:
    item, wishlist = await _get_item_and_wishlist(db, item_id)
    reservation = await db.scalar(select(Reservation).where(Reservation.item_id == item_id))
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "No reservation found."}},
        )
    _authorize_action(reservation, wishlist, current_user, anon_token)
    reservation.is_fulfilled = is_fulfilled
    await db.commit()


async def list_my_reservations(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int,
    offset: int,
) -> tuple[list[MyReservationResponse], int]:
    count_stmt = (
        select(func.count())
        .select_from(Reservation)
        .where(Reservation.reserver_id == user_id)
    )
    total: int = (await db.execute(count_stmt)).scalar_one()

    stmt = (
        select(Reservation, WishItem, Wishlist, User)
        .join(WishItem, Reservation.item_id == WishItem.id)
        .join(Wishlist, WishItem.wishlist_id == Wishlist.id)
        .join(User, Wishlist.user_id == User.id)
        .where(Reservation.reserver_id == user_id)
        .order_by(Reservation.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = (await db.execute(stmt)).all()

    items = [
        MyReservationResponse(
            item_id=row.WishItem.id,
            item_title=row.WishItem.title,
            item_image_url=row.WishItem.image_url,
            item_images=row.WishItem.images,
            item_product_url=row.WishItem.product_url,
            item_price_min=row.WishItem.price_min,
            item_price_max=row.WishItem.price_max,
            item_currency=row.WishItem.currency,
            wishlist_id=row.Wishlist.id,
            wishlist_title=row.Wishlist.title,
            wishlist_slug=row.Wishlist.slug,
            owner_display_name=row.User.display_name,
            is_fulfilled=row.Reservation.is_fulfilled,
            reserved_at=row.Reservation.created_at,
        )
        for row in rows
    ]

    return items, total
