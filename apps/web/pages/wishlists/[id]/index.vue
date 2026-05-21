<template>
  <div class="w-full p-6">
    <!-- Loading skeleton -->
    <div v-if="wishlistLoading" class="space-y-4">
      <USkeleton class="h-7 w-48 rounded-lg" />
      <USkeleton class="h-4 w-32 rounded-lg" />
    </div>

    <template v-else-if="current">
      <div class="mb-8 flex w-full items-center justify-between gap-4">
        <div class="space-y-1">
          <h1 class="text-xl font-bold text-black dark:text-white">
            {{ current.title }}
          </h1>
          <p
            v-if="current.event_date"
            class="text-body-gray dark:text-muted-gray text-sm"
          >
            {{ current.event_date }}
            <span v-if="current.event_type">
              · {{ t(`wishlists.event_type.${current.event_type}`) }}
            </span>
          </p>
        </div>

        <div class="flex items-center gap-2">
          <UTooltip
            v-if="current.visibility !== 'private'"
            :text="
              shareLinkCopied
                ? t('wishlists.settings.link_copied')
                : t('wishlists.settings.copy_link')
            "
          >
            <UButton
              variant="outline"
              color="neutral"
              square
              :icon="
                shareLinkCopied ? 'i-heroicons-check' : 'i-heroicons-share'
              "
              class="size-8"
              :ui="{
                leadingIcon: 'size-4.5 shrink-0',
              }"
              @click="copyShareLink"
            />
          </UTooltip>
          <UButton
            color="neutral"
            icon="i-heroicons-plus"
            :label="t('items.add')"
            @click="entryOpen = true"
          />

          <UButton
            variant="outline"
            color="neutral"
            icon="i-heroicons-cog-6-tooth"
            :label="t('wishlists.settings.title')"
            @click="settingsOpen = true"
          />
        </div>
      </div>

      <div class="mb-4 flex w-full items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <UTooltip :text="t('items.filters.title')">
            <UChip
              :text="
                activeFilterCount > 0 ? String(activeFilterCount) : undefined
              "
              :show="activeFilterCount > 0"
              color="neutral"
              size="2xl"
            >
              <UButton
                variant="outline"
                color="neutral"
                icon="i-heroicons-adjustments-horizontal"
                @click="filterOpen = true"
              />
            </UChip>
          </UTooltip>

          <UButton
            v-if="activeFilterCount > 0"
            variant="ghost"
            color="neutral"
            :label="t('items.filters.clear')"
            @click="clearFilters"
          />
        </div>

        <UTooltip
          :text="
            itemsLayout === 'grid'
              ? t('wishlists.items_layout.switch_to_masonry')
              : t('wishlists.items_layout.switch_to_grid')
          "
        >
          <UButton
            v-if="!itemsLoading"
            variant="outline"
            color="neutral"
            square
            :aria-label="
              itemsLayout === 'grid'
                ? t('wishlists.items_layout.switch_to_masonry')
                : t('wishlists.items_layout.switch_to_grid')
            "
            @click="toggleItemsLayout"
          >
            <template #leading>
              <Transition
                mode="out-in"
                enter-active-class="animate-in fade-in-0 zoom-in-95 ease-out"
                leave-active-class="animate-out fade-out-0 zoom-out-95 ease-in"
              >
                <UIcon
                  :key="itemsLayout"
                  :name="
                    itemsLayout === 'grid'
                      ? 'i-heroicons-view-columns'
                      : 'i-heroicons-squares-2x2'
                  "
                  class="size-5 shrink-0"
                />
              </Transition>
            </template>
          </UButton>
        </UTooltip>
      </div>

      <!-- Active filter chips -->
      <Transition
        enter-active-class="animate-in fade-in-0 slide-in-from-top-2 duration-200 ease-out"
        leave-active-class="animate-out fade-out-0 slide-out-to-top-2 duration-150 ease-in"
      >
        <div v-if="activeFilterCount > 0" class="mb-6">
          <TransitionGroup
            tag="div"
            class="flex flex-wrap gap-2"
            enter-active-class="animate-in fade-in-0 zoom-in-95 duration-200 ease-out"
            leave-active-class="animate-out fade-out-0 zoom-out-95 duration-150 ease-in"
          >
            <UBadge
              v-if="filters.is_reserved !== null"
              key="is_reserved"
              color="neutral"
              variant="subtle"
              class="cursor-pointer"
              @click="filters.is_reserved = null"
            >
              {{
                filters.is_reserved
                  ? t('items.filters.reserved')
                  : t('items.filters.not_reserved')
              }}
              <UIcon name="i-heroicons-x-mark" class="ml-1 h-3 w-3" />
            </UBadge>

            <UBadge
              v-if="filters.is_fulfilled !== null"
              key="is_fulfilled"
              color="neutral"
              variant="subtle"
              class="cursor-pointer"
              @click="filters.is_fulfilled = null"
            >
              {{
                filters.is_fulfilled
                  ? t('items.filters.fulfilled')
                  : t('items.filters.not_fulfilled')
              }}
              <UIcon name="i-heroicons-x-mark" class="ml-1 h-3 w-3" />
            </UBadge>

            <UBadge
              v-for="p in filters.priority"
              :key="`priority-${p}`"
              color="neutral"
              variant="solid"
              class="cursor-pointer"
              @click="
                filters.priority = filters.priority.filter((x) => x !== p)
              "
            >
              {{ priorityLabel(p) }}
              <UIcon name="i-heroicons-x-mark" class="ml-1 h-3 w-3" />
            </UBadge>

            <UBadge
              v-if="filters.store !== null"
              key="store"
              color="neutral"
              variant="outline"
              class="cursor-pointer"
              @click="filters.store = null"
            >
              {{ filters.store }}
              <UIcon name="i-heroicons-x-mark" class="ml-1 h-3 w-3" />
            </UBadge>
          </TransitionGroup>
        </div>
      </Transition>

      <Transition
        mode="out-in"
        enter-active-class="animate-in fade-in-0 duration-200 ease-out"
        leave-active-class="animate-out fade-out-0 duration-150 ease-in"
      >
        <div
          v-if="itemsLoading"
          key="skeleton"
          class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4"
        >
          <USkeleton v-for="n in 4" :key="n" class="aspect-square rounded-xl" />
        </div>

        <ItemsItemEmptyState
          v-else-if="!items.length"
          key="empty"
          @create="entryOpen = true"
        />

        <div v-else :key="itemsLayout">
          <VueDraggable
            v-if="itemsLayout === 'grid'"
            v-model="draggableItems"
            :animation="250"
            handle=".drag-handle"
            drag-class="drag-clone"
            class="grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-5"
            @start="onDragStart"
            @end="onDragEnd"
          >
            <ItemsItemCard
              v-for="(item, i) in draggableItems"
              :key="item.id"
              :item="item"
              :draggable="true"
              class="animate-in fade-in-0 zoom-in-95 fill-mode-both duration-300"
              :style="{ animationDelay: `${Math.min(i * 40, 280)}ms` }"
              @select="openItemDetail"
              @edit="onEditItem"
              @delete="onDeleteItem"
              @share="onShareItem"
              @update-priority="onUpdatePriority"
              @fulfill="onFulfillItem"
            />
          </VueDraggable>
          <MasonryWall
            v-else
            :items="items"
            :column-width="220"
            :gap="16"
            :min-columns="2"
            :max-columns="5"
          >
            <template #default="{ item, index }">
              <ItemsMasonryCard
                :item="item"
                class="animate-in fade-in-0 zoom-in-95 fill-mode-both duration-300"
                :style="{ animationDelay: `${Math.min(index * 40, 280)}ms` }"
                @select="openItemDetail"
                @edit="onEditItem"
                @delete="onDeleteItem"
                @share="onShareItem"
                @update-priority="onUpdatePriority"
                @fulfill="onFulfillItem"
              />
            </template>
          </MasonryWall>
        </div>
      </Transition>

      <WishlistSettingsModal
        v-model:open="settingsOpen"
        :wishlist="current"
        @deleted="navigateTo(localePath('/dashboard'))"
      />

      <ItemsItemEntryModal
        v-model:open="entryOpen"
        :parse-url-fn="itemsApi.parseUrl"
        @proceed="onEntryProceed"
      />

      <ItemsItemShareModal
        v-if="sharingItem"
        v-model:open="shareOpen"
        :item="sharingItem"
        :slug="current?.slug"
      />

      <ItemsItemFormModal
        v-model:open="formOpen"
        :initial-title="entryResult.title"
        :initial-product-url="entryResult.productUrl"
        :initial-parsed-data="parsedData"
        :wishlist-id="current.id"
        :item="editingItem"
        @saved="onItemSaved"
        @deleted="onItemDeleted"
      />

      <ItemsItemDetailModal
        v-if="detailItem"
        v-model:open="detailOpen"
        :item="detailItem"
        @fulfill="onFulfillItem"
      />

      <ItemsItemFilterSlideover
        v-model:open="filterOpen"
        :model-value="filters"
        :available-stores="availableStores"
        @update:model-value="filters = $event"
      />

      <UModal v-model:open="deleteConfirmOpen" :title="t('items.delete')">
        <template #body>
          <p class="text-body-gray dark:text-muted-gray text-sm">
            {{ t('items.delete_confirm_body') }}
          </p>
          <div class="mt-6 flex justify-end gap-2">
            <UButton
              variant="outline"
              color="neutral"
              :label="t('items.delete_cancel')"
              @click="closeDeleteConfirm"
            />
            <UButton
              color="error"
              :loading="deleteInProgress"
              :label="t('items.delete_confirm_yes')"
              @click="confirmDeleteItem"
            />
          </div>
        </template>
      </UModal>
    </template>
  </div>
