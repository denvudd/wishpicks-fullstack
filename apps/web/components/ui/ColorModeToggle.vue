<template>
  <button
    class="theme-toggle flex h-9 w-9 items-center justify-center rounded-full text-black transition-colors duration-200 hover:bg-chip-gray dark:text-white dark:hover:bg-white/10"
    :aria-label="ariaLabel"
    @click="cycle"
  >
    <ClientOnly>
      <Transition name="wp-spinner" mode="out-in">
        <UIcon :key="icon" :name="icon" class="h-4 w-4" />
      </Transition>
      <template #fallback>
        <UIcon name="i-lucide-monitor" class="h-4 w-4" />
      </template>
    </ClientOnly>
  </button>
</template>

<script setup lang="ts">
const colorMode = useColorMode()
const { t } = useI18n()

const CYCLE: Array<'light' | 'dark'> = ['dark', 'light']

const normalizedPreference = computed<'light' | 'dark'>(() => {
  return colorMode.preference === 'light' ? 'light' : 'dark'
})

const icon = computed(() => {
  return normalizedPreference.value === 'light' ? 'i-lucide-sun' : 'i-lucide-moon'
})

const ariaLabel = computed(() => {
  return normalizedPreference.value === 'light'
    ? t('theme.switch_to_dark')
    : t('theme.switch_to_light')
})

function cycle() {
  const current = CYCLE.indexOf(normalizedPreference.value)
  colorMode.preference = CYCLE[(current + 1) % CYCLE.length] ?? 'dark'
}
</script>

<style scoped>
.theme-toggle {
  transition:
    background 0.15s,
    transform 0.1s cubic-bezier(0.22, 1, 0.36, 1);
}
.theme-toggle:hover {
  transform: rotate(18deg);
}
</style>
