# Wish Item Extra Images (Web)

## Description

Extended wish item UI to support up to 5 additional images. `ItemFormModal` gains a drag-and-drop image grid in the Advanced collapsible. `ItemCard` renders up to 3 images in an organic CSS grid. `ItemDetailModal` shows a swipeable `UCarousel` with a clickable thumbnail strip when multiple images are present.

---

## Session Log

### Dependency

- Modified `apps/web/package.json`:
  - Added `"vue-draggable-plus": "^0.6.1"` — SortableJS-based drag-and-drop for Vue 3; **not auto-imported**, must be explicitly imported as `import { VueDraggable } from 'vue-draggable-plus'`

### TypeScript types

- Modified `apps/web/types/api.ts`:
  - Added `images: string[] | null` to `WishItemResponse`
  - Added `images?: string[] | null` to `WishItemCreateBody` and `WishItemUpdateBody`

### i18n

- Modified `apps/web/locales/uk.json` and `apps/web/locales/en.json`:

| Key | UK | EN |
|---|---|---|
| `items.image_uploading` | Завантаження… | Uploading… |
| `items.advanced.images` | Зображення | Images |
| `items.advanced.images_add` | Додати зображення | Add image |
| `items.errors.image_upload_failed` | Не вдалося завантажити зображення | Failed to upload image |

### ItemCard — organic grid

- Modified `apps/web/components/items/ItemCard.vue`:
  - Added `cardImages` computed — merges `image_url` (first) + `images` array, slices to max 3
  - Template: 4 cases driven by `cardImages.length`:
    - `0` → gift icon placeholder
    - `1` → single `<img>` full-cover
    - `2` → `grid-cols-2` with equal halves
    - `3+` → `grid-cols-2` with first image spanning 2 rows (`row-span-2`), two smaller images stacked on the right

### ItemDetailModal — gallery

- Modified `apps/web/components/items/ItemDetailModal.vue`:
  - Added `carouselRef = ref()`, `activeIndex = ref(0)`, `galleryImages` computed (same merge logic as `cardImages`)
  - `watch(open)` resets `activeIndex` to `0` on open
  - `goToSlide(index)` sets `activeIndex` and calls `carouselRef.value?.emblaApi?.scrollTo(index)` — **note: Nuxt UI v4 exposes Embla as `emblaApi`, not `embla`**
  - Left column template splits on `galleryImages.length <= 1`:
    - Single/no image → existing `<img>` or gift icon (unchanged)
    - 2+ images → `UCarousel` with `@select="(i) => (activeIndex = i)"` for swipe sync + thumbnail strip below
  - Thumbnail strip: `w-14 aspect-square` buttons; active thumbnail gets `scale-105` + full-opacity border; inactive thumbnails are `opacity-50`, animate to `opacity-80 + scale-105` on hover; all via `transition-all duration-200`

### ItemFormModal — images section

- Modified `apps/web/components/items/ItemFormModal.vue`:
  - Imported `VueDraggable` from `vue-draggable-plus`
  - Added `imagesUploading = ref(false)` and `imageFilesInputRef = ref<HTMLInputElement | null>(null)`
  - Added `images: [] as string[]` to `form` reactive
  - Updated `resetFormForCreate` → `form.images = []`
  - Updated `applyFormFromItem` → `form.images = [...(item.images ?? [])]`
  - Updated `buildBody` → `images: form.images.length ? form.images : null`
  - Added `onExtraImagePick` handler — guards `>= 5`, uploads via `mediaApi.uploadImage(file, 'items')`, pushes URL to `form.images`
  - Added images section inside Advanced collapsible (after Description):
    - Hidden `<input type="file">` triggered by the card button
    - `VueDraggable` with `:animation="150"` wrapping `w-16 aspect-square` image chips
    - Each chip: `hover:scale-105`, `active:scale-95`, dark overlay on hover, `×` delete button (hover-reveal)
    - Add button: dashed-border `w-16 aspect-square` card with `+` icon (or spinner while uploading); hidden when `form.images.length >= 5`

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Write strategy | Full array sent on every save | No dedicated add/remove endpoints needed; PATCH always has the latest order |
| Drag-and-drop library | `vue-draggable-plus` | Already in the project; SortableJS under the hood, no extra setup |
| VueDraggable layout | `class="contents"` wrapper | Keeps chips and the add card in the same `flex-wrap` row without breaking alignment |
| Embla API access | `emblaApi` (not `embla`) | Nuxt UI v4 exposes the Embla instance as `emblaApi`; confirmed from official docs |
| Swipe sync | `@select` event on `UCarousel` | Cleaner than manually attaching Embla `'select'` listener; native Nuxt UI event |
| Image order in grid/gallery | `image_url` always first | Primary image is the canonical cover; extra images are supplementary |
