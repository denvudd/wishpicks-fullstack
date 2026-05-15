<template>
  <div class="min-h-screen">
    <!-- Loading -->
    <div v-if="pending" class="space-y-4 p-6">
      <USkeleton class="h-7 w-56 rounded-lg" />
      <USkeleton class="h-4 w-36 rounded-lg" />
      <div class="mt-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        <USkeleton v-for="n in 6" :key="n" class="aspect-square rounded-xl" />
      </div>
    </div>

    <!-- Error / not found -->
    <div
      v-else-if="error || !wishlist"
      class="flex flex-col items-center justify-center py-24 text-center"
    >
      <p class="text-body-gray dark:text-muted-gray text-sm">
        {{ t('wishlists.errors.unknown') }}
      </p>
    </div>

    <!-- Content -->
    <div v-else class="w-full p-6">
      <!-- Header -->
      <div class="mb-8 space-y-3">
        <div class="space-y-1">
          <h1 class="text-xl font-bold text-black dark:text-white">
            {{ wishlist.title }}
          </h1>
          <p
            v-if="wishlist.event_date"
            class="text-body-gray dark:text-muted-gray text-sm"
          >
            {{ wishlist.event_date }}
            <span v-if="wishlist.event_type">
              · {{ t(`wishlists.event_type.${wishlist.event_type}`) }}
            </span>
          </p>
          <p
            v-if="wishlist.description"
            class="text-body-gray dark:text-muted-gray text-sm"
          >
            {{ wishlist.description }}
          </p>
        </div>

        <!-- Author + date -->
        <div class="flex items-center gap-2">
          <UAvatar
            :src="wishlist.author.avatar_url ?? undefined"
            :alt="wishlist.author.display_name ?? ''"
            size="xs"
          />
          <span class="text-body-gray dark:text-muted-gray text-xs">
            {{ wishlist.author.display_name ?? t('shared.anonymous_author') }}
            · {{ createdAt }}
          </span>
        </div>
      </div>

      <!-- Items grid -->
      <div
        v-if="displayItems.length"
        class="grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-5"
      >
        <SharedItemCard
          v-for="(item, i) in displayItems"
          :key="item.id"
          :item="item"
          :reservation-mode="wishlist.reservation_mode"
          :anon-token="reservationStore.getToken(item.id)"
          :is-authenticated="isAuthenticated"
          class="animate-in fade-in-0 zoom-in-95 fill-mode-both duration-300"
          :style="{ animationDelay: `${Math.min(i * 40, 280)}ms` }"
          @open="openDetail(item)"
          @reserve="onReserve(item)"
          @cancel="onCancel(item)"
          @fulfill="onFulfill(item)"
        />
      </div>

      <div
        v-else
        class="flex flex-col items-center justify-center py-16 text-center"
      >
        <p class="text-body-gray dark:text-muted-gray text-sm">
          {{ t('shared.no_items') }}
        </p>
      </div>
    </div>

    <!-- Item detail modal -->
    <SharedItemDetailModal
      v-if="detailItem && wishlist"
      v-model:open="detailOpen"
      :item="detailItem"
      :reservation-mode="wishlist.reservation_mode"
      :anon-token="reservationStore.getToken(detailItem.id)"
      :is-authenticated="isAuthenticated"
      @reserve="onReserve(detailItem)"
      @cancel="onCancel(detailItem)"
      @fulfill="onFulfill(detailItem)"
    />
  </div>
</template>

<script setup lang="ts">
import type { SharedItemResponse } from '~/types/api'
import { useReservationsApi } from '~/composables/api/useReservationsApi'

definePageMeta({ layout: 'default' })

const route = useRoute()
const { t } = useI18n()
const localePath = useLocalePath()
const slug = computed(() => route.params.slug as string)

const { wishlist, items: fetchedItems, pending, error } = useSharedWishlist(slug)
const reservationStore = useReservationStore()
const reservationsApi = useReservationsApi()
const authStore = useAuthStore()

const isAuthenticated = computed(() => !!authStore.user)

const createdAt = computed(() => {
  if (!wishlist.value) return ''
  const locale = useI18n().locale.value === 'uk' ? 'uk-UA' : 'en-US'
  return new Date(wishlist.value.created_at).toLocaleDateString(locale, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
})

const displayItems = ref<SharedItemResponse[]>([])
watch(fetchedItems, (val) => { displayItems.value = [...val] }, { immediate: true })

onMounted(() => reservationStore.load())

useSeoMeta({
  title: () => wishlist.value ? `${wishlist.value.title} — Wishpicks` : 'Wishpicks',
  ogTitle: () => wishlist.value?.title ?? 'Wishpicks',
  description: () => wishlist.value?.description ?? '',
  ogDescription: () => wishlist.value?.description ?? '',
  ogImage: () => wishlist.value?.cover_url ?? undefined,
})

const detailItem = ref<SharedItemResponse | null>(null)
const detailOpen = ref(false)

watch(displayItems, (items) => {
  if (detailItem.value) {
    const updated = items.find((i) => i.id === detailItem.value!.id)
    if (updated) detailItem.value = updated
  }
})

function openDetail(item: SharedItemResponse) {
  detailItem.value = item
  detailOpen.value = true
}

async function onReserve(item: SharedItemResponse) {
  if (wishlist.value?.reservation_mode === 'registered_only' && !isAuthenticated.value) {
    return navigateTo(localePath('/login'))
  }
  try {
    const res = await reservationsApi.reserve(item.id)
    if (res.data.anon_token) reservationStore.setToken(item.id, res.data.anon_token)
    displayItems.value = displayItems.value.map((i) =>
      i.id === item.id
        ? { ...i, is_reserved: true, my_reservation: { anon_token: null } }
        : i,
    )
  } catch {
    // reservation failed — list state unchanged
  }
}

async function onCancel(item: SharedItemResponse) {
  const anonToken = reservationStore.getToken(item.id)
  try {
    await reservationsApi.cancel(item.id, anonToken)
    reservationStore.clearToken(item.id)
    displayItems.value = displayItems.value.map((i) =>
      i.id === item.id
        ? { ...i, is_reserved: false, is_fulfilled: false, my_reservation: null }
        : i,
    )
  } catch {
    // cancel failed — list state unchanged
  }
}

async function onFulfill(item: SharedItemResponse) {
  const anonToken = reservationStore.getToken(item.id)
  const newState = !item.is_fulfilled
  try {
    await reservationsApi.fulfill(item.id, newState, anonToken)
    displayItems.value = displayItems.value.map((i) =>
      i.id === item.id ? { ...i, is_fulfilled: newState } : i,
    )
  } catch {
    // fulfill failed — list state unchanged
  }
}
</script>
