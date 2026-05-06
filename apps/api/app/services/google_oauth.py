import urllib.parse

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.models.user import User

_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def get_google_auth_url() -> str:
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    return _GOOGLE_AUTH_URL + "?" + urllib.parse.urlencode(params)


async def exchange_code_for_profile(code: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        token_resp = await client.post(
            _GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        token_resp.raise_for_status()
        tokens = token_resp.json()

        userinfo_resp = await client.get(
            _GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        userinfo_resp.raise_for_status()
        return userinfo_resp.json()


async def upsert_google_user(db: AsyncSession, profile: dict) -> User:
    google_id: str = profile["sub"]
    email: str | None = profile.get("email")
    display_name: str | None = profile.get("name")
    avatar_url: str | None = profile.get("picture")

    # 1. Match by google_id — returning user who already linked Google
    user = await db.scalar(select(User).where(User.google_id == google_id))
    if user:
        return user

    # 2. Match by email — existing email/password account; link google_id to it
    if email:
        user = await db.scalar(select(User).where(User.email == email))
        if user:
            user.google_id = google_id
            user.is_email_verified = True
            if not user.avatar_url and avatar_url:
                user.avatar_url = avatar_url
            await db.flush()
            return user

    # 3. No match — create a brand-new Google-only account
    user = User(
        email=email,
        google_id=google_id,
        display_name=display_name,
        avatar_url=avatar_url,
        is_email_verified=True,
    )
    db.add(user)
    await db.flush()
    return user
