from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import WishlistVisibility
from app.models.reservation import Reservation
from app.models.user import User
from app.models.wish_item import WishItem
from app.models.wishlist import Wishlist
from app.schemas.shared import MyReservation, SharedAuthor, SharedItemResponse


async def get_shared_wishlist(
    db: AsyncSession,
    slug: str,
    current_user: User | None,
) -> tuple[Wishlist, User, list[SharedItemResponse]]:
    row = (
        await db.execute(
            select(Wishlist, User)
            .join(User, Wishlist.user_id == User.id)
            .where(Wishlist.slug == slug)
        )
    ).first()

    if not row or row.Wishlist.visibility == WishlistVisibility.private:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "NOT_FOUND", "message": "Wishlist not found."}},
        )

    wishlist, owner = row.Wishlist, row.User

    item_rows = (
        await db.execute(
            select(WishItem, Reservation)
            .outerjoin(Reservation, Reservation.item_id == WishItem.id)
            .where(WishItem.wishlist_id == wishlist.id)
            .order_by(WishItem.position)
        )
    ).all()

    items: list[SharedItemResponse] = []
    for item_row in item_rows:
        item = item_row.WishItem
        reservation = item_row.Reservation

        my_reservation = None
        if reservation and current_user and reservation.reserver_id == current_user.id:
            my_reservation = MyReservation(anon_token=None)

        items.append(
            SharedItemResponse(
                id=item.id,
                title=item.title,
                description=item.description,
                image_url=item.image_url,
                product_url=item.product_url,
                price_min=item.price_min,
                price_max=item.price_max,
                currency=item.currency,
                priority=item.priority,
                position=item.position,
                notes=item.notes,
                tags=item.tags,
                is_reserved=reservation is not None,
                is_fulfilled=reservation.is_fulfilled if reservation else False,
                my_reservation=my_reservation,
            )
        )

    return wishlist, owner, items
