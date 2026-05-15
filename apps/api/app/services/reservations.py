import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import ReservationMode
from app.models.reservation import Reservation
from app.models.user import User
from app.models.wish_item import WishItem
from app.models.wishlist import Wishlist
from app.schemas.reservations import ReservationCreate


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
