<template>
  <div class="flex gap-1 text-sm">
    <button
      v-for="loc in availableLocales"
      :key="loc.code"
      class="px-1 transition-opacity"
      :class="loc.code === locale ? 'font-semibold' : 'opacity-50 hover:opacity-80'"
      @click="setLocale(loc.code as 'uk' | 'en')"
    >
      {{ loc.code.toUpperCase() }}
    </button>
  </div>
</template>

<script setup lang="ts">
const { locale, locales, setLocale } = useI18n()
const availableLocales = computed(() => locales.value)
</script>
