from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cookies import clear_auth_cookies
from app.core.limiter import limiter
from app.dependencies.get_current_user import get_current_user
from app.dependencies.get_db import get_db
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.users import UserProfileResponse, UserUpdateRequest
from app.services import users as users_service

router = APIRouter()


@router.patch(
    "/me",
    response_model=UserProfileResponse,
    summary="Update the current user's profile",
    responses={
        401: {"description": "Not authenticated"},
        409: {"description": "Username already taken"},
        422: {"description": "Validation error"},
    },
    tags=["users"],
)
@limiter.limit("10/minute")
async def update_profile(
    request: Request,
    data: UserUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await users_service.update_profile(db, current_user, data)
    return UserProfileResponse(data=UserResponse.model_validate(user))


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Permanently delete the current user's account",
    responses={401: {"description": "Not authenticated"}},
    tags=["users"],
)
@limiter.limit("10/minute")
async def delete_account(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await users_service.delete_account(db, current_user)
    clear_auth_cookies(response)
