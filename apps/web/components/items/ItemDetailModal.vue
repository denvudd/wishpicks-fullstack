<template>
  <component
    :is="dialogComponent"
    v-model:open="open"
    size="xl"
    class="flex w-full transform-none overflow-y-auto text-left text-base transition sm:my-8 sm:max-w-3xl lg:max-w-5xl"
    :ui="{
      header: 'hidden',
    }"
  >
    <template #body>
      <div
        class="space-y-5 gap-x-6 gap-y-8 sm:grid sm:min-h-0 sm:grid-cols-12 sm:space-y-0 lg:gap-x-8"
      >
        <div class="sm:col-span-5">
          <!-- Single image or placeholder -->
          <template v-if="galleryImages.length <= 1">
            <div
              class="bg-chip-gray relative aspect-square overflow-hidden rounded-2xl dark:bg-neutral-800"
            >
              <img
                v-if="item.image_url"
                :src="item.image_url"
                :alt="item.title"
                class="h-full w-full object-cover"
                loading="lazy"
              />
              <div v-else class="flex h-full items-center justify-center">
                <UIcon
                  name="i-heroicons-gift"
                  class="text-muted-gray h-16 w-16"
                />
              </div>
              <UTooltip :text="priorityLabel">
                <span
                  v-if="priorityEmoji"
                  class="absolute top-2 right-2 flex h-8 w-8 items-center justify-center rounded-full bg-white/80 text-lg backdrop-blur-sm dark:bg-black/50"
                >
                  {{ priorityEmoji }}
                </span>
              </UTooltip>
            </div>
          </template>

          <!-- Gallery: main carousel + thumbnail strip -->
          <template v-else>
            <div class="space-y-2">
              <div class="relative aspect-square overflow-hidden rounded-2xl">
                <UCarousel
                  ref="carouselRef"
                  :items="galleryImages"
                  class="h-full w-full"
                  @select="(i: number) => (activeIndex = i)"
                >
                  <template #default="{ item: src }">
                    <img
                      :src="src"
                      :alt="item.title"
                      class="h-full w-full object-cover"
                      loading="lazy"
                    />
                  </template>
                </UCarousel>
                <UTooltip :text="priorityLabel">
                  <span
                    v-if="priorityEmoji"
                    class="absolute top-2 right-2 flex h-8 w-8 items-center justify-center rounded-full bg-white/80 text-lg backdrop-blur-sm dark:bg-black/50"
                  >
                    {{ priorityEmoji }}
                  </span>
                </UTooltip>
              </div>
              <!-- Thumbnail strip -->
              <div class="flex gap-1.5 overflow-x-auto pb-0.5">
                <button
                  v-for="(src, i) in galleryImages"
                  :key="src + '-' + i"
                  type="button"
                  class="relative aspect-square w-14 shrink-0 overflow-hidden rounded-lg border transition-all duration-200"
                  :class="
                    activeIndex === i
                      ? 'border-neutral-900 opacity-100 dark:border-white'
                      : 'border-transparent opacity-50 hover:opacity-80'
                  "
                  @click="goToSlide(i)"
                >
                  <img
                    :src="src"
                    :alt="item.title"
                    class="h-full w-full object-cover"
                  />
                </button>
              </div>
            </div>
          </template>
        </div>

        <!-- Right: details -->
        <div class="flex flex-col gap-4 sm:col-span-7">
          <!-- Title + time -->
          <div class="space-y-0.5">
            <h2
              class="text-xl leading-snug font-bold text-black dark:text-white"
            >
              {{ item.title }}
            </h2>
            <p class="text-muted-gray text-xs">{{ addedAgo }}</p>
          </div>

          <!-- Price -->
          <p
            v-if="priceDisplay"
            class="text-lg font-semibold text-black dark:text-white"
          >
            {{ priceDisplay }}
          </p>

          <!-- Description -->
          <div v-if="item.description" class="space-y-1">
            <p
              :class="[
                'text-body-gray dark:text-muted-gray text-sm',
                showFullDesc ? '' : 'line-clamp-2',
              ]"
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
            <p v-else class="text-muted-gray text-xs">
              {{ t('items.fields.product_url_placeholder') }}
            </p>
            <UButton
              v-if="item.is_reserved"
              variant="outline"
              color="neutral"
              size="sm"
              :label="
                item.is_fulfilled
                  ? t('reservation.unfulfill')
                  : t('reservation.fulfill')
              "
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
const isMobile =
  typeof window !== 'undefined' &&
  window.matchMedia('(max-width: 767px)').matches
const dialogComponent = isMobile ? UDrawer : UModal

const showFullDesc = ref(false)

const PRIORITY_EMOJI: Record<number, string> = { 0: '🙂', 1: '🥰', 2: '😍' }
const priorityEmoji = computed(
  () => PRIORITY_EMOJI[props.item.priority] ?? null
)

const priorityLabel = computed(() => {
  const map: Record<number, string> = {
    0: t('items.priority.normal'),
    1: t('items.priority.high'),
    2: t('items.priority.must_have'),
  }

  return map[props.item.priority] ?? ''
})

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

const carouselRef = ref()
const activeIndex = ref(0)

const galleryImages = computed(() => [
  ...(props.item.image_url ? [props.item.image_url] : []),
  ...(props.item.images ?? []),
])

watch(open, (val) => {
  if (val) activeIndex.value = 0
})

function goToSlide(index: number) {
  activeIndex.value = index
  carouselRef.value?.emblaApi?.scrollTo(index)
}
</script>
