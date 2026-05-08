<template>
  <UCard
    :ui="{ body: 'p-4' }"
    class="cursor-pointer transition-shadow hover:shadow-md"
    @click="navigateTo(localePath(`/wishlists/${props.wishlist.id}`))"
  >
    <template #footer>
      <div class="space-y-2">
        <div class="flex w-full items-center justify-between">
          <h3
            class="line-clamp-2 text-sm leading-snug font-semibold text-black dark:text-white"
          >
            {{ props.wishlist.title }}
          </h3>
          <div class="flex items-start justify-between gap-2">
            <UBadge
              :label="t(`wishlists.visibility.${props.wishlist.visibility}`)"
              color="neutral"
              variant="subtle"
              size="sm"
              class="shrink-0"
            />
          </div>
        </div>

        <p class="text-body-gray dark:text-muted-gray text-xs">
          {{ t('wishlists.items_count', props.wishlist.item_count) }}
        </p>

        <p
          v-if="props.wishlist.event_date"
          class="text-body-gray dark:text-muted-gray text-xs"
        >
          {{ props.wishlist.event_date }}
          <span v-if="props.wishlist.event_type">
            · {{ t(`wishlists.event_type.${props.wishlist.event_type}`) }}
          </span>
        </p>
      </div>
    </template>
  </UCard>
</template>

<script setup lang="ts">
import type { WishlistResponse } from '~/types/api'

const props = defineProps<{ wishlist: WishlistResponse }>()

const { t } = useI18n()
const localePath = useLocalePath()
</script>
