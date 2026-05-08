# Wishlist Management (Web)

## Description

Implemented the full wishlist management frontend in Nuxt 3: store, composables, API layer, components (cards, empty state, create modal, settings modal), and pages (dashboard grid, detail page). Followed up with a UI pass replacing USlideover with UModal/UDrawer and maximising Nuxt UI component usage throughout.

## Session Log

### Types

1. Extended `apps/web/types/api.ts` with wishlist-related types:
   - `WishlistVisibility`, `ReservationMode`, `EventType` union types
   - `WishlistResponse`, `WishlistInviteResponse`, `WishlistCreateBody`, `WishlistUpdateBody` interfaces
   - `ApiFetchError` interface for typed error handling

### Store

2. Replaced `apps/web/stores/useWishlistStore.ts`:
   - State: `wishlists[]`, `current`, `total`, `status` (`'idle' | 'loading' | 'error'`)
   - Actions: `setList`, `setCurrent`, `prependOne`, `updateOne`, `removeOne`, `setStatus`

### API composable

3. Created `apps/web/composables/api/useWishlistsApi.ts`:
   - Wraps `apiFetch` for all wishlist endpoints: `list`, `create`, `get`, `update`, `remove`, `listInvites`, `createInvite`, `deleteInvite`

### Business logic composable

4. Created `apps/web/composables/useWishlists.ts`:
   - Mirrors the `useAuth` → `useAuthApi` pattern (pages never call `useWishlistsApi` directly)
   - Owns a local `invites` ref per call — not in the store (invites are per-modal session)
   - `fetchOne` returns `null` on 403/404 so the detail page can redirect gracefully
   - `fetchInvites`, `addInvite`, `removeInvite` manage the local `invites` ref

### Components

5. Created `apps/web/components/wishlist/WishlistCard.vue`:
   - `UCard` + `UBadge` (visibility), item count via i18n pluralisation, event date/type

6. Created `apps/web/components/wishlist/WishlistEmptyState.vue`:
   - `UIcon` + descriptive text + `UButton` emitting `create`

7. Created `apps/web/components/wishlist/WishlistCreateModal.vue`:
   - `UModal` on desktop, `UDrawer` on mobile (resolved via `resolveComponent`)
   - `URadioGroup` for visibility and reservation mode options
   - `#body` + `#footer` slots; `title` prop for the header

8. Created `apps/web/components/wishlist/WishlistSettingsModal.vue`:
   - Same UModal/UDrawer wrapper
   - Three-tab layout (basic, access, booking) using `UTabs`
   - `URadioGroup` for visibility (access tab) and reservation mode (booking tab)
   - `USeparator` before delete zone
   - Invite list with revoke buttons; copy-link button for non-private wishlists
   - Watches `open` to prefetch invites when wishlist is already private

### Pages

9. Updated `apps/web/pages/dashboard.vue`:
   - Grid of `WishlistCard` components; `WishlistEmptyState` when empty
   - `USkeleton` for loading state (replaces custom animated divs)
   - `WishlistCreateModal` triggered by header button

10. Created `apps/web/pages/wishlists/[id]/index.vue`:
    - `fetchOne` on mount; redirects to dashboard on 403/404
    - Header with title, event info, and settings button → `WishlistSettingsModal`
    - `USkeleton` for loading state

11. Added redirect stubs:
    - `apps/web/pages/wishlists/new.vue` → `/dashboard`
    - `apps/web/pages/wishlists/[id]/settings.vue` → `/wishlists/:id`

### i18n

12. Added `wishlists.*` keys to both `locales/uk.json` and `locales/en.json`:
    - `title`, `new`, `empty_title`, `empty_body`, `items_count` (pluralised)
    - `create.*`, `visibility.*` (with descriptions), `reservation.*` (with descriptions)
    - `settings.*` (all three tabs + fields), `event_type.*`, `errors.*`

## Session Outcomes

- Full wishlist CRUD UI: create via modal on dashboard, view detail page, edit/delete via settings slideover
- Visibility management with invite system for private wishlists
- Responsive modal strategy: UModal on desktop, UDrawer on mobile
- i18n complete for both Ukrainian and English

## Lessons Learned

- `<component :is="'UModal'">` with a string name silently fails in Nuxt — Nuxt auto-import does not globally register components in the Vue component registry. Always use `resolveComponent('UModal')` at setup time when dynamic component selection is needed.
- `URadioGroup` items use `description` key (not `desc`) for the secondary line — matches the `descriptionKey` prop default.
- Both `UModal` and `UDrawer` share the same slot API (`#body`, `#footer`, `title` prop) — a single template works for both once the component reference is resolved correctly.
