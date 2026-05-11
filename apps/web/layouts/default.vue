<template>
  <div class="min-h-screen bg-brand-white dark:bg-brand-black">
    <header
      class="sticky top-0 z-40 flex h-14 items-center justify-between border-b border-black/10 bg-brand-white px-4 dark:border-white/10 dark:bg-brand-black lg:px-6"
    >
      <NuxtLink
        :to="localePath('/')"
        class="font-heading text-lg font-bold tracking-tight text-black dark:text-white"
      >
        {{ $t('app.name') }}
      </NuxtLink>

      <div class="flex items-center gap-1">
        <UiColorModeToggle />
        <UiLanguageSwitcher />
      </div>
    </header>

    <main>
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
</script>
