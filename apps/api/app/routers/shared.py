from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.get_current_user import optional_current_user
from app.dependencies.get_db import get_db
from app.models.user import User
from app.schemas.shared import (
    SharedAuthor,
    SharedWishlistData,
    SharedWishlistResponse,
    SharedWishlistSchema,
)
from app.services import shared as shared_service

router = APIRouter()


@router.get(
    "/{slug}",
    summary="Get shared wishlist (public guest view)",
    response_model=SharedWishlistResponse,
    responses={404: {"description": "Wishlist not found or private"}},
)
async def get_shared_wishlist(
    slug: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(optional_current_user),
) -> SharedWishlistResponse:
    wishlist, owner, items = await shared_service.get_shared_wishlist(db, slug, current_user)
    return SharedWishlistResponse(
        data=SharedWishlistData(
            wishlist=SharedWishlistSchema(
                id=wishlist.id,
                title=wishlist.title,
                description=wishlist.description,
                cover_url=wishlist.cover_url,
                event_type=wishlist.event_type,
                event_date=wishlist.event_date,
                reservation_mode=wishlist.reservation_mode,
                slug=wishlist.slug,
                created_at=wishlist.created_at,
                author=SharedAuthor(
                    display_name=owner.display_name,
                    avatar_url=owner.avatar_url,
                ),
            ),
            items=items,
        )
    )
