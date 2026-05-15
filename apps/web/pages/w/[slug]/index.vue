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

        <!-- Save button -->
        <div class="flex">
          <UButton
            v-if="isAuthenticated"
            :icon="
              savedState ? 'i-heroicons-bookmark-solid' : 'i-heroicons-bookmark'
            "
            :label="savedState ? t('saved.saved') : t('saved.save')"
            variant="outline"
            color="neutral"
            size="sm"
            :loading="saveLoading"
            @click="onToggleSave"
          />
          <UButton
            v-else
            icon="i-heroicons-bookmark"
            :label="t('saved.save')"
            variant="outline"
            color="neutral"
            size="sm"
            @click="onSaveGuest"
          />
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
          @copy="onCopyItem"
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

    <!-- Reservation modal (handles anonymous name prompt + registered-only gate) -->
    <SharedReservationModal
      v-if="reserveItem && wishlist"
      v-model:open="reserveOpen"
      :item="reserveItem"
      :reservation-mode="wishlist.reservation_mode"
      :is-authenticated="isAuthenticated"
      @reserved="onReserved"
    />

    <!-- Copy item modal -->
    <SavedCopyItemModal
      v-if="copyModalItem"
      v-model:open="copyOpen"
      :item="copyModalItem"
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

const {
  wishlist,
  items: fetchedItems,
  pending,
  error,
} = useSharedWishlist(slug)
const reservationStore = useReservationStore()
const reservationsApi = useReservationsApi()
const authStore = useAuthStore()
const toast = useToast()

const isAuthenticated = computed(() => !!authStore.user)

const { isSaved, fetchWishlists, toggleWishlist } = useSaved()

const savedState = computed(() =>
  wishlist.value ? isSaved(wishlist.value.id) : false
)
const saveLoading = ref(false)

const copyModalItem = ref<SharedItemResponse | null>(null)
const copyOpen = ref(false)

const reserveItem = ref<SharedItemResponse | null>(null)
const reserveOpen = ref(false)

async function onToggleSave() {
  if (!wishlist.value) return
  saveLoading.value = true
  await toggleWishlist(wishlist.value.id)
  saveLoading.value = false
}

function onSaveGuest() {
  toast.add({
    title: t('saved.save_guest_prompt'),
    actions: [
      {
        label: t('auth.login.submit'),
        onClick: () => {
          navigateTo(localePath('/login'))
        },
      },
    ],
  })
}

function onCopyItem(item: SharedItemResponse) {
  copyModalItem.value = item
  copyOpen.value = true
}

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
watch(
  fetchedItems,
  (val) => {
    displayItems.value = [...val]
  },
  { immediate: true }
)

onMounted(() => {
  reservationStore.load()
  if (isAuthenticated.value) {
    fetchWishlists()
  }
})

useSeoMeta({
  title: () =>
    wishlist.value ? `${wishlist.value.title} — Wishpicks` : 'Wishpicks',
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

function onReserve(item: SharedItemResponse) {
  reserveItem.value = item
  reserveOpen.value = true
}

function onReserved(itemId: string, anonToken: string | null) {
  if (anonToken) reservationStore.setToken(itemId, anonToken)

  displayItems.value = displayItems.value.map((i) =>
    i.id === itemId
      ? { ...i, is_reserved: true, my_reservation: { anon_token: null } }
      : i
  )
}

async function onCancel(item: SharedItemResponse) {
  const anonToken = reservationStore.getToken(item.id)

  try {
    await reservationsApi.cancel(item.id, anonToken)
    reservationStore.clearToken(item.id)

    displayItems.value = displayItems.value.map((i) =>
      i.id === item.id
        ? {
            ...i,
            is_reserved: false,
            is_fulfilled: false,
            my_reservation: null,
          }
        : i
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
      i.id === item.id ? { ...i, is_fulfilled: newState } : i
    )
  } catch {
    // fulfill failed — list state unchanged
  }
}
</script>
