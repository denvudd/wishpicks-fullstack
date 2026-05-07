from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cookies import clear_auth_cookies, set_auth_cookies
from app.core.limiter import limiter
from app.dependencies.get_current_user import get_current_user
from app.dependencies.get_db import get_db
from app.dependencies.get_redis import get_redis
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
    VerifyEmailRequest,
)
from app.services import auth as auth_service
from app.services.email import send_verification_email
from app.services.otp import (
    OTPCooldownError,
    OTPInvalidError,
    OTPMaxAttemptsError,
    check_and_set_cooldown,
    generate_and_store_otp,
    verify_otp,
)

router = APIRouter()


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
    redis=Depends(get_redis),
):
    user, access_token, refresh_token = await auth_service.register(db, redis, data)
    set_auth_cookies(response, access_token, refresh_token)
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
    set_auth_cookies(response, access_token, refresh_token)
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
    clear_auth_cookies(response)


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
    set_auth_cookies(response, access_token, new_refresh_token)
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


@router.get(
    "/google",
    summary="Redirect to Google OAuth consent screen",
    status_code=302,
    responses={302: {"description": "Redirect to Google consent screen"}},
)
@limiter.limit("10/minute")
async def google_login(request: Request):
    from app.services.google_oauth import get_google_auth_url

    return RedirectResponse(url=get_google_auth_url())


@router.get(
    "/google/callback",
    summary="Handle Google OAuth callback, issue session cookies, redirect to frontend",
    status_code=302,
    responses={302: {"description": "Redirect to dashboard or login on failure"}},
)
@limiter.limit("10/minute")
async def google_callback(
    request: Request,
    code: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    from app.core.settings import settings

    error_redirect = RedirectResponse(
        url=f"{settings.FRONTEND_URL}/login?error=oauth_failed",
        status_code=302,
    )

    if error or not code:
        return error_redirect

    try:
        user, access_token, refresh_token = await auth_service.google_login(db, code)
    except Exception:
        return error_redirect

    success_redirect = RedirectResponse(
        url=f"{settings.FRONTEND_URL}/dashboard",
        status_code=302,
    )
    set_auth_cookies(success_redirect, access_token, refresh_token)
    return success_redirect


@router.post(
    "/verify-email",
    response_model=AuthResponse,
    summary="Verify email address with OTP code",
    responses={
        400: {"description": "Invalid or expired OTP, or max attempts exceeded"},
        401: {"description": "Not authenticated"},
        409: {"description": "Email already verified"},
    },
)
@limiter.limit("10/minute")
async def verify_email(
    request: Request,
    data: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
    redis=Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    if current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "EMAIL_ALREADY_VERIFIED",
                    "message": "Email is already verified.",
                }
            },
        )

    try:
        await verify_otp(redis, current_user.id, data.code)
    except OTPMaxAttemptsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "OTP_MAX_ATTEMPTS",
                    "message": "Too many failed attempts. Request a new code.",
                }
            },
        )
    except OTPInvalidError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "OTP_INVALID",
                    "message": "Invalid or expired verification code.",
                }
            },
        )

    current_user.is_email_verified = True
    await db.commit()
    await db.refresh(current_user)
    return AuthResponse(data=UserResponse.model_validate(current_user))


@router.post(
    "/resend-verification",
    status_code=204,
    summary="Resend email verification OTP",
    responses={
        401: {"description": "Not authenticated"},
        409: {"description": "Email already verified"},
        429: {"description": "Resend cooldown active"},
    },
)
@limiter.limit("5/minute")
async def resend_verification(
    request: Request,
    redis=Depends(get_redis),
    current_user: User = Depends(get_current_user),
):
    if current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "EMAIL_ALREADY_VERIFIED",
                    "message": "Email is already verified.",
                }
            },
        )

    try:
        await check_and_set_cooldown(redis, current_user.id)
    except OTPCooldownError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": {
                    "code": "RESEND_COOLDOWN",
                    "message": "Please wait before requesting another code.",
                }
            },
        )

    otp = await generate_and_store_otp(redis, current_user.id)
    await send_verification_email(current_user.email, otp)
