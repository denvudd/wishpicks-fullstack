# Saved Wishlists & Items (Web)

## Description

Implemented the full frontend for Phase 3 saved/copy features:
- **WishlistCard redesign** — image grid (0/1/2/3+ preview images), hover overlay with bookmark button, footer with title + item count, `href` prop for context-aware navigation
- **Save wishlist** — bookmark button on public wishlist page header; auth gate (UToast) for unauthenticated users; `isSaved` state populated on mount via `fetchWishlists()`
- **Saved wishlists tab** — second tab on dashboard ("Збережені"), URL query sync (`?tab=saved`), lazy fetch on tab activate, empty state, optimistic unsave
- **Copy wish item** — "Додати" hover button on public ItemCard (authenticated users only); `CopyItemModal` with item preview, wishlist select (pre-selects first), priority picker, notes textarea, toast on success
- **Anonymous reservation fix** — `onReserve` was calling the API directly without a name, causing NAME_REQUIRED 422 silently; replaced with `SharedReservationModal` which handles name collection, auth gate, and registered-only prompt

---

## Session Log

### Types (`apps/web/types/api.ts`)

- Added `preview_images: string[]` to `WishlistResponse`
- Added `SavedWishlistResponse` — id, title, description, visibility, slug, cover_url, item_count, preview_images, owner_display_name, saved_at
- Added `SavedItemResponse` — item_id, wishlist_id, title, image_url, images, product_url, price_min, price_max, currency, saved_at
- Added `CopyItemRequest` — wishlist_id, priority?, notes?

### i18n

- Added `saved.*` key group to `apps/web/locales/uk.json` and `apps/web/locales/en.json`: save, saved, unsave, add, tab_my, tab_saved, empty_wishlists_title/body, copy_modal_title, copy_wishlist_label, copy_priority_label, copy_notes_label, copy_submit, copy_submitting, copy_success, copy_no_wishlists, save_guest_prompt, cannot_save_own, errors.unknown

### API composable (`apps/web/composables/api/useSavedApi.ts`) — created

- `listWishlists(limit?, offset?)` — `GET /api/saved/wishlists`
- `saveWishlist(id)` — `POST /api/saved/wishlists/:id`
- `unsaveWishlist(id)` — `DELETE /api/saved/wishlists/:id`
- `listItems(limit?, offset?)` — `GET /api/saved/items`
- `copyItem(sourceItemId, body)` — `POST /api/saved/items/:id`
- `unsaveItem(sourceItemId)` — `DELETE /api/saved/items/:id`

### Store (`apps/web/stores/useSavedStore.ts`) — replaced stub

- State: `wishlists`, `wishlistIds: Set<string>`, `items`, `wishlistsTotal`, `itemsTotal`, `status`
- `wishlistIds` Set for O(1) `isSaved` lookup
- Actions: `setWishlists` (rebuilds Set), `addWishlist`, `removeWishlist`, `setItems`, `setStatus`

### Composable (`apps/web/composables/useSaved.ts`) — created

- `isSaved(wishlistId)` — O(1) via store Set
- `fetchWishlists()` — deduplicates if already loading
- `saveWishlist(id)` — calls API + `store.addWishlist`; catches 403 → toast "Не можна зберегти власний"
- `unsaveWishlist(id)` — optimistic: removes from store immediately, refetches on failure
- `toggleWishlist(id)` — isSaved → unsave, else save
- `fetchItems()`, `copyItem()`, `unsaveItem()`

### WishlistCard (`apps/web/components/wishlist/WishlistCard.vue`) — replaced

- Props: `wishlist: WishlistResponse | SavedWishlistResponse`, `canSave?: boolean`, `isSaved?: boolean`, `href?: string`
- Emits: `save`, `unsave`
- Image grid: 0 images → gift icon; 1 → full cover; 2 → grid-cols-2; 3+ → left full-height + right stacked 2
- Hover overlay (v-if="canSave"): bookmark icon button, top-right corner
- Footer: title (line-clamp-2) + item count
- Navigation: `href` prop overrides default `/w/:slug`; dashboard passes `/wishlists/:id`

### CopyItemModal (`apps/web/components/saved/CopyItemModal.vue`) — created

- Item preview (image thumb + title + price)
- USelect for target wishlist (pre-selects first option on open)
- Priority picker (reuses `ItemsItemPriorityPicker`)
- Notes textarea
- Error UAlert, loading submit button
- `watch(open, ..., { immediate: true, flush: 'sync' })` — ensures `fetchList()` + `setStatus('loading')` runs synchronously before first render, avoiding false "no wishlists" flash when component mounts with `open` already `true`
- `watch(wishlistOptions)` — sets first option when wishlists arrive asynchronously

### ItemCard (`apps/web/components/shared/ItemCard.vue`) — modified

- Added `group` class to root div
- Added `copy: [item: SharedItemResponse]` emit
- Added hover overlay with "Додати" button (authenticated only)
- `@click.stop` on both overlay wrapper and UButton to prevent click bubbling to card's `@click="$emit('open', item)"`

### Dashboard (`apps/web/pages/dashboard.vue`) — replaced

- `UTabs` with two items: `saved.tab_my` / `saved.tab_saved`
- `activeTab` synced with `?tab=saved` URL query param
- "My wishlists" tab: existing grid with `href="/wishlists/:id"` on WishlistCard
- "Saved" tab: lazy `fetchWishlists()` on activate; skeleton; empty state; WishlistCard with `canSave=true`, `isSaved=true`, `@unsave`

### Public wishlist page (`apps/web/pages/w/[slug]/index.vue`) — modified

- Save button in header: bookmark icon + label; authenticated → `toggleWishlist`; unauthenticated → UToast with login link
- `fetchWishlists()` called in `onMounted` if authenticated (ensures `isSaved` state is correct even on direct navigation)
- `@copy` emit on `SharedItemCard` → opens `SavedCopyItemModal`
- `SharedReservationModal` wired up (was missing — see fixes below)

### Anonymous reservation fix

- **Bug:** `onReserve` called `reservationsApi.reserve(item.id)` directly with no name → backend returns 422 NAME_REQUIRED for anonymous wishlists; error was silently swallowed
- **Fix:** `onReserve` now sets `reserveItem` + `reserveOpen = true`; `SharedReservationModal` handles name collection (already existed and had correct logic), auth gate, and registered-only prompt
- `onReserved(itemId, anonToken)` updates `displayItems` and saves `anonToken` to `reservationStore`

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| `wishlistIds: Set<string>` in store | O(1) `isSaved` check | WishlistCard bookmark state read on every render; linear scan would be costly |
| Optimistic unsave | Remove from store immediately, refetch on API failure | Instant UI feedback; failure is rare |
| `href` prop on WishlistCard | Dashboard passes `/wishlists/:id`, everywhere else uses `/w/:slug` | Same card component used in two navigation contexts |
| `watch(open, ..., { immediate: true, flush: 'sync' })` in CopyItemModal | Ensures fetch runs before first render | Component mounts with `open` already `true` (parent sets `copyModalItem` then `copyOpen = true` synchronously); non-immediate watch would never fire for the initial value |
| `@click.stop` on both overlay div and UButton | Belt-and-suspenders | UButton renders a native `<button>`; stop on wrapper div catches bubbling, stop on UButton ensures the copy emit doesn't re-trigger the card's open handler |
| Anonymous reservation via ReservationModal | Open existing modal instead of inline API call | ReservationModal already had the name prompt UI; the page was bypassing it entirely |
