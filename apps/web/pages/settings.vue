<template>
  <div class="p-6">
    <div class="mx-auto max-w-lg space-y-8">
      <!-- Header -->
      <div>
        <h1 class="text-xl font-bold text-black dark:text-white">
          {{ t('settings.title') }}
        </h1>
        <p class="mt-1 text-sm text-body-gray dark:text-muted-gray">
          {{ user?.email }}
        </p>
      </div>

      <!-- Appearance -->
      <UCard>
        <template #header>
          <p class="text-sm font-semibold text-highlighted">
            {{ t('settings.appearance') }}
          </p>
        </template>

        <div class="space-y-5">
          <!-- Theme -->
          <div class="flex items-center justify-between gap-6">
            <div>
              <p class="text-sm font-medium text-default">
                {{ t('settings.theme_label') }}
              </p>
            </div>
            <ClientOnly>
              <USelect
                v-model="themePreference"
                :items="themeOptions"
                class="w-32"
              />
              <template #fallback>
                <div class="h-8 w-32 animate-pulse rounded-md bg-elevated" />
              </template>
            </ClientOnly>
          </div>

          <USeparator />

          <!-- Language -->
          <div class="flex items-center justify-between gap-6">
            <div>
              <p class="text-sm font-medium text-default">
                {{ t('settings.language_label') }}
              </p>
            </div>
            <USelect
              v-model="currentLocale"
              :items="localeOptions"
              class="w-32"
            />
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

const { t, locale, setLocale } = useI18n()
const colorMode = useColorMode()
const authStore = useAuthStore()
const user = computed(() => authStore.user)

const themePreference = computed({
  get: () => colorMode.preference,
  set: (val) => { colorMode.preference = val },
})

const themeOptions = computed(() => [
  { label: t('settings.theme_light'), value: 'light' },
  { label: t('settings.theme_dark'), value: 'dark' },
])

const currentLocale = computed({
  get: () => locale.value,
  set: (val) => setLocale(val as 'uk' | 'en'),
})

const localeOptions = [
  { label: 'Українська', value: 'uk' },
  { label: 'English', value: 'en' },
]
</script>
