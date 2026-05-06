# Email Verification 

## Description

Implemented the email verification.

## Session Log

### Bug Fix — OTP service Redis guard

1. Verified a reported bug: `generate_and_store_otp`, `verify_otp`, and `check_and_set_cooldown` in `app/services/otp.py` call Redis methods directly without checking if `redis is None`. `get_redis()` can return `None` on connection failure, causing `AttributeError`. Existing code elsewhere (e.g. `refresh_tokens`) already has `if redis:` guards; the new OTP functions lacked them.

2. Fixed with per-function degradation logic:
   - `generate_and_store_otp`: raises `RuntimeError("Redis unavailable")` — registration flow wraps this in try/except, so it degrades gracefully
   - `verify_otp`: raises `OTPInvalidError` — user gets a `400 OTP_INVALID`, which is the correct response when the stored code cannot be retrieved
   - `check_and_set_cooldown`: returns early (skips enforcement) — allows resend to proceed rather than blocking the user when Redis is down

### Frontend — Email Verification

3. Added `is_email_verified: boolean` to `AuthUser` interface in `stores/useAuthStore.ts`.

4. Added `verifyEmail(code: string): Promise<AuthUser>` and `resendVerification(): Promise<void>` to `composables/api/useAuthApi.ts` — mapping to `POST /api/auth/verify-email` and `POST /api/auth/resend-verification` respectively.

5. Updated `composables/useAuth.ts`:
   - `register()` now checks `user.is_email_verified` after registration; redirects to `/auth/verify-email` if false, `/dashboard` if true (Google OAuth users land on dashboard directly)
   - Added `verifyEmail(code)` — calls API, updates store, navigates to `/dashboard`
   - Added `resendVerification()` — delegates to API, no store update needed

6. Added locale keys to both `locales/en.json` and `locales/uk.json`:
   - `auth.verify_email.*` block (title, subtitle, instructions, code, submit, resend, resend_cooldown, resend_success, no_code, skip)
   - New error codes: `OTP_INVALID`, `OTP_MAX_ATTEMPTS`, `RESEND_COOLDOWN`, `EMAIL_ALREADY_VERIFIED`

7. Created `pages/auth/verify-email.vue`:
   - `definePageMeta({ middleware: 'auth' })` — unauthenticated users redirected to `/login`
   - `onMounted` guard: if `store.user.is_email_verified` is already true → redirect to `/dashboard` (handles direct URL access)
   - OTP input field (`inputmode="numeric"`, `maxlength="6"`, `autocomplete="one-time-code"`)
   - Submit handler: calls `verifyEmail(form.code)`, shows error on `OTP_INVALID` / `OTP_MAX_ATTEMPTS`
   - Resend button with 60-second client-side countdown timer (`setInterval`), cleaned up in `onUnmounted`
   - Success alert on resend
   - "Continue without verifying" skip link to `/dashboard`


## Session Outcomes

- OTP Redis guard bug fixed in `apps/api/app/services/otp.py`
- `POST /api/auth/verify-email` and `POST /api/auth/resend-verification` fully wired to frontend
- Email verification page functional at `/auth/verify-email`
- Registration flow redirects unverified users to verify-email page
- `<UiAlert :show="condition">` pattern established for all animated alerts — login, register, verify-email pages updated
- Locale strings complete in both `uk` and `en`

## Lessons Learned

- **Vue `<Transition>` + scoped styles**: Transition class names (`.alert-enter-active` etc.) are added dynamically by Vue without the component's scoped data-attribute, so they won't match scoped CSS selectors. Always use non-scoped `<style>` for transition classes.
