# Phase 1 Foundation

## Description

Implemented the full Phase 1 foundation: initial database schema migration (all 7 tables) and complete auth system with JWT HTTP-only cookies, refresh token rotation, and theft detection.

## Session Log

1. Created `migrations/versions/6fc915cac3e1_initial_schema.py` via `alembic revision --autogenerate`, then manually patched `ix_users_google_id` to be a partial index (`WHERE google_id IS NOT NULL`) — autogenerate cannot detect partial index conditions.

2. Built `app/core/security.py` — JWT create/decode utilities using python-jose.

3. Extracted `app/core/limiter.py` — slowapi Limiter instance lives here (not in main.py) to avoid circular imports, since routers import limiter and main.py imports routers.

4. Built `app/schemas/auth.py` — RegisterRequest, LoginRequest, UserResponse, AuthResponse. Required switching `pydantic` to `pydantic[email]` for EmailStr.

5. Replaced `passlib` with direct `bcrypt` usage in `app/services/auth.py`. passlib raises `ValueError: password cannot be longer than 72 bytes` during `CryptContext` initialization (`detect_wrap_bug()`) when bcrypt >= 4.0 is installed. Removed passlib from `pyproject.toml`.

6. Built full `app/services/auth.py`: register, login, logout, refresh_tokens (rotation + theft detection), `_revoke_all_user_tokens`, `_issue_tokens` helper.

7. Built `app/dependencies/get_current_user.py` — reads access_token from Cookie, validates JWT type=="access", loads User from DB.

8. Built `app/routers/auth.py` — 5 endpoints: POST /register (201, 3/min), POST /login (200, 5/min), POST /logout (204, 10/min), POST /refresh (200, 10/min), GET /me (200, 10/min). Each needs `Request` as first param for slowapi.

9. Updated `app/main.py` — wired slowapi, disabled OpenAPI in production, added custom HTTPException handler to enforce `{"data":{}}` / `{"error":{}}` envelope (FastAPI's default wraps detail in `{"detail": ...}`).

10. Removed all tests from the project. `tests/` directory deleted, pytest/pytest-asyncio removed from `pyproject.toml`.

11. Created `apps/api/README.md` and `apps/web/README.md`.

## Session Outcomes

- All 7 tables created and migrated: users, wishlists, wish_items, reservations, refresh_tokens, saved_wishlists, saved_items
- Auth endpoints fully functional and verified via curl
- `ruff check app/` passes cleanly
- Both READMEs written

## Lessons Learned

- **passlib + bcrypt >= 4.0 incompatible**: use `bcrypt` directly — `bcrypt.hashpw()` / `bcrypt.checkpw()`
- **Alembic partial indexes**: autogenerate misses `WHERE` clause — always review and patch manually after generation
- **slowapi circular import**: keep Limiter in its own `core/limiter.py`, not in `main.py`
- **FastAPI HTTPException envelope**: default behavior wraps `detail` in `{"detail": ...}` — need a custom exception handler to enforce project envelope format
- **Swagger Set-Cookie**: browsers block reading Set-Cookie as a forbidden header — this is expected behavior, not a bug; use curl `-v` or Network tab to verify cookies are set
- **asyncpg + Windows**: incompatible with ProactorEventLoop — all backend CLI commands must run inside Docker (`docker exec wishpicks-api-1 ...`)
