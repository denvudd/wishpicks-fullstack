<template>
  <div class="cursor-pointer space-y-1">
    <div
      class="group relative overflow-hidden rounded-xl"
      @click="navigateTo(localePath(href ?? `/w/${wishlist.slug}`))"
    >
      <!-- Image grid (square) -->
      <div class="bg-chip-gray relative aspect-square dark:bg-neutral-800">
        <!-- 0 images -->
        <div
          v-if="images.length === 0"
          class="flex h-full items-center justify-center"
        >
          <UIcon name="i-heroicons-gift" class="text-muted-gray h-10 w-10" />
        </div>

        <!-- 1 image -->
        <img
          v-else-if="images.length === 1"
          :src="images[0]"
          :alt="wishlist.title"
          class="h-full w-full object-cover"
        />

        <!-- 2 images -->
        <div
          v-else-if="images.length === 2"
          class="grid h-full grid-cols-2 gap-px"
        >
          <img
            v-for="(src, i) in images"
            :key="i"
            :src="src"
            :alt="wishlist.title"
            class="h-full w-full object-cover"
          />
        </div>

        <!-- 3+ images: 5-col × 2-row asymmetric grid -->
        <div v-else class="grid h-full grid-cols-5 grid-rows-2 gap-0.5">
          <img
            :src="images[0]"
            :alt="wishlist.title"
            class="col-span-3 col-start-1 row-span-2 row-start-1 h-full w-full object-cover object-center"
          />
          <img
            :src="images[1]"
            :alt="wishlist.title"
            class="col-span-2 col-start-4 row-start-1 h-full w-full object-cover object-center"
          />
          <img
            :src="images[2]"
            :alt="wishlist.title"
            class="col-span-2 col-start-4 row-start-2 h-full w-full object-cover object-center"
          />
        </div>

        <!-- Hover overlay with bookmark button -->
        <div
          v-if="canSave"
          class="absolute inset-0 bg-black/35 opacity-0 transition-opacity group-hover:opacity-100"
        >
          <div class="absolute top-2 right-2" @click.stop>
            <UButton
              :icon="
                isSaved ? 'i-heroicons-bookmark-solid' : 'i-heroicons-bookmark'
              "
              color="neutral"
              variant="ghost"
              size="sm"
              class="bg-white/15 text-white hover:bg-white/30"
              @click="isSaved ? $emit('unsave') : $emit('save')"
            />
          </div>
        </div>
      </div>
    </div>
    <div class="space-y-1 p-3">
      <p class="line-clamp-2 text-sm font-semibold text-black dark:text-white">
        {{ wishlist.title }}
      </p>
      <p class="text-body-gray dark:text-muted-gray text-xs">
        {{ t('wishlists.items_count', wishlist.item_count) }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { WishlistResponse, SavedWishlistResponse } from '~/types/api'

const props = withDefaults(
  defineProps<{
    wishlist: WishlistResponse | SavedWishlistResponse
    canSave?: boolean
    isSaved?: boolean
    href?: string
  }>(),
  { canSave: false, isSaved: false }
)

defineEmits<{
  save: []
  unsave: []
}>()

const { t } = useI18n()
const localePath = useLocalePath()

const images = computed(() => props.wishlist.preview_images ?? [])
</script>
