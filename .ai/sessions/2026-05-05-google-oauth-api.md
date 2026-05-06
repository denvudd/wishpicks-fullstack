# Google OAuth — Full Implementation (API + Web)

## Description

Implemented Google OAuth login flow end-to-end: FastAPI backend handles the full code exchange and cookie issuance; the Nuxt frontend had most of the UI pre-built, the only missing piece was surfacing the `?error=oauth_failed` redirect on the login page.

## Session Log

### API

1. Created `app/services/google_oauth.py` — `get_google_auth_url()` builds the consent screen URL; `exchange_code_for_profile(code)` exchanges the authorization code for a Google userinfo profile via httpx; `upsert_google_user(db, profile)` applies 3-step upsert: match by `google_id` → match by email (links `google_id` to existing account) → create new Google-only account (no `password_hash`).

2. Added `google_login(db, code)` to `app/services/auth.py` — orchestrates the google_oauth service + existing `_issue_tokens`, follows the same return shape `(user, access_token, refresh_token)` as `register` and `login`.

3. Added `GET /api/auth/google` and `GET /api/auth/google/callback` to `app/routers/auth.py`. The callback redirects to `{FRONTEND_URL}/dashboard` on success with JWT HTTP-only cookies set, or to `{FRONTEND_URL}/login?error=oauth_failed` on any failure (missing code, Google error param, exchange failure). Rate limit: 10/minute/IP.

4. Discovered that `docker restart` does not re-read `env_file` — must use `docker compose up -d --force-recreate api` to pick up `.env` changes.

### Web

5. The frontend was already ~95% built: Google buttons on login/register pages, `loginWithGoogle()` composable, `googleAuthUrl()` API method, `/auth/google/callback` loading page, and all translations existed. `GOOGLE_REDIRECT_URI` points to the backend (`localhost:8000/api/auth/google/callback`), so the backend owns the full OAuth exchange and redirects the browser to `/dashboard` directly — the frontend callback page is not in the active redirect path.

6. The only missing piece: `pages/login.vue` did not read the `?error` query param, so users who denied access on Google's consent screen were silently redirected to `/login` with no feedback. Fixed by initialising `errorCode` from `route.query.error` via `useRoute()`.

7. Added `auth.errors.oauth_failed` to `locales/en.json` ("Google sign-in failed. Please try again.") and `locales/uk.json` ("Вхід через Google не вдався. Спробуй ще раз.").

## Session Outcomes

- `GET /api/auth/google` and `GET /api/auth/google/callback` fully functional
- Smoke tested with real Google credentials — redirect URL contains correct `client_id`
- Error fallbacks verified: missing code and `error=access_denied` both redirect to `/login?error=oauth_failed`
- `ruff check` passes on all modified API files
- Login page now surfaces `oauth_failed` error message in both locales when Google auth is denied or fails

## Lessons Learned

- **`docker restart` vs `--force-recreate`**: `restart` keeps the existing environment snapshot; `env_file` changes only take effect after `docker compose up --force-recreate`.
- **Frontend OAuth callback page vs direct dashboard redirect**: `GOOGLE_REDIRECT_URI` points to the backend, so the backend sets cookies and redirects the browser to `/dashboard` directly. The `/auth/google/callback` Nuxt page exists but is not in the active flow — `auth.client.ts` plugin calls `initialize()` on every page load, so landing on `/dashboard` with cookies already set works correctly.
