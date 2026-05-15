import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.get_current_user import get_current_user
from app.dependencies.get_db import get_db
from app.models.user import User
from app.schemas.items import WishItemSingleResponse
from app.schemas.saved import (
    CopyItemRequest,
    SavedItemListResponse,
    SavedItemResponse,
    SavedWishlistListResponse,
    SavedWishlistResponse,
    SavedWishlistSingleResponse,
)
from app.services import items as item_service
from app.services import saved as saved_service
from app.services.wishlists import get_item_count, get_preview_images

router = APIRouter()


def _build_saved_wishlist_response(
    wishlist, item_count: int, preview_images: list[str], saved_at
) -> SavedWishlistResponse:
    return SavedWishlistResponse(
        id=wishlist.id,
        title=wishlist.title,
        description=wishlist.description,
        visibility=wishlist.visibility,
        slug=wishlist.slug,
        cover_url=wishlist.cover_url,
        item_count=item_count,
        preview_images=preview_images,
        owner_display_name=wishlist.owner.display_name if wishlist.owner else None,
        saved_at=saved_at,
    )


# ── Saved wishlists ──────────────────────────────────────────────────────────


@router.get(
    "/wishlists",
    summary="List saved wishlists",
    response_model=SavedWishlistListResponse,
    responses={401: {"description": "Not authenticated"}},
)
async def list_saved_wishlists(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavedWishlistListResponse:
    rows, total = await saved_service.list_saved_wishlists(db, current_user, limit, offset)
    items = [_build_saved_wishlist_response(w, count, previews, saved_at) for w, count, previews, saved_at in rows]
    return SavedWishlistListResponse(data={"items": items, "total": total, "limit": limit, "offset": offset})


@router.post(
    "/wishlists/{wishlist_id}",
    summary="Save a wishlist",
    response_model=SavedWishlistSingleResponse,
    status_code=201,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Cannot save your own wishlist"},
        404: {"description": "Wishlist not found"},
        409: {"description": "Already saved"},
    },
)
async def save_wishlist(
    wishlist_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavedWishlistSingleResponse:
    wishlist, saved = await saved_service.save_wishlist(db, current_user, wishlist_id)
    count = await get_item_count(db, wishlist.id)
    previews = await get_preview_images(db, wishlist.id)
    return SavedWishlistSingleResponse(data=_build_saved_wishlist_response(wishlist, count, previews, saved.saved_at))


@router.delete(
    "/wishlists/{wishlist_id}",
    summary="Unsave a wishlist",
    status_code=204,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Wishlist not in saved list"},
    },
)
async def unsave_wishlist(
    wishlist_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await saved_service.unsave_wishlist(db, current_user, wishlist_id)


# ── Saved items (copy) ───────────────────────────────────────────────────────


@router.get(
    "/items",
    summary="List saved (source) items",
    response_model=SavedItemListResponse,
    responses={401: {"description": "Not authenticated"}},
)
async def list_saved_items(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SavedItemListResponse:
    rows, total = await saved_service.list_saved_items(db, current_user, limit, offset)
    items = [
        SavedItemResponse(
            item_id=item.id,
            wishlist_id=item.wishlist_id,
            title=item.title,
            image_url=item.image_url,
            images=item.images,
            product_url=item.product_url,
            price_min=item.price_min,
            price_max=item.price_max,
            currency=item.currency,
            saved_at=saved_at,
        )
        for item, saved_at in rows
    ]
    return SavedItemListResponse(data={"items": items, "total": total, "limit": limit, "offset": offset})


@router.post(
    "/items/{item_id}",
    summary="Copy a wish item into one of your wishlists",
    response_model=WishItemSingleResponse,
    status_code=201,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Cannot copy your own item, or target wishlist not yours"},
        404: {"description": "Source item or target wishlist not found"},
        422: {"description": "Validation error"},
    },
)
async def copy_item(
    item_id: uuid.UUID,
    body: CopyItemRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WishItemSingleResponse:
    new_item = await saved_service.copy_and_save_item(db, current_user, item_id, body)
    return WishItemSingleResponse(
        data=item_service.build_item_response(new_item, is_reserved=False, is_fulfilled=False)
    )


@router.delete(
    "/items/{item_id}",
    summary="Remove a wish item from saved list (does not delete the copied item)",
    status_code=204,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Item not in saved list"},
    },
)
async def unsave_item(
    item_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    await saved_service.unsave_item(db, current_user, item_id)
