from fastapi import FastAPI

from app.core.settings import settings
from app.middleware.cors import add_cors_middleware
from app.middleware.csrf import add_csrf_middleware
from app.middleware.security_headers import add_security_headers_middleware
from app.routers import auth, items, media, reservations, saved, wishlists

app = FastAPI(title="Wishpicks API", version="0.1.0")

add_cors_middleware(app)
add_security_headers_middleware(app)
add_csrf_middleware(app)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(wishlists.router, prefix="/api/wishlists", tags=["wishlists"])
app.include_router(items.router, prefix="/api/items", tags=["items"])
app.include_router(reservations.router, prefix="/api", tags=["reservations"])
app.include_router(saved.router, prefix="/api/saved", tags=["saved"])
app.include_router(media.router, prefix="/api/media", tags=["media"])


@app.get("/api/health", tags=["health"])
async def health():
    return {"data": {"status": "ok", "environment": settings.ENVIRONMENT}}