</template>

<script setup lang="ts">
import { VueDraggable } from 'vue-draggable-plus'
import { MasonryWall } from '@yeger/vue-masonry-wall'
import type { ParseUrlData, WishItemResponse, ItemFilters } from '~/types/api'
import { useItemsApi } from '~/composables/api/useItemsApi'
import { useReservationsApi } from '~/composables/api/useReservationsApi'

definePageMeta({ layout: 'app', middleware: 'auth' })

const { t } = useI18n()
const localePath = useLocalePath()
const route = useRoute()

const { current, isLoading: wishlistLoading, fetchOne } = useWishlists()
const {
  items,
  isLoading: itemsLoading,
  fetchList,
  updateItem,
  removeItem,
  reorderItems,
  availableStores,
  clear,
} = useItems()
const reservationsApi = useReservationsApi()
const itemsApi = useItemsApi()
const itemStore = useItemStore()
const toast = useToast()

const draggableItems = ref<WishItemResponse[]>([])
const previousOrder = ref<WishItemResponse[]>([])
const isDragging = ref(false)
const dragBlocked = ref(false)

type ItemsLayoutMode = 'grid' | 'masonry'

const settingsOpen = ref(false)
const entryOpen = ref(false)
const formOpen = ref(false)
const shareOpen = ref(false)
const filterOpen = ref(false)
const itemsLayout = ref<ItemsLayoutMode>('grid')
const editingItem = ref<WishItemResponse | null>(null)
const sharingItem = ref<WishItemResponse | null>(null)
const detailOpen = ref(false)
const detailItem = ref<WishItemResponse | null>(null)
const deleteConfirmOpen = ref(false)
const itemPendingDelete = ref<WishItemResponse | null>(null)
const deleteInProgress = ref(false)
const entryResult = ref({ title: '', productUrl: null as string | null })
const parsedData = ref<ParseUrlData | null>(null)
const shareLinkCopied = ref(false)

