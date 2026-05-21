<template>
  <div
    tabindex="0"
    class="group cursor-pointer overflow-hidden rounded-xl border border-neutral-100 bg-white transition-colors hover:border-neutral-300 focus-visible:ring-2 focus-visible:ring-neutral-400 focus-visible:outline-none dark:border-neutral-800 dark:bg-neutral-900 dark:hover:border-neutral-600 dark:focus-visible:ring-neutral-500"
    style="box-shadow: var(--shadow-card)"
    @click="$emit('open', item)"
    @keydown.enter.prevent="$emit('open', item)"
    @keydown.space.prevent="$emit('open', item)"
  >
    <!-- Image area -->
    <div class="bg-chip-gray relative aspect-square dark:bg-neutral-800">
      <img
        v-if="item.image_url"
        :src="item.image_url"
        :alt="item.title"
        class="h-full w-full object-cover"
      />
      <div v-else class="flex h-full items-center justify-center">
        <UIcon name="i-heroicons-gift" class="text-muted-gray h-10 w-10" />
      </div>

      <!-- Priority emoji -->
      <span
        v-if="priorityEmoji"
        class="absolute top-2 right-2 flex h-8 w-8 items-center justify-center rounded-full bg-white/80 text-base backdrop-blur-sm dark:bg-black/50"
      >
        {{ priorityEmoji }}
      </span>

      <!-- Status badges -->
      <div class="absolute bottom-2 left-2 flex flex-col gap-1">
        <Transition
          mode="out-in"
          enter-active-class="animate-in fade-in-0 zoom-in-90 duration-200 ease-out"
          leave-active-class="animate-out fade-out-0 zoom-out-90 duration-150 ease-in"
        >
          <UBadge
            v-if="item.is_fulfilled"
            key="fulfilled"
            color="success"
            variant="solid"
            size="sm"
          >
            {{ t('shared.fulfilled_badge') }}
          </UBadge>
          <UBadge
            v-else-if="item.is_reserved"
            key="reserved"
            color="neutral"
            variant="solid"
            size="sm"
          >
            {{ t('shared.reserved_badge') }}
          </UBadge>
        </Transition>
      </div>

      <div
        v-if="isAuthenticated"
        class="pointer-events-none absolute left-3 top-2 opacity-0 transition-opacity group-hover:pointer-events-auto group-hover:opacity-100"
        @click.stop
      >
        <UButton
          size="sm"
          color="secondary"
          variant="solid"
          :label="t('saved.add')"
          @click.stop="$emit('copy', item)"
        />
      </div>
    </div>

    <!-- Info + actions -->
    <div class="space-y-3 p-3">
      <div class="space-y-1">
        <p
          class="line-clamp-1 text-sm leading-tight font-semibold text-black dark:text-white"
        >
          {{ item.title }}
        </p>
        <div
          class="text-body-gray dark:text-muted-gray flex items-center gap-2 text-xs"
        >
          <a
            v-if="item.product_url"
            :href="item.product_url"
            target="_blank"
            rel="noopener noreferrer"
            class="min-w-0 flex-1 truncate underline underline-offset-2 transition-colors hover:text-black dark:hover:text-white"
            @click.stop
          >
            {{ storeDomain }}
          </a>
          <span
            v-if="priceDisplay"
            :class="item.product_url ? 'ml-auto shrink-0' : ''"
          >
            {{ priceDisplay }}
          </span>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex flex-col gap-2" @click.stop>
        <Transition
          mode="out-in"
          enter-active-class="animate-in fade-in-0 slide-in-from-bottom-1 duration-200 ease-out"
          leave-active-class="animate-out fade-out-0 duration-100 ease-in"
        >
          <!-- Not reserved -->
          <UButton
            v-if="!item.is_reserved"
            key="reserve"
            color="neutral"
            size="sm"
            class="w-full"
            :label="t('reservation.reserve')"
            @click="$emit('reserve')"
          />

          <!-- Reserved by me -->
          <div
            v-else-if="isReservedByMe"
            key="mine"
            class="flex flex-col gap-2"
          >
            <Transition
              mode="out-in"
              enter-active-class="animate-in fade-in-0 duration-150 ease-out"
              leave-active-class="animate-out fade-out-0 duration-100 ease-in"
            >
              <p
                :key="item.is_fulfilled ? 'fulfilled-label' : 'reserved-label'"
                class="text-xs font-medium text-black dark:text-white"
              >
                {{
                  item.is_fulfilled
                    ? t('reservation.fulfilled_by_you')
                    : t('reservation.reserved_by_you')
                }}
              </p>
            </Transition>
            <div class="flex gap-2">
              <Transition
                mode="out-in"
                enter-active-class="animate-in fade-in-0 duration-150 ease-out"
                leave-active-class="animate-out fade-out-0 duration-100 ease-in"
              >
                <UButton
                  :key="item.is_fulfilled ? 'unfulfill-btn' : 'fulfill-btn'"
                  variant="outline"
                  color="neutral"
                  size="sm"
                  class="flex-1"
                  :label="
                    item.is_fulfilled
                      ? t('reservation.unfulfill')
                      : t('reservation.fulfill')
                  "
                  @click="$emit('fulfill')"
                />
              </Transition>
              <UButton
                variant="ghost"
                color="error"
                size="sm"
                :label="t('reservation.cancel')"
                @click="$emit('cancel')"
              />
            </div>
          </div>

          <!-- Reserved by someone else -->
          <p
            v-else
            key="other"
            class="text-body-gray dark:text-muted-gray text-xs"
          >
            {{ t('reservation.already_reserved') }}
          </p>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ReservationMode, SharedItemResponse } from '~/types/api'

const props = defineProps<{
  item: SharedItemResponse
  reservationMode: ReservationMode
  anonToken?: string
  isAuthenticated: boolean
}>()

defineEmits<{
  reserve: []
  cancel: []
  fulfill: []
  open: [item: SharedItemResponse]
  copy: [item: SharedItemResponse]
}>()

const { t } = useI18n()

const PRIORITY_EMOJI: Record<number, string> = { 0: '🙂', 1: '🥰', 2: '😍' }
const priorityEmoji = computed(
  () => PRIORITY_EMOJI[props.item.priority] ?? null
)

const isReservedByMe = computed(
  () => !!props.item.my_reservation || !!props.anonToken
)

const storeDomain = computed(() => {
  if (!props.item.product_url) return null
  try {
    return new URL(props.item.product_url).hostname.replace(/^www\./, '')
  } catch {
    return props.item.product_url
  }
})

const priceDisplay = computed(() => {
  const { price_min, price_max, currency } = props.item
  if (!price_min && !price_max) return null
  if (price_min && price_max && price_min !== price_max) {
    return `${price_min}–${price_max} ${currency}`
  }
  return `${price_min || price_max} ${currency}`
})
</script>
