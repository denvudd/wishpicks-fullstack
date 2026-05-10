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

      <div class="mb-8 flex w-full items-center justify-between gap-4">
        <UButton
          v-if="!itemsLoading && items.length"
          variant="outline"
          color="neutral"
          :icon="
            itemsLayout === 'grid'
              ? 'i-heroicons-view-columns'
              : 'i-heroicons-squares-2x2'
          "
          :aria-label="
            itemsLayout === 'grid'
              ? t('wishlists.items_layout.switch_to_masonry')
              : t('wishlists.items_layout.switch_to_grid')
          "
          @click="toggleItemsLayout"
        />
      </div>

      <div
        v-if="itemsLoading"
        class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4"
      >
        <USkeleton v-for="n in 4" :key="n" class="aspect-square rounded-xl" />
      </div>

      <ItemsItemEmptyState
        v-else-if="!items.length"
        @create="entryOpen = true"
      />

      <div v-else>
        <div
          v-if="itemsLayout === 'grid'"
          class="grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-5"
        >
          <ItemsItemCard
            v-for="item in items"
            :key="item.id"
            :item="item"
            @select="openItemDetail"
            @edit="onEditItem"
            @delete="onDeleteItem"
            @share="onShareItem"
            @update-priority="onUpdatePriority"
          />
        </div>
        <div v-else class="columns-2 gap-x-4 sm:columns-4 lg:columns-5">
          <div
            v-for="item in items"
            :key="item.id"
            class="mb-4 break-inside-avoid"
          >
            <ItemsItemCard
              :item="item"
              @select="openItemDetail"
              @edit="onEditItem"
              @delete="onDeleteItem"
              @share="onShareItem"
              @update-priority="onUpdatePriority"
            />
          </div>
        </div>
      </div>

      <WishlistSettingsModal
        v-model:open="settingsOpen"
        :wishlist="current"
        @deleted="navigateTo(localePath('/dashboard'))"
      />

      <ItemsItemEntryModal v-model:open="entryOpen" @proceed="onEntryProceed" />

      <ItemsItemShareModal
        v-if="sharingItem"
        v-model:open="shareOpen"
        :item="sharingItem"
      />

      <ItemsItemFormModal
        v-model:open="formOpen"
        :initial-title="entryResult.title"
        :initial-product-url="entryResult.productUrl"
        :wishlist-id="current.id"
        :item="editingItem"
        @saved="onItemSaved"
        @deleted="onItemDeleted"
      />

      <ItemsItemDetailModal
        v-if="detailItem"
        v-model:open="detailOpen"
        :item="detailItem"
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
import type { WishItemResponse } from '~/types/api'

definePageMeta({ layout: 'app', middleware: 'auth' })

const { t } = useI18n()
const localePath = useLocalePath()
const route = useRoute()

const { current, isLoading: wishlistLoading, fetchOne: fetchWishlist } = useWishlists()
const {
  items,
  isLoading: itemsLoading,
  fetchList,
  fetchOne: fetchItem,
  updateItem,
  removeItem,
  clear,
} = useItems()

type ItemsLayoutMode = 'grid' | 'masonry'

const settingsOpen = ref(false)
const entryOpen = ref(false)
const formOpen = ref(false)
const shareOpen = ref(false)
const detailOpen = ref(false)
const detailItem = ref<WishItemResponse | null>(null)
const deleteConfirmOpen = ref(false)
const itemPendingDelete = ref<WishItemResponse | null>(null)
const deleteInProgress = ref(false)
const itemsLayout = ref<ItemsLayoutMode>('grid')
const editingItem = ref<WishItemResponse | null>(null)
const sharingItem = ref<WishItemResponse | null>(null)
const entryResult = ref({ title: '', productUrl: null as string | null })

const wishlistId = computed(() => route.params.id as string)
const itemId = computed(() => route.params.itemId as string)

onMounted(async () => {
  const result = await fetchWishlist(wishlistId.value)
  if (!result) {
    await navigateTo(localePath('/dashboard'))
    return
  }

  const itemPromise = fetchItem(itemId.value)
  await fetchList(wishlistId.value)
  const item = await itemPromise

  if (item) {
    detailItem.value = item
    detailOpen.value = true
  }
})

onUnmounted(() => {
  clear()
})

function toggleItemsLayout() {
  itemsLayout.value = itemsLayout.value === 'grid' ? 'masonry' : 'grid'
}

function onEntryProceed(payload: { title: string; productUrl: string | null }) {
  entryResult.value = payload
  editingItem.value = null
  formOpen.value = true
}

function onEditItem(item: WishItemResponse) {
  editingItem.value = item
  entryResult.value = { title: '', productUrl: null }
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
    if (target.id === itemId.value) {
      await navigateTo(localePath(`/wishlists/${wishlistId.value}`))
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

function onItemSaved(_item: WishItemResponse) {
  // store updated via useItems composable
}

function onItemDeleted() {
  // store updated via useItems composable
}
</script>