const filters = ref<ItemFilters>({
  is_reserved: null,
  is_fulfilled: null,
  priority: [],
  store: null,
})

watch(
  items,
  (newItems) => {
    if (!isDragging.value) {
      draggableItems.value = [...newItems]
    }
  },
  { immediate: true }
)

const activeFilterCount = computed(
  () =>
    (filters.value.is_reserved !== null ? 1 : 0) +
    (filters.value.is_fulfilled !== null ? 1 : 0) +
    filters.value.priority.length +
    (filters.value.store !== null ? 1 : 0)
)

const wishlistId = computed(() => route.params.id as string)

const priorityEmojis: Record<number, string> = { 0: '🙂', 1: '🥰', 2: '😍' }
function priorityLabel(p: number): string {
  const keys = ['normal', 'high', 'must_have'] as const
  return `${priorityEmojis[p]} ${t(`items.priority.${keys[p]}`)}`
}

function clearFilters() {
  filters.value = {
    is_reserved: null,
    is_fulfilled: null,
    priority: [],
    store: null,
  }
}

function onDragStart() {
  previousOrder.value = [...draggableItems.value]
  isDragging.value = true
  if (activeFilterCount.value > 0) {
    dragBlocked.value = true
    toast.add({ title: t('items.drag_filter_warning'), color: 'warning' })
  }
}

