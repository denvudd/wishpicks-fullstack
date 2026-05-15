<template>
  <div class="flex gap-2">
    <UButton
      v-for="opt in choices"
      :key="opt.value"
      type="button"
      class="flex-1 gap-1 whitespace-normal"
      :variant="model === opt.value ? 'solid' : 'outline'"
      color="neutral"
      :aria-pressed="model === opt.value"
      @click="model = opt.value"
    >
      <span class="text-xl leading-none" aria-hidden="true">{{ opt.emoji }}</span>
      <span class="text-center text-xs leading-snug font-medium">
        {{ opt.label }}
      </span>
    </UButton>
  </div>
</template>

<script setup lang="ts">
const model = defineModel<number>({ default: 0 })

const { t } = useI18n()

const choices = computed(() => [
  { value: 0, emoji: '🙂', label: t('items.priority.normal') },
  { value: 1, emoji: '🥰', label: t('items.priority.high') },
  { value: 2, emoji: '😍', label: t('items.priority.must_have') },
])
</script>
