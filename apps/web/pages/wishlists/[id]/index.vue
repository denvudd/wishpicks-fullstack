<template>
  <div class="p-6 w-full">
    <!-- Loading skeleton -->
    <div v-if="isLoading" class="space-y-4">
      <USkeleton class="h-7 w-48 rounded-lg" />
      <USkeleton class="h-4 w-32 rounded-lg" />
    </div>

    <!-- Content -->
    <template v-else-if="current">
      <!-- Header -->
      <div class="flex items-start justify-between gap-4 mb-8 w-full">
        <div class="space-y-1">
          <h1 class="text-xl font-bold text-black dark:text-white">
            {{ current.title }}
          </h1>
          <p v-if="current.event_date" class="text-sm text-body-gray dark:text-muted-gray">
            {{ current.event_date }}
            <span v-if="current.event_type">
              · {{ t(`wishlists.event_type.${current.event_type}`) }}
            </span>
          </p>
        </div>
        <UButton
          variant="outline"
          color="neutral"
          icon="i-heroicons-cog-6-tooth"
          :label="t('wishlists.settings.title')"
          @click="settingsOpen = true"
        />
      </div>

      <!-- Items stub -->
      <UCard>
        <p class="text-sm text-body-gray dark:text-muted-gray">
          Items coming soon
        </p>
      </UCard>

      <!-- Settings modal -->
      <WishlistSettingsModal
        v-model:open="settingsOpen"
        :wishlist="current"
        @deleted="navigateTo(localePath('/dashboard'))"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

const { t } = useI18n()
const localePath = useLocalePath()
const route = useRoute()
const { current, isLoading, fetchOne } = useWishlists()

const settingsOpen = ref(false)

onMounted(async () => {
  const result = await fetchOne(route.params.id as string)
  if (!result) {
    await navigateTo(localePath('/dashboard'))
  }
})
</script>
