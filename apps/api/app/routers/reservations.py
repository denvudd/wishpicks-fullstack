import uuid

from fastapi import APIRouter, Depends, Header, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.dependencies.get_current_user import get_current_user, optional_current_user
from app.dependencies.get_db import get_db
from app.models.user import User
from app.schemas.reservations import (
    FulfillRequest,
    MyReservationListData,
    MyReservationListResponse,
    ReservationCreate,
    ReservationResponse,
    ReservationSingleResponse,
)
from app.services import reservations as reservation_service

router = APIRouter()


@router.post(
    "/items/{item_id}/reserve",
    summary="Reserve a wish item",
    response_model=ReservationSingleResponse,
    status_code=201,
    responses={
        403: {"description": "Auth required or registered-only wishlist"},
        404: {"description": "Item not found"},
        409: {"description": "Item already reserved"},
        422: {"description": "Name required for anonymous reservation"},
    },
)
@limiter.limit("10/minute")
async def reserve_item(
    item_id: uuid.UUID,
    body: ReservationCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(optional_current_user),
) -> ReservationSingleResponse:
    reservation = await reservation_service.create_reservation(db, item_id, body, current_user)
    return ReservationSingleResponse(data=ReservationResponse.model_validate(reservation))


@router.delete(
    "/items/{item_id}/reserve",
    summary="Cancel a reservation",
    status_code=204,
    responses={
        403: {"description": "Not authorized"},
        404: {"description": "No reservation found"},
    },
)
@limiter.limit("10/minute")
async def cancel_reservation(
    item_id: uuid.UUID,
    request: Request,
    x_anon_token: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(optional_current_user),
) -> None:
    await reservation_service.delete_reservation(db, item_id, current_user, x_anon_token)


@router.patch(
    "/items/{item_id}/reserve/fulfill",
    summary="Toggle fulfillment status of a reservation",
    status_code=204,
    responses={
        403: {"description": "Not authorized"},
        404: {"description": "No reservation found"},
    },
)
@limiter.limit("10/minute")
async def fulfill_reservation(
    item_id: uuid.UUID,
    body: FulfillRequest,
    request: Request,
    x_anon_token: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(optional_current_user),
) -> None:
    await reservation_service.fulfill_reservation(db, item_id, body.is_fulfilled, current_user, x_anon_token)


@router.get(
    "/reservations",
    summary="List current user's reservations",
    response_model=MyReservationListResponse,
    responses={
        401: {"description": "Not authenticated"},
    },
)
async def list_my_reservations(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MyReservationListResponse:
    items, total = await reservation_service.list_my_reservations(db, current_user.id, limit, offset)
    return MyReservationListResponse(
        data=MyReservationListData(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )
    )
