<template>
  <div class="min-h-screen flex flex-col">
    <header class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-800">
      <span class="text-xl font-bold tracking-tight">{{ $t('app.name') }}</span>
      <div class="flex items-center gap-3">
        <LanguageSwitcher />
        <UButton
          :icon="colorMode.value === 'dark' ? 'i-lucide-sun' : 'i-lucide-moon'"
          variant="ghost"
          color="neutral"
          @click="colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'"
        />
      </div>
    </header>

    <main class="flex-1 flex flex-col items-center justify-center gap-8 px-6 py-16 text-center">
      <div class="max-w-lg space-y-4">
        <h1 class="text-5xl font-bold leading-tight">
          {{ $t('landing.title') }}
        </h1>
        <p class="text-lg text-gray-500 dark:text-gray-400">
          {{ $t('landing.tagline') }}
        </p>
      </div>

      <div class="flex flex-wrap gap-3 justify-center">
        <UButton
          size="lg"
          variant="outline"
          :to="localePath('/login')"
        >
          {{ $t('landing.login') }}
        </UButton>
        <UButton
          size="lg"
          :to="localePath('/register')"
        >
          {{ $t('landing.register') }}
        </UButton>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const colorMode = useColorMode()
</script>
