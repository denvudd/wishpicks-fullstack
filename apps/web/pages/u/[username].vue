<template>
  <div class="min-h-screen bg-brand-white dark:bg-brand-black p-6">
    <div class="max-w-2xl mx-auto">
      <!-- Back to top nav -->
      <div class="mb-8">
        <NuxtLink
          :to="localePath('/')"
          class="text-sm font-medium text-body-gray dark:text-muted-gray hover:text-black dark:hover:text-white transition-colors"
        >
          Wishpicks
        </NuxtLink>
      </div>

      <!-- Identity -->
      <div class="flex items-center gap-5 mb-10">
        <div
          class="size-20 rounded-full bg-chip-gray dark:bg-white/10 flex items-center justify-center shrink-0"
        >
          <UIcon name="i-heroicons-user" class="size-10 text-muted-gray" />
        </div>
        <div>
          <h1 class="text-2xl font-bold text-black dark:text-white">
            @{{ username }}
          </h1>
        </div>
      </div>

      <!-- Wishlists stub -->
      <section class="mb-8">
        <h2 class="text-lg font-bold text-black dark:text-white mb-3">
          {{ $t('profile.wishlists_section') }}
        </h2>
        <UCard>
          <p class="text-sm text-body-gray dark:text-muted-gray">
            {{ $t('profile.coming_soon') }}
          </p>
        </UCard>
      </section>

      <!-- Wish board stub -->
      <section>
        <h2 class="text-lg font-bold text-black dark:text-white mb-3">
          {{ $t('profile.board_section') }}
        </h2>
        <UCard>
          <p class="text-sm text-body-gray dark:text-muted-gray">
            {{ $t('profile.coming_soon') }}
          </p>
        </UCard>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const localePath = useLocalePath()

const username = computed(() => route.params.username as string)

useSeoMeta({ title: () => `@${username.value} — Wishpicks` })
</script>
