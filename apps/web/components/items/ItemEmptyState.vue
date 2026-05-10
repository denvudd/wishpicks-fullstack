<template>
  <div class="flex flex-col items-center justify-center py-20 gap-4 text-center">
    <div class="w-14 h-14 rounded-full bg-chip-gray dark:bg-neutral-800 flex items-center justify-center">
      <UIcon name="i-heroicons-gift" class="w-7 h-7 text-muted-gray" />
    </div>
    <div class="space-y-1">
      <p class="font-semibold text-black dark:text-white">{{ t('items.empty_title') }}</p>
      <p class="text-sm text-body-gray dark:text-muted-gray">{{ t('items.empty_body') }}</p>
    </div>
    <UButton variant="outline" color="neutral" @click="$emit('create')">
      {{ t('items.empty_action') }}
    </UButton>
  </div>
</template>

<script setup lang="ts">
const { t } = useI18n()
defineEmits<{ create: [] }>()
</script>
