<template>
  <header
    class="bg-brand-white dark:bg-brand-black sticky top-0 z-40 flex h-16 items-center justify-between border-b border-black/10 px-4 lg:px-6 dark:border-white/10"
  >
    <!-- Left: hamburger (mobile/tablet) + logo -->
    <div class="flex items-center gap-3">
      <UButton
        class="lg:hidden"
        variant="ghost"
        color="neutral"
        icon="i-heroicons-bars-3"
        aria-label="Menu"
        @click="$emit('open-sidebar')"
      />
      <NuxtLink
        :to="localePath('/dashboard')"
        class="font-heading text-lg font-bold tracking-tight text-black dark:text-white"
      >
        {{ $t('app.name') }}
      </NuxtLink>
    </div>

    <!-- Right: theme toggle + avatar dropdown -->
    <div class="flex items-center gap-2">
      <UiColorModeToggle />
      <UDropdownMenu :items="menuItems">
        <UAvatar
          :src="user?.avatar_url ?? undefined"
          :alt="displayName"
          size="sm"
          class="cursor-pointer rounded-full ring-2 ring-transparent transition-all hover:ring-black/20 dark:hover:ring-white/20"
        />
      </UDropdownMenu>
    </div>
  </header>
</template>

<script setup lang="ts">
defineEmits<{ 'open-sidebar': [] }>()

const { t } = useI18n()
const localePath = useLocalePath()
const { user, displayName, logout } = useAuth()

const menuItems = computed(() => [
  [
    {
      label: t('nav.settings'),
      icon: 'i-heroicons-cog-6-tooth',
      onSelect: () => navigateTo(localePath('/settings')),
    },
  ],
  [
    {
      label: t('auth.logout'),
      icon: 'i-heroicons-arrow-right-on-rectangle',
      onSelect: logout,
    },
  ],
])
</script>
