# Wish Item Management (Web)

## Description

Implemented the full wish item frontend: types, store, API/business composables, six components (card, empty state, entry modal, form modal, detail modal, share modal), updated wishlist detail page, and a standalone share-link page that opens the detail modal by default.

## Session Log

### Types

1. Extended `apps/web/types/api.ts`:
   - `ItemPriority` type alias (`0 | 1 | 2`)
   - `WishItemResponse`, `WishItemCreateBody`, `WishItemUpdateBody` interfaces

### Store

2. Created `apps/web/stores/useItemStore.ts`:
   - State: `items[]`, `total`, `status` (`'idle' | 'loading' | 'error'`)
   - Actions: `setItems`, `appendOne`, `updateOne`, `removeOne`, `setStatus`, `clear`

### API composable

3. Created `apps/web/composables/api/useItemsApi.ts`:
   - `getOne(itemId)` — `GET /api/items/:id`
   - `list(wishlistId)` — `GET /api/wishlists/:id/items`
   - `create(wishlistId, body)` — `POST /api/wishlists/:id/items`
   - `update(itemId, body)` — `PATCH /api/items/:id`
   - `remove(itemId)` — `DELETE /api/items/:id`
   - `updatePosition(itemId, position)` — `PATCH /api/items/:id/position`

### Business logic composable

4. Created `apps/web/composables/useItems.ts`:
   - Pages never call `useItemsApi` directly (mirrors `useWishlists` pattern)
   - `fetchOne` — wraps `api.getOne`, returns `null` on error
   - `fetchList` — loads items into store
   - `createItem`, `updateItem`, `removeItem` — mutate store after API call
   - `clear` — resets store on page unmount

### Components

5. Created `apps/web/components/items/ItemEmptyState.vue`:
   - Empty state with icon and "Add wish" button, emits `create`

6. Created `apps/web/components/items/ItemCard.vue`:
   - Image area with hover overlay (opacity-0 → opacity-100 on group-hover)
   - Overlay: `UDropdownMenu` (Edit / Copy / Share / Delete) + share button top-left; store link top-right; "Fulfill" button + priority dropdown bottom
   - Priority shown as emoji: `{ 0: '🙂', 1: '🥰', 2: '😍' }`
   - Inline priority change via `UDropdownMenu` — no modal needed
   - Body: title (line-clamp-2) + store domain link + price range row
   - Emits: `edit`, `delete`, `copy`, `share`, `fulfill`, `update-priority`

7. Created `apps/web/components/items/ItemEntryModal.vue`:
   - Step 1 of item creation: detects pasted URL vs plain title
   - Emits `proceed({ title, productUrl })` to open the full form

8. Created `apps/web/components/items/ItemFormModal.vue`:
   - Full create/edit form with `UCollapsible` advanced section
   - Custom pill-style priority picker with emoji labels
   - Price mode toggle: single price vs range
   - Tags as comma-separated input
   - Emits `saved` and `deleted`

9. Created `apps/web/components/items/ItemDetailModal.vue`:
   - 12-col grid: left = image + priority badge; right = title, relative time, price, description (line-clamp-2 + show more), tags, fulfill section with store link
   - `UModal` on desktop, `UDrawer` on mobile
   - `isMobile` resolved synchronously at setup time (not in `onMounted`) to prevent component switch from emitting `update:open=false`
   - Relative time via `Intl.RelativeTimeFormat` (no external dependency)

10. Created `apps/web/components/items/ItemShareModal.vue`:
    - Share URL: `${window.location.origin}/wishlists/:wishlistId/wish/:itemId`
    - Copy to clipboard with 2s "Copied" feedback
    - Social share buttons: Telegram, WhatsApp, X, Facebook (open in popup)

### Pages

11. Updated `apps/web/pages/wishlists/[id]/index.vue`:
    - Items grid with masonry/grid layout toggle
    - `ItemEmptyState`, `ItemCard` (grid + masonry variants)
    - Share flow: `onShareItem` → `ItemShareModal`
    - Inline priority update: `onUpdatePriority` → `useItems.updateItem`
    - Two-step create flow: `ItemEntryModal` → `ItemFormModal`
    - Edit/delete: `ItemFormModal` with `editingItem` pre-filled

12. Created `apps/web/pages/wishlists/[id]/wish/[itemId].vue`:
    - Standalone page for share links — renders full wishlist UI
    - Fetches wishlist + items on mount, then fetches target item via `GET /api/items/:id`
    - Opens `ItemDetailModal` by default once item is loaded
    - Closing the modal leaves the user on the wishlist (no redirect)

### i18n

13. Added `items.*` keys to `locales/uk.json` and `locales/en.json`:
    - CRUD labels: `add`, `edit`, `copy`, `share`, `delete`, `fulfill`
    - Priority: `priority.normal`, `priority.high`, `priority.must_have`
    - Form fields: all input labels + placeholders
    - Share modal: `share_title`, `share_copy_link`, `share_link_copied`, `share_via`
    - Detail modal: `show_more`, `show_less`, `fulfill_question`, `open_store`
    - Empty state, loading, error strings

## Session Outcomes

- Full wish item CRUD UI with two-step creation flow
- Card hover overlay with inline priority change (no modal)
- Share link flow: `/wishlists/:id/wish/:itemId` opens full wishlist page with detail modal
- Responsive modals: UModal desktop / UDrawer mobile
- i18n complete for Ukrainian and English

## Lessons Learned

- `isMobile` must be resolved synchronously at component setup time, not in `onMounted`. Setting it reactively causes `UModal` → `UDrawer` component swap which emits `update:open=false` and closes the modal immediately on first render.
- Composables in `composables/api/` subdirectory are **not** auto-imported by Nuxt. Pages should only import from top-level `composables/` (e.g. `useItems`, not `useItemsApi` directly).
- `UDropdownMenu` items are structured as an array of arrays (groups), each item needs `label` and `onSelect`.
