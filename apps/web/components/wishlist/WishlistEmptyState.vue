<template>
  <div class="flex flex-col items-center justify-center py-20 text-center space-y-4">
    <div class="size-16 rounded-full bg-chip-gray dark:bg-white/10 flex items-center justify-center">
      <UIcon name="i-heroicons-gift" class="size-8 text-muted-gray" />
    </div>
    <div class="space-y-1">
      <p class="font-semibold text-black dark:text-white">
        {{ t('wishlists.empty_title') }}
      </p>
      <p class="text-sm text-body-gray dark:text-muted-gray">
        {{ t('wishlists.empty_body') }}
      </p>
    </div>
    <UButton :label="t('wishlists.new')" @click="$emit('create')" />
  </div>
</template>

<script setup lang="ts">
const { t } = useI18n()
defineEmits<{ create: [] }>()
</script>
