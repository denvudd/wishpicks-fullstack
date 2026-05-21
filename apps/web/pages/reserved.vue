<template>
  <div class="p-6">
    <h1 class="mb-6 text-xl font-bold text-black dark:text-white">
      {{ t('reserved.title') }}
    </h1>

    <!-- Loading -->
    <div v-if="isLoading" class="space-y-3">
      <USkeleton v-for="n in 4" :key="n" class="h-24 w-full rounded-xl" />
    </div>

    <!-- Empty -->
    <div
      v-else-if="reservations.length === 0"
      class="flex flex-col items-center justify-center py-16 text-center"
    >
      <UIcon name="i-heroicons-gift" class="mb-4 size-12 text-neutral-300 dark:text-neutral-600" />
      <p class="mb-1 text-sm font-semibold text-black dark:text-white">
        {{ t('reserved.empty_title') }}
      </p>
      <p class="text-body-gray dark:text-muted-gray text-xs">
        {{ t('reserved.empty_body') }}
      </p>
    </div>

    <!-- List -->
    <div v-else class="space-y-3">
      <div
        v-for="item in reservations"
        :key="item.item_id"
        class="flex items-center gap-4 rounded-xl border border-neutral-100 bg-white p-4 dark:border-neutral-800 dark:bg-neutral-900"
      >
        <!-- Image -->
        <div class="shrink-0">
          <img
            v-if="item.item_image_url"
            :src="item.item_image_url"
            :alt="item.item_title"
            class="h-16 w-16 rounded-lg object-cover"
          />
          <div
            v-else
            class="flex h-16 w-16 items-center justify-center rounded-lg bg-neutral-100 dark:bg-neutral-800"
          >
            <UIcon name="i-heroicons-gift" class="size-7 text-neutral-400 dark:text-neutral-500" />
          </div>
        </div>

        <!-- Info -->
        <div class="min-w-0 flex-1">
          <p class="line-clamp-1 text-sm font-semibold text-black dark:text-white">
            {{ item.item_title }}
          </p>
          <p class="text-body-gray dark:text-muted-gray mt-0.5 text-xs">
            {{ t('reserved.wishlist_label') }}
            <NuxtLink
              :to="localePath(`/w/${item.wishlist_slug}`)"
              class="text-black underline-offset-2 hover:underline dark:text-white"
            >
              {{ item.wishlist_title }}
            </NuxtLink>
          </p>
          <p class="text-body-gray dark:text-muted-gray text-xs">
            {{ t('reserved.by_owner', { name: item.owner_display_name }) }}
          </p>
          <UBadge
            v-if="item.is_fulfilled"
            color="success"
            variant="subtle"
            size="xs"
            class="mt-1"
            icon="i-heroicons-check"
            :label="t('reserved.fulfilled_badge')"
          />
        </div>

        <!-- Actions -->
        <div class="flex shrink-0 items-center gap-2">
          <UButton
            v-if="item.item_product_url"
            variant="outline"
            color="neutral"
            size="sm"
            :label="t('reserved.go_to_store')"
            :to="item.item_product_url"
            target="_blank"
          />
          <UDropdownMenu :items="menuItems(item)">
            <UButton
              variant="ghost"
              color="neutral"
              size="sm"
              icon="i-heroicons-ellipsis-horizontal"
            />
          </UDropdownMenu>
        </div>
      </div>
    </div>

    <!-- Copy item modal -->
    <SavedCopyItemModal
      v-if="copyModalItem"
      v-model:open="copyModalOpen"
      :item="copyModalItem"
    />
  </div>
</template>

<script setup lang="ts">
import { useReservationsApi } from '~/composables/api/useReservationsApi'
import type { MyReservationResponse, SharedItemResponse } from '~/types/api'

definePageMeta({ layout: 'app', middleware: 'auth' })

const { t } = useI18n()
const localePath = useLocalePath()
const toast = useToast()
const api = useReservationsApi()

const isLoading = ref(true)
const reservations = ref<MyReservationResponse[]>([])
const pendingCopyItem = ref<MyReservationResponse | null>(null)
const copyModalOpen = ref(false)

const copyModalItem = computed<SharedItemResponse | null>(() => {
  if (!pendingCopyItem.value) return null
  const r = pendingCopyItem.value
  return {
    id: r.item_id,
    title: r.item_title,
    image_url: r.item_image_url,
    images: r.item_images,
    product_url: r.item_product_url,
    price_min: r.item_price_min,
    price_max: r.item_price_max,
    currency: r.item_currency,
    description: null,
    priority: 0,
    position: 0,
    is_reserved: false,
    is_fulfilled: false,
    is_surprise: false,
    notes: null,
    tags: null,
    my_reservation: null,
  }
})

function menuItems(item: MyReservationResponse) {
  return [
    [
      {
        label: t('reserved.want_it_too'),
        icon: 'i-heroicons-heart',
        onSelect: () => {
          pendingCopyItem.value = item
          copyModalOpen.value = true
        },
      },
      {
        label: t('reserved.cancel'),
        icon: 'i-heroicons-x-circle',
        onSelect: () => cancelReservation(item),
      },
    ],
  ]
}

async function cancelReservation(item: MyReservationResponse) {
  const previous = [...reservations.value]
  reservations.value = reservations.value.filter((r) => r.item_id !== item.item_id)
  try {
    await api.cancel(item.item_id)
  } catch {
    reservations.value = previous
    toast.add({ title: t('reserved.errors.cancel_failed'), color: 'error' })
  }
}

onMounted(async () => {
  try {
    const data = await api.listMine()
    reservations.value = data.items
  } finally {
    isLoading.value = false
  }
})
</script>
