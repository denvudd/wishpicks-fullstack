# Settings Page (Web)

## Description

Implemented the full user settings page: avatar upload with local preview, display_name and username editing, single Save action. Avatar upload goes through Cloudinary via the new `useMediaApi` composable. Extended existing composables to support `avatar_url`. Polished micro-animations on avatar preview and hover overlay.

---

## Changes

### New — `apps/web/composables/api/useMediaApi.ts`

- `uploadImage(file: File, folder: string): Promise<string>`
  - Builds `FormData` with `file` and `folder` fields
  - Calls `POST /api/media/upload` via `apiFetch`
  - Returns `secure_url` string from the response
- **Must be explicitly imported** — Nuxt does not auto-import from `composables/api/` subdirectories

### Modified — `apps/web/composables/api/useUsersApi.ts`

- Added `avatar_url?: string | null` to the `updateProfile` body type

### Modified — `apps/web/composables/useUsers.ts`

- Added `avatar_url?: string | null` to the `updateProfile` body type

### Replaced — `apps/web/pages/settings.vue`

Full settings page replacing the stub. All form state is inline (no separate composable needed for a form this small).

**Layout:** narrow centered card (`max-w-lg`), no tabs. Top-down: page heading + email subtitle → avatar block → display_name / username fields → Save button footer.

**Avatar block:**
- 80px circle, shows current `avatar_url` from store, or local `ObjectURL` preview after file pick, or initials fallback
- Click on circle or "Змінити фото" caption → triggers hidden `<input type="file" accept="image/jpeg,image/png,image/webp">`
- On file pick: `URL.createObjectURL()` for instant preview, `pendingFile` ref set, Save button activates
- Hover → camera icon overlay (opacity transition 150ms)
- New avatar preview: scale(0.9)→scale(1) + opacity 0→1 via Vue `<Transition name="wp-avatar">`, 200ms ease-out

**Form refs:**
- `form.display_name`, `form.username` — reactive, initialized from store
- `pendingFile: File | null` — selected file not yet uploaded
- `previewUrl: string | null` — ObjectURL for local preview
- `isDirty: computed` — true if any field differs from stored user or `pendingFile !== null`
- `isSaving: ref<boolean>`
- `usernameError: ref<string>` — inline error under username field

**Save sequence:**
1. If `pendingFile` → `mediaApi.uploadImage(pendingFile, 'avatars')` (separate try/catch — upload failure shows toast and returns early without touching other fields)
2. `users.updateProfile({ display_name, username, avatar_url? })` — `avatar_url` only included if upload happened
3. Success → revoke ObjectURL, clear `pendingFile`/`previewUrl`, success toast
4. `USERNAME_TAKEN` (409) → inline error under username field (no toast)
5. Other errors → generic error toast

**Memory leak guard:** `onBeforeUnmount` calls `URL.revokeObjectURL(previewUrl)` to clean up any pending local preview.

**User store sync:** `watch(user)` resets `form` fields whenever the store updates (after save or external change), guarded by `!isSaving` to avoid overwriting during in-flight requests.

### Modified — `apps/web/locales/uk.json` and `apps/web/locales/en.json`

Added `settings.*` section:

| Key | UK | EN |
|---|---|---|
| `settings.title` | Налаштування | Settings |
| `settings.avatar_label` | Фото профілю | Profile photo |
| `settings.avatar_change` | Змінити фото | Change photo |
| `settings.display_name` | Імʼя | Name |
| `settings.username` | Username | Username |
| `settings.save` | Зберегти зміни | Save changes |
| `settings.saving` | Збереження… | Saving… |
| `settings.saved` | Зміни збережено | Changes saved |
| `settings.errors.upload_failed` | Не вдалося завантажити фото | Failed to upload photo |
| `settings.errors.unknown` | Щось пішло не так | Something went wrong |
| `settings.errors.USERNAME_TAKEN` | Цей username вже зайнятий | This username is already taken |

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Form state location | Inline in `settings.vue` | Form is small; separate composable would be over-engineering |
| Upload vs save coupling | Upload first, PATCH second — separate try/catch | Allows specific "upload failed" error without conflating with profile save errors |
| `avatar_url` in PATCH | Only sent if upload happened | Avoids overwriting existing avatar when only text fields change |
| Avatar preview | `URL.createObjectURL` + Vue Transition | Instant local preview without a round-trip; memory cleaned up on unmount |
| USERNAME_TAKEN | Inline field error, not toast | Inline is more actionable — user sees exactly which field is wrong |
