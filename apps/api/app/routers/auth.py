from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.dependencies.get_current_user import get_current_user
from app.dependencies.get_db import get_db
from app.dependencies.get_redis import get_redis
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.services import auth as auth_service

router = APIRouter()


def _set_auth_cookies(
    response: Response, access_token: str, refresh_token: str
) -> None:
    from app.core.settings import settings

    secure = settings.ENVIRONMENT == "production"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=secure,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/auth/refresh",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/api/auth/refresh")


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=201,
    summary="Register a new user account",
    responses={
        409: {"description": "Email already registered"},
        422: {"description": "Validation error"},
    },
)
@limiter.limit("3/minute")
async def register(
    request: Request,
    data: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user, access_token, refresh_token = await auth_service.register(db, data)
    _set_auth_cookies(response, access_token, refresh_token)
    return AuthResponse(data=UserResponse.model_validate(user))


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Authenticate with email and password",
    responses={401: {"description": "Invalid credentials"}},
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    data: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    user, access_token, refresh_token = await auth_service.login(db, data)
    _set_auth_cookies(response, access_token, refresh_token)
    return AuthResponse(data=UserResponse.model_validate(user))


@router.post(
    "/logout",
    status_code=204,
    summary="Invalidate the current session and clear auth cookies",
)
@limiter.limit("10/minute")
async def logout(
    request: Request,
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    from jose import JWTError

    from app.core.security import decode_token

    jti_str = None
    if refresh_token:
        try:
            payload = decode_token(refresh_token)
            jti_str = payload.get("jti")
        except JWTError:
            pass
    await auth_service.logout(db, jti_str)
    _clear_auth_cookies(response)


@router.post(
    "/refresh",
    response_model=AuthResponse,
    summary="Rotate access and refresh tokens",
    responses={401: {"description": "Missing, invalid, or stolen refresh token"}},
)
@limiter.limit("10/minute")
async def refresh(
    request: Request,
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "NOT_AUTHENTICATED",
                    "message": "Authentication required.",
                }
            },
        )
    user, access_token, new_refresh_token = await auth_service.refresh_tokens(
        db, redis, refresh_token
    )
    _set_auth_cookies(response, access_token, new_refresh_token)
    return AuthResponse(data=UserResponse.model_validate(user))


@router.get(
    "/me",
    response_model=AuthResponse,
    summary="Return the currently authenticated user",
    responses={401: {"description": "Not authenticated"}},
)
@limiter.limit("10/minute")
async def me(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return AuthResponse(data=UserResponse.model_validate(current_user))
