# User Profile Read + Update (API)

## Description

Implemented `GET /api/users/me`, `PATCH /api/users/me`, `DELETE /api/users/me` endpoints. No migration needed — all fields already existed on the `User` model.

## Session Log

### Refactor — shared cookie utilities

1. Extracted `_set_auth_cookies` and `_clear_auth_cookies` from `app/routers/auth.py` into a new shared module `app/core/cookies.py` as `set_auth_cookies` / `clear_auth_cookies`.

2. Updated `app/routers/auth.py` to import from `app.core.cookies` — all five call-sites updated (register, login, logout, refresh, google_callback).

### New — `app/schemas/users.py`

3. `UserUpdateRequest` — PATCH schema with optional `username`, `display_name`, `avatar_url`:
   - `username` validated against `^[a-z0-9_-]{3,30}$` via `field_validator`
   - All fields default to `None`; `model_fields_set` used in service to apply only provided fields

4. `UserProfileResponse` — envelope `data: UserResponse`, reuses existing `UserResponse` from `auth.py` to avoid duplication.

### New — `app/services/users.py`

5. `update_profile(db, user, data)`:
   - If `username` is in `model_fields_set` and not None → uniqueness check against other users → 409 `USERNAME_TAKEN` on conflict
   - Applies only fields present in `model_fields_set` via `setattr` loop
   - `commit` + `refresh` → returns updated user

6. `delete_account(db, user)`:
   - `db.delete(user)` — ORM cascade (`all, delete-orphan`) handles wishlists, refresh_tokens, saved_wishlists, saved_items
   - `commit`

### New — `app/routers/users.py`

7. Three endpoints, all rate-limited at `10/minute`:
   - `GET /me` → 200 `UserProfileResponse`
   - `PATCH /me` → 200 `UserProfileResponse`; 409 on username conflict; 422 on validation
   - `DELETE /me` → 204; clears auth cookies after account deletion

### Updated — `app/main.py`

8. Registered `users.router` at prefix `/api/users`.

## Session Outcomes

- `GET /api/users/me`, `PATCH /api/users/me`, `DELETE /api/users/me` fully implemented
- Cookie helpers centralized in `app/core/cookies.py`
- `username` uniqueness enforced at service level with 409 `USERNAME_TAKEN`
- All ruff checks pass; import verified in running Docker container
- Phase 1 Foundation complete — ready to move to Phase 2 (Wishlist CRUD)
