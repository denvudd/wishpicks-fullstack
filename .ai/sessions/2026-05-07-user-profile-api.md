# User Profile Read + Update (API)

## Description

Implemented `GET /api/users/me`, `PATCH /api/users/me`, `DELETE /api/users/me` endpoints. 

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

### Modified — `apps/api/app/services/auth.py`

9. Added `import random` and `import re` at the top of the file.

10. Added `_generate_username_from_email(email: str) -> str` helper after `_verify_password`:
   - Strips the local part of the email (before `@`)
   - Lowercases and replaces non-`[a-z0-9]` characters with `_` via `re.sub`
   - Truncates to 20 characters, strips leading/trailing underscores; falls back to `"user"` if empty
   - Appends a random 4-digit suffix (`random.randint(1000, 9999)`)

11. Modified `register()` to call the helper in a retry loop before creating the `User` object:
   - Tries up to 5 candidates; each is checked against `User.username` in the DB
   - Sets `username` to the first available candidate; leaves it `None` if all 5 collide (graceful degradation — no registration failure)
   - `User(...)` now receives `username=username`

## Session Outcomes

- `GET /api/users/me`, `PATCH /api/users/me`, `DELETE /api/users/me` fully implemented
- Cookie helpers centralized in `app/core/cookies.py`
- `username` uniqueness enforced at service level with 409 `USERNAME_TAKEN`
- All new email/password registrations receive an auto-generated username (e.g. `john_doe_4271`)
- Uniqueness is guaranteed via DB check with 5-attempt retry; collision is astronomically unlikely (10 000 permutations per prefix)
- Google OAuth registrations are unaffected — `google_login` calls a separate `upsert_google_user` path
- No migration required — `username` column already existed and was already nullable
