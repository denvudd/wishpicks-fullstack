import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.dependencies.get_current_user import get_current_user
from app.dependencies.get_db import get_db
from app.models.user import User
from app.models.wishlist import Wishlist
from app.schemas.wishlists import (
    WishlistCreate,
    WishlistInviteCreate,
    WishlistInviteListResponse,
    WishlistInviteResponse,
    WishlistListResponse,
    WishlistResponse,
    WishlistSingleResponse,
    WishlistUpdate,
)
from app.schemas.items import WishItemCreate, WishItemListResponse, WishItemSingleResponse
from app.services import items as item_service
from app.services import wishlist_invites as invite_service
from app.services import wishlists as wishlist_service

router = APIRouter()


def _build_response(wishlist: Wishlist, item_count: int) -> WishlistResponse:
    return WishlistResponse(
        id=wishlist.id,
        title=wishlist.title,
        description=wishlist.description,
        visibility=wishlist.visibility,
        event_type=wishlist.event_type,
        event_date=wishlist.event_date,
        reservation_mode=wishlist.reservation_mode,
        slug=wishlist.slug,
        cover_url=wishlist.cover_url,
        item_count=item_count,
        created_at=wishlist.created_at,
        updated_at=wishlist.updated_at,
    )


@router.get(
    "",
    summary="List current user's wishlists",
    response_model=WishlistListResponse,
    responses={401: {"description": "Not authenticated"}},
)
async def list_wishlists(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WishlistListResponse:
    rows, total = await wishlist_service.list_wishlists(db, current_user, limit, offset)
    items = [_build_response(wishlist, count) for wishlist, count in rows]
    return WishlistListResponse(
        data={"items": items, "total": total, "limit": limit, "offset": offset}
    )


@router.post(
    "",
    summary="Create a wishlist",
    response_model=WishlistSingleResponse,
    status_code=201,
    responses={
        401: {"description": "Not authenticated"},
        409: {"description": "Wishlist limit reached (max 10)"},
        422: {"description": "Validation error"},
    },
)
@limiter.limit("20/minute")
async def create_wishlist(
    request: Request,
    body: WishlistCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WishlistSingleResponse:
    wishlist = await wishlist_service.create_wishlist(db, current_user, body)
    return WishlistSingleResponse(data=_build_response(wishlist, 0))


@router.get(
    "/{wishlist_id}",
    summary="Get wishlist (owner view)",
    response_model=WishlistSingleResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden — not the owner"},
        404: {"description": "Wishlist not found"},
    },
)
async def get_wishlist(
    wishlist_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WishlistSingleResponse:
    wishlist = await wishlist_service.get_wishlist(db, wishlist_id, current_user)
    count = await wishlist_service.get_item_count(db, wishlist.id)
    return WishlistSingleResponse(data=_build_response(wishlist, count))


@router.patch(
    "/{wishlist_id}",
    summary="Update wishlist",
    response_model=WishlistSingleResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden — not the owner"},
        404: {"description": "Wishlist not found"},
        422: {"description": "Validation error"},
    },
)
async def update_wishlist(
    wishlist_id: uuid.UUID,
    body: WishlistUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WishlistSingleResponse:
    wishlist = await wishlist_service.get_wishlist(db, wishlist_id, current_user)
    updated = await wishlist_service.update_wishlist(db, wishlist, body)
    count = await wishlist_service.get_item_count(db, updated.id)
    return WishlistSingleResponse(data=_build_response(updated, count))


@router.delete(
    "/{wishlist_id}",
    summary="Delete wishlist",
    status_code=204,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden — not the owner"},
        404: {"description": "Wishlist not found"},
    },
)
async def delete_wishlist(
    wishlist_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    wishlist = await wishlist_service.get_wishlist(db, wishlist_id, current_user)
    await wishlist_service.delete_wishlist(db, wishlist)


@router.get(
    "/{wishlist_id}/invites",
    summary="List invites for a private wishlist",
    response_model=WishlistInviteListResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden — not the owner"},
        404: {"description": "Wishlist not found"},
    },
)
async def list_invites(
    wishlist_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WishlistInviteListResponse:
    wishlist = await wishlist_service.get_wishlist(db, wishlist_id, current_user)
    invites = await invite_service.list_invites(db, wishlist)
    return WishlistInviteListResponse(
        data={"items": [WishlistInviteResponse.model_validate(i) for i in invites]}
    )


@router.post(
    "/{wishlist_id}/invites",
    summary="Invite an email to a private wishlist",
    response_model=WishlistInviteResponse,
    status_code=201,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden — not the owner"},
        404: {"description": "Wishlist not found"},
        409: {"description": "Email already invited"},
        422: {"description": "Wishlist is not private"},
    },
)
@limiter.limit("10/minute")
async def create_invite(
    wishlist_id: uuid.UUID,
    body: WishlistInviteCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WishlistInviteResponse:
    wishlist = await wishlist_service.get_wishlist(db, wishlist_id, current_user)
    invite = await invite_service.create_invite(db, wishlist, body.email)
    return WishlistInviteResponse.model_validate(invite)


@router.delete(
    "/{wishlist_id}/invites/{invite_id}",
    summary="Revoke an invite",
    status_code=204,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden — not the owner"},
        404: {"description": "Wishlist not found"},
    },
)
async def delete_invite(
    wishlist_id: uuid.UUID,
    invite_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    wishlist = await wishlist_service.get_wishlist(db, wishlist_id, current_user)
    await invite_service.delete_invite(db, wishlist, invite_id)


@router.get(
    "/{wishlist_id}/items",
    summary="List items in a wishlist",
    response_model=WishItemListResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden — not the owner"},
        404: {"description": "Wishlist not found"},
    },
)
async def list_items(
    wishlist_id: uuid.UUID,
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    is_reserved: bool | None = Query(default=None),
    is_fulfilled: bool | None = Query(default=None),
    priority: list[int] | None = Query(default=None),
    store: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WishItemListResponse:
    wishlist = await wishlist_service.get_wishlist(db, wishlist_id, current_user)
    rows, total, available_stores = await item_service.list_items(
        db, wishlist, limit, offset, is_reserved, is_fulfilled, priority, store
    )
    items = [
        item_service.build_item_response(row.WishItem, bool(row.is_reserved), bool(row.is_fulfilled))
        for row in rows
    ]
    return WishItemListResponse(
        data={
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
            "available_stores": available_stores,
        }
    )


@router.post(
    "/{wishlist_id}/items",
    summary="Add a wish item to a wishlist",
    response_model=WishItemSingleResponse,
    status_code=201,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden — not the owner"},
        404: {"description": "Wishlist not found"},
        422: {"description": "Validation error"},
    },
)
async def create_item(
    wishlist_id: uuid.UUID,
    body: WishItemCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WishItemSingleResponse:
    wishlist = await wishlist_service.get_wishlist(db, wishlist_id, current_user)
    item = await item_service.create_item(db, wishlist, body)
    return WishItemSingleResponse(data=item_service.build_item_response(item, False, False))
