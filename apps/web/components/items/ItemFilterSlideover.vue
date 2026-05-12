<template>
  <USlideover
    :open="open"
    :title="t('items.filters.title')"
    side="right"
    @update:open="$emit('update:open', $event)"
  >
    <template #body>
      <div class="space-y-6 py-2">
        <!-- Reservation status -->
        <div class="space-y-3">
          <p class="text-sm font-medium text-black dark:text-white">
            {{ t('items.filters.reservation_status') }}
          </p>
          <div class="space-y-2">
            <UCheckbox
              :model-value="modelValue.is_reserved === false"
              :label="t('items.filters.not_reserved')"
              @update:model-value="toggleReservation(false)"
            />
            <UCheckbox
              :model-value="modelValue.is_reserved === true"
              :label="t('items.filters.reserved')"
              @update:model-value="toggleReservation(true)"
            />
          </div>
        </div>

        <UDivider />

        <!-- Fulfillment status -->
        <div class="space-y-3">
          <p class="text-sm font-medium text-black dark:text-white">
            {{ t('items.filters.fulfillment_status') }}
          </p>
          <div class="space-y-2">
            <UCheckbox
              :model-value="modelValue.is_fulfilled === false"
              :label="t('items.filters.not_fulfilled')"
              @update:model-value="toggleFulfillment(false)"
            />
            <UCheckbox
              :model-value="modelValue.is_fulfilled === true"
              :label="t('items.filters.fulfilled')"
              @update:model-value="toggleFulfillment(true)"
            />
          </div>
        </div>

        <UDivider />

        <!-- Priority -->
        <div class="space-y-3">
          <p class="text-sm font-medium text-black dark:text-white">
            {{ t('items.filters.priority') }}
          </p>
          <div class="flex gap-2">
            <UButton
              v-for="opt in priorityOptions"
              :key="opt.value"
              type="button"
              class="flex-1 gap-1 whitespace-normal"
              :variant="modelValue.priority.includes(opt.value) ? 'solid' : 'outline'"
              color="neutral"
              :aria-pressed="modelValue.priority.includes(opt.value)"
              @click="togglePriority(opt.value)"
            >
              <span class="text-xl leading-none" aria-hidden="true">{{ opt.emoji }}</span>
              <span class="text-center text-xs leading-snug font-medium">{{ opt.label }}</span>
            </UButton>
          </div>
        </div>

        <!-- Store -->
        <template v-if="availableStores.length > 0">
          <UDivider />
          <div class="space-y-3">
            <p class="text-sm font-medium text-black dark:text-white">
              {{ t('items.filters.store') }}
            </p>
            <div class="space-y-2">
              <UCheckbox
                v-for="store in availableStores"
                :key="store"
                :model-value="modelValue.store === store"
                :label="store"
                @update:model-value="toggleStore(store)"
              />
            </div>
          </div>
        </template>
      </div>
    </template>
  </USlideover>
</template>

<script setup lang="ts">
import type { ItemFilters } from '~/types/api'

const props = defineProps<{
  open: boolean
  modelValue: ItemFilters
  availableStores: string[]
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'update:modelValue': [value: ItemFilters]
}>()

const { t } = useI18n()

const priorityOptions = computed(() => [
  { value: 0, emoji: '🙂', label: t('items.priority.normal') },
  { value: 1, emoji: '🥰', label: t('items.priority.high') },
  { value: 2, emoji: '😍', label: t('items.priority.must_have') },
])

function toggleReservation(value: boolean) {
  const current = props.modelValue.is_reserved
  emit('update:modelValue', {
    ...props.modelValue,
    is_reserved: current === value ? null : value,
  })
}

function toggleFulfillment(value: boolean) {
  const current = props.modelValue.is_fulfilled
  emit('update:modelValue', {
    ...props.modelValue,
    is_fulfilled: current === value ? null : value,
  })
}

function togglePriority(value: number) {
  const current = props.modelValue.priority
  const next = current.includes(value)
    ? current.filter((p) => p !== value)
    : [...current, value]
  emit('update:modelValue', { ...props.modelValue, priority: next })
}

function toggleStore(store: string) {
  emit('update:modelValue', {
    ...props.modelValue,
    store: props.modelValue.store === store ? null : store,
  })
}
</script>
