<template>
  <component :is="dialogComponent" v-model:open="open" :title="item.title" size="xl">
    <template #body>
      <div
        class="space-y-5 gap-x-6 gap-y-8 sm:grid sm:min-h-0 sm:grid-cols-12 sm:space-y-0 lg:gap-x-8"
      >
        <!-- Left: image + badges -->
        <div class="sm:col-span-5">
          <div
            class="relative aspect-square overflow-hidden rounded-2xl bg-chip-gray dark:bg-neutral-800"
          >
            <img
              v-if="item.image_url"
              :src="item.image_url"
              :alt="item.title"
              class="h-full w-full object-cover"
            />
            <div v-else class="flex h-full items-center justify-center">
              <UIcon name="i-heroicons-gift" class="text-muted-gray h-16 w-16" />
            </div>

            <span
              v-if="priorityEmoji"
              class="absolute right-2 top-2 flex h-8 w-8 items-center justify-center rounded-full bg-white/80 text-lg backdrop-blur-sm dark:bg-black/50"
            >
              {{ priorityEmoji }}
            </span>

            <div class="absolute bottom-2 left-2 flex flex-col gap-1">
              <UBadge v-if="item.is_fulfilled" color="success" variant="solid" size="sm">
                {{ t('shared.fulfilled_badge') }}
              </UBadge>
              <UBadge v-else-if="item.is_reserved" color="neutral" variant="solid" size="sm">
                {{ t('shared.reserved_badge') }}
              </UBadge>
            </div>
          </div>
        </div>

        <!-- Right: details + actions -->
        <div class="sm:col-span-7 flex flex-col gap-4">
          <h2 class="text-xl font-bold leading-snug text-black dark:text-white">
            {{ item.title }}
          </h2>

          <p v-if="priceDisplay" class="text-lg font-semibold text-black dark:text-white">
            {{ priceDisplay }}
          </p>

          <div v-if="item.description" class="space-y-1">
            <p
              :class="[
                'text-sm text-body-gray dark:text-muted-gray',
                showFullDesc ? '' : 'line-clamp-3',
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

          <!-- Actions -->
          <div class="mt-auto space-y-2 pt-2">
            <UButton
              v-if="item.product_url"
              :to="item.product_url"
              target="_blank"
              color="neutral"
              icon="i-heroicons-arrow-top-right-on-square"
              :label="t('items.open_store')"
            />

            <Transition
              mode="out-in"
              enter-active-class="animate-in fade-in-0 slide-in-from-bottom-1 duration-200 ease-out"
              leave-active-class="animate-out fade-out-0 duration-100 ease-in"
            >
              <UButton
                v-if="!item.is_reserved"
                key="reserve"
                class="w-full"
                color="neutral"
                :label="t('reservation.reserve')"
                @click="emit('reserve')"
              />

              <div v-else-if="isReservedByMe" key="mine" class="flex flex-col gap-2">
                <Transition
                  mode="out-in"
                  enter-active-class="animate-in fade-in-0 duration-150 ease-out"
                  leave-active-class="animate-out fade-out-0 duration-100 ease-in"
                >
                  <p
                    :key="item.is_fulfilled ? 'fulfilled-label' : 'reserved-label'"
                    class="text-xs font-medium text-black dark:text-white"
                  >
                    {{ item.is_fulfilled ? t('reservation.fulfilled_by_you') : t('reservation.reserved_by_you') }}
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
                      :label="item.is_fulfilled ? t('reservation.unfulfill') : t('reservation.fulfill')"
                      @click="emit('fulfill')"
                    />
                  </Transition>
                  <UButton
                    variant="ghost"
                    color="error"
                    size="sm"
                    :label="t('reservation.cancel')"
                    @click="emit('cancel')"
                  />
                </div>
              </div>

              <p v-else key="other" class="text-body-gray dark:text-muted-gray text-xs">
                {{ t('reservation.already_reserved') }}
              </p>
            </Transition>
          </div>
        </div>
      </div>
    </template>
  </component>
</template>

<script setup lang="ts">
import { resolveComponent } from 'vue'
import type { ReservationMode, SharedItemResponse } from '~/types/api'

const props = defineProps<{
  item: SharedItemResponse
  reservationMode: ReservationMode
  anonToken?: string
  isAuthenticated: boolean
}>()

const emit = defineEmits<{
  reserve: []
  cancel: []
  fulfill: []
}>()

const open = defineModel<boolean>('open', { default: false })

const { t } = useI18n()

const UModal = resolveComponent('UModal')
const UDrawer = resolveComponent('UDrawer')

const isMobile = typeof window !== 'undefined' && window.matchMedia('(max-width: 767px)').matches
const dialogComponent = isMobile ? UDrawer : UModal

const showFullDesc = ref(false)

const PRIORITY_EMOJI: Record<number, string> = { 0: '✨', 1: '🔥', 2: '💎' }
const priorityEmoji = computed(() => PRIORITY_EMOJI[props.item.priority] ?? null)

const isReservedByMe = computed(
  () => !!props.item.my_reservation || !!props.anonToken,
)

const priceDisplay = computed(() => {
  const { price_min, price_max, currency } = props.item

  if (!price_min && !price_max) return null

  if (price_min && price_max && price_min !== price_max) {
    return `${price_min}–${price_max} ${currency}`
  }
  
  return `${price_min || price_max} ${currency}`
})
</script>
