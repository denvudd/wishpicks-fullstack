<template>
  <div
    tabindex="0"
    class="group relative cursor-pointer overflow-hidden rounded-xl border border-neutral-100 bg-white transition-all hover:border-neutral-300 focus-visible:ring-2 focus-visible:ring-neutral-400 focus-visible:outline-none dark:border-neutral-800 dark:bg-neutral-900 dark:hover:border-neutral-600 dark:focus-visible:ring-neutral-500"
    :aria-label="t('items.card_open_detail', { title: item.title })"
    style="box-shadow: var(--shadow-card)"
    @click="emit('select', item)"
    @keydown.enter.prevent="emit('select', item)"
    @keydown.space.prevent="emit('select', item)"
  >
    <div class="bg-chip-gray relative aspect-square dark:bg-neutral-800">
      <!-- 0 images -->
      <div v-if="cardImages.length === 0" class="flex h-full items-center justify-center">
        <UIcon name="i-heroicons-gift" class="text-muted-gray h-10 w-10" />
      </div>

      <!-- 1 image -->
      <img
        v-else-if="cardImages.length === 1"
        :src="cardImages[0]"
        :alt="item.title"
        class="h-full w-full object-cover"
        loading="lazy"
      />

      <!-- 2 images -->
      <div v-else-if="cardImages.length === 2" class="grid h-full w-full grid-cols-2 gap-px">
        <img
          v-for="(src, i) in cardImages"
          :key="i"
          :src="src"
          :alt="item.title"
          class="h-full w-full object-cover"
          loading="lazy"
        />
      </div>

      <!-- 3 images -->
      <div v-else class="grid h-full w-full grid-cols-2 gap-px">
        <img
          :src="cardImages[0]"
          :alt="item.title"
          class="row-span-2 h-full w-full object-cover"
          loading="lazy"
        />
        <img
          :src="cardImages[1]"
          :alt="item.title"
          class="h-full w-full object-cover"
          loading="lazy"
        />
        <img
          :src="cardImages[2]"
          :alt="item.title"
          class="h-full w-full object-cover"
          loading="lazy"
        />
      </div>

      <div
        v-if="priorityEmoji"
        class="absolute right-2 bottom-2 z-10"
        @click.stop
      >
        <UDropdownMenu :items="priorityMenuItems">
          <button
            type="button"
            class="flex h-8 w-8 items-center justify-center rounded-full bg-white/95 text-base leading-none shadow-sm ring-1 ring-neutral-200/80 transition-colors hover:bg-white dark:bg-neutral-900/95 dark:ring-neutral-700"
            :title="priorityLabel"
          >
            {{ priorityEmoji }}
          </button>
        </UDropdownMenu>
      </div>

      <div
        class="pointer-events-none absolute inset-0 rounded-t-xl opacity-0 transition-opacity group-hover:pointer-events-auto group-hover:opacity-100"
        style="background: rgba(0, 0, 0, 0.35)"
      >
        <div class="absolute top-2 left-2 flex gap-1" @click.stop>
          <UDropdownMenu :items="menuItems">
            <UButton
              color="neutral"
              variant="ghost"
              icon="i-heroicons-ellipsis-horizontal"
              class="bg-white/15 text-white hover:bg-white/30"
            />
          </UDropdownMenu>
          <UButton
            color="neutral"
            variant="ghost"
            icon="i-heroicons-share"
            class="bg-white/15 text-white hover:bg-white/30"
            @click="$emit('share', item)"
          />
        </div>

        <div v-if="item.product_url" class="absolute top-2 right-2" @click.stop>
          <UTooltip :text="t('items.open_store')">
            <UButton
              color="neutral"
              variant="ghost"
              icon="i-heroicons-shopping-bag"
              class="bg-white/15 text-white hover:bg-white/30"
              :to="item.product_url"
              target="_blank"
            />
          </UTooltip>
        </div>

        <Transition
          enter-active-class="animate-in fade-in-0 slide-in-from-bottom-2 duration-200 ease-out"
          leave-active-class="animate-out fade-out-0 slide-out-to-bottom-2 duration-150 ease-in"
        >
          <div v-if="item.is_reserved" class="absolute bottom-2 left-2" @click.stop>
            <Transition
              mode="out-in"
              enter-active-class="animate-in fade-in-0 duration-150 ease-out"
              leave-active-class="animate-out fade-out-0 duration-100 ease-in"
            >
              <UButton
                :key="item.is_fulfilled ? 'unfulfill' : 'fulfill'"
                color="neutral"
                variant="ghost"
                :label="item.is_fulfilled ? t('reservation.unfulfill') : t('items.fulfill')"
                class="bg-white/15 text-xs text-white hover:bg-white/30"
                @click="$emit('fulfill', item)"
              />
            </Transition>
          </div>
        </Transition>
      </div>
    </div>

    <div class="space-y-1 p-3">
      <p
        class="line-clamp-2 text-sm leading-tight font-semibold text-black dark:text-white"
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
  </div>
</template>

<script setup lang="ts">
import type { WishItemResponse } from '~/types/api'

const props = defineProps<{ item: WishItemResponse }>()
const emit = defineEmits<{
  select: [item: WishItemResponse]
  edit: [item: WishItemResponse]
  delete: [item: WishItemResponse]
  copy: [item: WishItemResponse]
  share: [item: WishItemResponse]
  fulfill: [item: WishItemResponse]
  'update-priority': [item: WishItemResponse, priority: number]
}>()

const { t } = useI18n()

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

const storeDomain = computed(() => {
  if (!props.item.product_url) return null

  try {
    return new URL(props.item.product_url).hostname.replace(/^www\./, '')
  } catch {
    return props.item.product_url
  }
})

const cardImages = computed(() => {
  const all = [
    ...(props.item.image_url ? [props.item.image_url] : []),
    ...(props.item.images ?? []),
  ]
  return all.slice(0, 3)
})

const priceDisplay = computed(() => {
  const { price_min, price_max, currency } = props.item

  if (!price_min && !price_max) return null

  if (price_min && price_max && price_min !== price_max) {
    return `${price_min}–${price_max} ${currency}`
  }

  return `${price_min || price_max} ${currency}`
})

const priorityMenuItems = computed(() => [
  [
    {
      label: `🙂 ${t('items.priority.normal')}`,
      onSelect: () => emit('update-priority', props.item, 0),
    },
    {
      label: `🥰 ${t('items.priority.high')}`,
      onSelect: () => emit('update-priority', props.item, 1),
    },
    {
      label: `😍 ${t('items.priority.must_have')}`,
      onSelect: () => emit('update-priority', props.item, 2),
    },
  ],
])

const menuItems = computed(() => [
  [
    {
      label: t('items.edit'),
      icon: 'i-heroicons-pencil-square',
      onSelect: () => emit('edit', props.item),
    },
    {
      label: t('items.copy'),
      icon: 'i-heroicons-document-duplicate',
      onSelect: () => emit('copy', props.item),
    },
    {
      label: t('items.share'),
      icon: 'i-heroicons-share',
      onSelect: () => emit('share', props.item),
    },
  ],
  [
    {
      label: t('items.delete'),
      icon: 'i-heroicons-trash',
      onSelect: () => emit('delete', props.item),
    },
  ],
])
</script>
