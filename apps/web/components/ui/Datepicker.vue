<script setup lang="ts">
import type { CalendarDate } from '@internationalized/date'
import {
  DateFormatter,
  getLocalTimeZone,
  parseDate,
} from '@internationalized/date'

const props = withDefaults(
  defineProps<{
    locale?: string
    placeholder?: string
  }>(),
  {
    locale: 'en-US',
    placeholder: '',
  },
)

const modelValue = defineModel<string>({ default: '' })

function parseIso(iso: string): CalendarDate | undefined {
  if (!iso || !/^\d{4}-\d{2}-\d{2}$/.test(iso)) return undefined
  try {
    return parseDate(iso)
  } catch {
    return undefined
  }
}

const selected = shallowRef<CalendarDate | undefined>(parseIso(modelValue.value))

watch(
  () => modelValue.value,
  (v) => {
    const parsed = parseIso(v)
    const cur = selected.value?.toString() ?? ''
    const next = parsed?.toString() ?? ''
    if (cur !== next) selected.value = parsed
  },
)

watch(selected, (v) => {
  const next = v?.toString() ?? ''
  if (next !== modelValue.value) modelValue.value = next
})

const df = computed(() =>
  new DateFormatter(props.locale, {
    dateStyle: 'medium',
  }),
)

function buttonLabel(): string {
  const v = selected.value
  if (!v) return props.placeholder
  return df.value.format(v.toDate(getLocalTimeZone()))
}
</script>

<template>
  <UPopover class="flex w-full">
    <UButton
      color="neutral"
      variant="subtle"
      icon="i-lucide-calendar"
      class="w-full justify-start rounded-lg bg-white dark:bg-black text-black dark:text-white focus:outline-none focus:ring-0"
    >
      {{ buttonLabel() }}
    </UButton>

    <template #content>
      <UCalendar v-model="selected" class="p-2" />
    </template>
  </UPopover>
</template>
