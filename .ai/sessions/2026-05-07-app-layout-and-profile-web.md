# App Layout + User Profile (Web)

## Description

Implemented the authenticated app shell (layout, header, sidebar) and the `/profile` page on the Nuxt 3 frontend. Also added auto-generated username at registration on the backend, a public profile page at `/u/[username]`, stub pages for reserved/settings, and a custom animated color-mode toggle component.

## Session Log

### Backend — auto-generate username at registration

1. Added `_generate_username_from_email(email)` helper in `apps/api/app/services/auth.py`:
   - Derives a prefix from the email local-part (`re.sub` to keep `[a-z0-9_]`, truncated to 20 chars)
   - Appends a 4-digit random suffix
   - Retries up to 5 times on collision; leaves `username=None` if all collide

2. Modified `register()` to call the helper and assign `username` before `User(...)` creation.

### Frontend — composables

3. Created `apps/web/composables/api/useUsersApi.ts`:
   - `updateProfile(body)` → `PATCH /api/users/me` via `apiFetch`, returns `AuthUser`

4. Created `apps/web/composables/useUsers.ts` (root-level, auto-imported):
   - Wraps `useUsersApi` and calls `store.setUser(updated)` after a successful update
   - Mirrors the `useAuth` → `useAuthApi` pattern; pages never call `useUsersApi` directly

### Frontend — Nuxt layout fix

5. Updated `apps/web/app.vue` to wrap `<NuxtPage>` with `<NuxtLayout>`:
   - Without this, named layouts declared in `definePageMeta` are silently ignored

### Frontend — layouts/app.vue

6. Created `apps/web/layouts/app.vue`:
   - Desktop (`lg+`): sticky `AppHeader` + always-visible `aside` (w-56) + `<slot>`
   - Mobile/tablet (`< lg`): hamburger in header triggers `USlideover` (side="left") containing `AppSidebar`
   - `AppSidebar` emits `navigate` to close the drawer on link click

### Frontend — AppHeader

7. Created `apps/web/components/layout/AppHeader.vue`:
   - Left: hamburger `UButton` (hidden on `lg+`) + logo `NuxtLink`
   - Right: `UiColorModeToggle` + `UDropdownMenu` with `UAvatar` trigger
   - Dropdown: Settings (`/settings`) and Logout (calls `useAuth().logout`)

### Frontend — AppSidebar

8. Created `apps/web/components/layout/AppSidebar.vue`:
   - 5 nav links: Collections (`/dashboard`), Interesting (`/saved`), Profile (`/profile`), Reserved (`/reserved`), Settings (`/settings`)
   - Active state via `useRoute` comparison; emits `navigate` on each click

### Frontend — pages

9. Replaced `apps/web/pages/profile.vue`:
   - `definePageMeta({ layout: 'app', middleware: 'auth', ssr: false })`
   - Editable display name with `isDirty` save button (calls `useUsers().updateProfile`)
   - Read-only `@username`; avatar placeholder
   - Share button: copies `window.location.origin + /u/ + username` to clipboard
   - Stub sections: "My wishlists" and "Wish board"

10. Created `apps/web/pages/u/[username].vue`:
    - Public, no auth, no layout (`definePageMeta({ ssr: false })`)
    - Shows `@username`, stub sections, `useSeoMeta` title

11. Created `apps/web/pages/reserved.vue` and `apps/web/pages/settings.vue` as stubs (`layout: 'app'`, `middleware: 'auth'`)

12. Updated `pages/dashboard.vue` and `pages/saved.vue` to declare `layout: 'app'`

### Frontend — ColorModeToggle

13. Created `apps/web/components/ui/ColorModeToggle.vue`:
    - 2-state cycle: dark ↔ light (system preference treated as dark)
    - Animated icon swap via `<Transition name="wp-spinner" mode="out-in">` reusing existing `wp-spin-in`/`wp-spin-out` keyframes from `main.css`
    - Hover rotation effect (`transform: rotate(18deg)`)
    - `<ClientOnly>` wrapper with static fallback (avoids SSR hydration mismatch)
    - `aria-label` changes with state via i18n keys

14. Replaced `UColorModeButton` in `AppHeader.vue` with `<UiColorModeToggle />`

15. Replaced inline theme toggle block in `pages/index.vue` with `<UiColorModeToggle />`; removed now-unused `colorMode` ref and scoped styles

### Frontend — i18n

16. Added `theme.*` keys (`switch_to_light`, `switch_to_dark`, `switch_to_system`) to both `locales/uk.json` and `locales/en.json`
17. Added `profile.edit` and `profile.cancel` keys (added by linter pass)

## Session Outcomes

- Authenticated app shell fully working: header + collapsible sidebar + named Nuxt layout
- `/profile` page: display name edit, share profile link, stub sections
- `/u/[username]` public profile page
- Stub pages for `/reserved` and `/settings`
- Custom animated `UiColorModeToggle` used in both the app header and landing page
- Auto-generated username on registration
- `<NuxtLayout>` fix ensures named layouts work across all pages

## Lessons Learned

- Nuxt 3 requires `<NuxtLayout>` in `app.vue`; omitting it causes named layouts to silently not apply — no error, just `<slot>` rendered directly.
- Nuxt auto-import only scans the root `composables/` directory, not subdirectories like `composables/api/`. Composables in subdirs must be explicitly imported from a root-level wrapper (follow the `useAuth` → `useAuthApi` pattern).
- Auth-gated pages that use `window`/`navigator` APIs should set `ssr: false` in `definePageMeta` to avoid SSR serialization errors.