async function onDragEnd() {
  isDragging.value = false
  if (dragBlocked.value) {
    draggableItems.value = [...previousOrder.value]
    dragBlocked.value = false
    return
  }
  const newOrder = [...draggableItems.value]
  itemStore.setItems(newOrder, itemStore.total)
  try {
    await reorderItems(newOrder)
  } catch {
    itemStore.setItems(previousOrder.value, itemStore.total)
    draggableItems.value = [...previousOrder.value]
    toast.add({ title: t('items.errors.unknown'), color: 'error' })
  }
}

onMounted(async () => {
  const result = await fetchOne(wishlistId.value)
  if (!result) {
    await navigateTo(localePath('/dashboard'))
    return
  }
})

watch(
  filters,
  (val) => {
    if (wishlistId.value) fetchList(wishlistId.value, val)
  },
  { deep: true, immediate: true }
)

onUnmounted(() => {
  clear()
})

function toggleItemsLayout() {
  itemsLayout.value = itemsLayout.value === 'grid' ? 'masonry' : 'grid'
}

async function copyShareLink() {
  if (!current.value?.slug) return

  const url = `${window.location.origin}/w/${current.value.slug}`
  await navigator.clipboard.writeText(url)

  shareLinkCopied.value = true

  setTimeout(() => {
    shareLinkCopied.value = false
  }, 2000)
}

function onEntryProceed(payload: {
  title: string
  productUrl: string | null
  parsedData?: ParseUrlData | null
}) {
  entryResult.value = { title: payload.title, productUrl: payload.productUrl }
  editingItem.value = null
  parsedData.value = payload.parsedData ?? null
  formOpen.value = true
}

function onEditItem(item: WishItemResponse) {
  editingItem.value = item
  entryResult.value = { title: '', productUrl: null }
  parsedData.value = null
  formOpen.value = true
}

function openItemDetail(item: WishItemResponse) {
  detailItem.value = item
  detailOpen.value = true
}

function onDeleteItem(item: WishItemResponse) {
  itemPendingDelete.value = item
  deleteConfirmOpen.value = true
}

function closeDeleteConfirm() {
  deleteConfirmOpen.value = false
  itemPendingDelete.value = null
}

async function confirmDeleteItem() {
  const target = itemPendingDelete.value
  if (!target) return

  deleteInProgress.value = true

  try {
    await removeItem(target.id)

    if (detailItem.value?.id === target.id) {
      detailOpen.value = false
      detailItem.value = null
    }

    closeDeleteConfirm()
  } finally {
    deleteInProgress.value = false
  }
}

function onShareItem(item: WishItemResponse) {
  sharingItem.value = item
  shareOpen.value = true
}

async function onUpdatePriority(item: WishItemResponse, priority: number) {
  await updateItem(item.id, { priority })
}

function onItemSaved(_item: WishItemResponse) {}

function onItemDeleted() {}

async function onFulfillItem(item: WishItemResponse) {
  try {
    await reservationsApi.fulfill(item.id, !item.is_fulfilled)

    const updated = { ...item, is_fulfilled: !item.is_fulfilled }
    itemStore.updateOne(updated)

    if (detailItem.value?.id === item.id) {
      detailItem.value = updated
    }
  } catch (error) {
    console.error(error)
  }
}
</script>

<style>
.drag-clone {
  border-radius: 0.75rem;
  box-shadow:
    0 24px 48px rgba(0, 0, 0, 0.18),
    0 8px 16px rgba(0, 0, 0, 0.1) !important;
  transform: scale(1.03) rotate(1deg) !important;
  opacity: 0.96 !important;
  cursor: grabbing !important;
}

@media (prefers-color-scheme: dark) {
  .drag-ghost {
    background: #262626;
    outline-color: #525252;
  }
}
</style>
