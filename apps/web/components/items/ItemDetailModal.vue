<template>
  <component
    :is="dialogComponent"
    v-model:open="open"
    :title="item.title"
    size="xl"
  >
    <template #body>
      <div
        class="space-y-5 gap-x-6 gap-y-8 sm:grid sm:min-h-0 sm:grid-cols-12 sm:space-y-0 lg:gap-x-8"
      >
        <!-- Left: image + priority badge -->
        <div class="sm:col-span-5">
          <div class="relative aspect-square overflow-hidden rounded-2xl bg-chip-gray dark:bg-neutral-800">
            <div class="flex h-full items-center justify-center">
              <UIcon name="i-heroicons-gift" class="text-muted-gray h-16 w-16" />
            </div>
            <span
              v-if="priorityEmoji"
              class="absolute right-2 top-2 flex h-8 w-8 items-center justify-center rounded-full bg-white/80 text-lg backdrop-blur-sm dark:bg-black/50"
            >
              {{ priorityEmoji }}
            </span>
          </div>
        </div>

        <!-- Right: details -->
        <div class="sm:col-span-7 flex flex-col gap-4">
          <!-- Title + time -->
          <div class="space-y-0.5">
            <h2 class="text-xl font-bold leading-snug text-black dark:text-white">
              {{ item.title }}
            </h2>
            <p class="text-xs text-muted-gray">{{ addedAgo }}</p>
          </div>

          <!-- Price -->
          <p v-if="priceDisplay" class="text-lg font-semibold text-black dark:text-white">
            {{ priceDisplay }}
          </p>

          <!-- Description -->
          <div v-if="item.description" class="space-y-1">
            <p
              :class="['text-sm text-body-gray dark:text-muted-gray', showFullDesc ? '' : 'line-clamp-2']"
            >
              {{ item.description }}
            </p>
            <button
              class="text-xs font-medium text-black underline underline-offset-2 dark:text-white"
              @click="showFullDesc = !showFullDesc"
            >
              {{ showFullDesc ? t('items.show_less') : t('items.show_more') }}
            </button>
          </div>

          <!-- Tags -->
          <div v-if="item.tags?.length" class="flex flex-wrap gap-1.5">
            <UBadge
              v-for="tag in item.tags"
              :key="tag"
              variant="soft"
              color="neutral"
              size="sm"
            >
              {{ tag }}
            </UBadge>
          </div>

          <!-- Fulfill section -->
          <div class="mt-auto space-y-2 pt-2">
            <p class="text-sm font-semibold text-black dark:text-white">
              {{ t('items.fulfill_question') }}
            </p>
            <UButton
              v-if="item.product_url"
              :to="item.product_url"
              target="_blank"
              color="neutral"
              icon="i-heroicons-arrow-top-right-on-square"
              :label="t('items.open_store')"
            />
            <p v-else class="text-xs text-muted-gray">
              {{ t('items.fields.product_url_placeholder') }}
            </p>
            <UButton
              v-if="item.is_reserved"
              variant="outline"
              color="neutral"
              size="sm"
              :label="item.is_fulfilled ? t('reservation.unfulfill') : t('reservation.fulfill')"
              @click="emit('fulfill', item)"
            />
          </div>
        </div>
      </div>
    </template>
  </component>
</template>

<script setup lang="ts">
import { resolveComponent } from 'vue'
import type { WishItemResponse } from '~/types/api'

const props = defineProps<{ item: WishItemResponse }>()
const emit = defineEmits<{ fulfill: [item: WishItemResponse] }>()
const open = defineModel<boolean>('open', { default: false })

const { t } = useI18n()

const UModal = resolveComponent('UModal')
const UDrawer = resolveComponent('UDrawer')

// Resolved synchronously so dialogComponent never changes after the modal first renders,
// preventing UModal→UDrawer swap from emitting update:open=false and triggering a redirect.
const isMobile = typeof window !== 'undefined' && window.matchMedia('(max-width: 767px)').matches
const dialogComponent = isMobile ? UDrawer : UModal

const showFullDesc = ref(false)

const PRIORITY_EMOJI: Record<number, string> = { 0: '✨', 1: '🔥', 2: '💎' }
const priorityEmoji = computed(() => PRIORITY_EMOJI[props.item.priority] ?? null)

const priceDisplay = computed(() => {
  const { price_min, price_max, currency } = props.item
  if (!price_min && !price_max) return null
  if (price_min && price_max && price_min !== price_max) {
    return `${price_min}–${price_max} ${currency}`
  }
  return `${price_min || price_max} ${currency}`
})

const addedAgo = computed(() => {
  const created = new Date(props.item.created_at)
  const now = new Date()
  const diffMs = now.getTime() - created.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHr = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHr / 24)
  const diffWeek = Math.floor(diffDay / 7)
  const diffMonth = Math.floor(diffDay / 30)

  const locale = useI18n().locale.value === 'uk' ? 'uk-UA' : 'en-US'
  const rtf = new Intl.RelativeTimeFormat(locale, { numeric: 'auto' })

  if (diffMonth >= 1) return rtf.format(-diffMonth, 'month')
  if (diffWeek >= 1) return rtf.format(-diffWeek, 'week')
  if (diffDay >= 1) return rtf.format(-diffDay, 'day')
  if (diffHr >= 1) return rtf.format(-diffHr, 'hour')
  if (diffMin >= 1) return rtf.format(-diffMin, 'minute')
  return rtf.format(-diffSec, 'second')
})
</script>
