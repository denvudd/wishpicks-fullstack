# URL Parser (Web)

## Description

Implemented the frontend for the URL parser flow. When a user pastes a product URL into the entry modal, the modal transitions through scanning → success → form states in-place, then opens the item form pre-filled with scraped data (title, description, image, price, currency).

---

## Session Log

### Types

- Modified `apps/web/types/api.ts`:
  - Added `ParseUrlData` interface: `title`, `description`, `image_url`, `price` (string | null, Decimal serialised as string), `currency`, `product_url`

### API composable

- Modified `apps/web/composables/api/useItemsApi.ts`:
  - Added `parseUrl(url: string): Promise<ParseUrlData>` — `POST /api/items/parse-url`

### i18n

- Modified `apps/web/locales/en.json` and `apps/web/locales/uk.json`:
  - Added `items.scanning` group: `title`, `success`, `success_body`, `error`, `error_body`, `proceed`
  - Removed `items.entry_url_note` (no longer used)

### Entry modal (`ItemEntryModal.vue`)

- Rewrote `apps/web/components/items/ItemEntryModal.vue` to handle scanning in-place:
  - Added `parseUrlFn?: (url: string) => Promise<ParseUrlData>` prop
  - Internal `phase` state: `'idle' | 'scanning' | 'success' | 'error'`
  - When URL submitted with `parseUrlFn` present: stays open, transitions through phases
  - `idle` → spinner + hostname (scanning), → check icon (success, 800 ms), → modal closes, emits `proceed` with `parsedData`
  - On error: shows error state with "Continue" button that closes and emits `proceed` without data
  - `proceed` emit extended: `{ title, productUrl, parsedData?: ParseUrlData | null }`
  - `Transition mode="out-in"` with tw-animate-css classes between phases
  - Modal is non-dismissible during scanning/success phases
  - `reset()` restores idle state on close

### Scanning modal (created but superseded)

- Created `apps/web/components/items/ItemUrlScanningModal.vue` — standalone scanning modal originally intended to sit between entry and form modals
- Superseded by in-place scanning in `ItemEntryModal` due to Nuxt UI overlay conflicts when two modals open/close in rapid succession; file retained but unused

### Form modal (`ItemFormModal.vue`)

- Modified `apps/web/components/items/ItemFormModal.vue`:
  - Added `initialParsedData?: ParseUrlData | null` prop
  - In `resetFormForCreate`: pre-fills `title`, `description`, `image_url`, `price_min`/`price_max`, `currency` from `initialParsedData` when present

### Wishlist page (`pages/wishlists/[id]/index.vue`)

- Modified `apps/web/pages/wishlists/[id]/index.vue`:
  - Added `ParseUrlData` import, `useItemsApi` composable
  - Added `parsedData` ref to carry scanned data from entry modal to form modal
  - Simplified `onEntryProceed` to sync: receives `parsedData` from emit, sets `formOpen = true`
  - `onEditItem` resets `parsedData = null` (edit flow bypasses scanning)
  - Passes `:parse-url-fn="itemsApi.parseUrl"` to `ItemsItemEntryModal`
  - Passes `:initial-parsed-data="parsedData"` to `ItemsItemFormModal`

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Scanning state location | Inside `ItemEntryModal`, not a separate modal | Nuxt UI overlay system conflicts when one modal closes and another opens immediately; in-place transitions avoid the issue entirely |
| Separate `ItemUrlScanningModal` | Created but unused | Was the original plan; replaced after discovering the overlay conflict; kept in case the pattern is useful later |
| Success display duration | 800 ms | Long enough to register visually; short enough not to feel sluggish |
| Non-dismissible during scan | `dismissible="phase === 'idle'"` | Prevents accidental close while the async request is in flight |
| Parsed data flow | Entry modal emits `parsedData` → page stores it → form modal reads as `initialParsedData` | Keeps API calls out of the form modal; form modal remains a pure presentational form |
| Error path | Shows error state, "Continue" button opens form empty | Parse failure is non-fatal; user can fill manually |
