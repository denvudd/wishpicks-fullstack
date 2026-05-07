<template>
  <nav class="p-3 w-full">
    <UTabs
      :items="tabItems"
      :model-value="activeTab"
      orientation="vertical"
      variant="pill"
      color="neutral"
      size="lg"
      class="w-full"
      :ui="{
        root: 'w-full block',
        list: 'w-full flex flex-col items-stretch bg-transparent p-0',
        trigger:
          'flex w-full justify-start rounded-lg text-sm font-medium text-body-gray dark:text-muted-gray data-[state=active]:text-black dark:data-[state=active]:text-white transition-[color,transform] duration-200 ease-out active:scale-[0.98]',
        indicator:
          'rounded-lg bg-hover-light dark:bg-white/5 shadow-none transition-[translate,height] duration-250 ease-out',
        leadingIcon:
          'inline-block transform-gpu transition-[transform,filter] duration-300 ease-out group-data-[state=active]:scale-105',
      }"
      @update:model-value="onTabChange"
    />
  </nav>
</template>

<script setup lang="ts">
const emit = defineEmits<{ navigate: [] }>()

const { t } = useI18n()
const route = useRoute()
const localePath = useLocalePath()

const navItems = [
  {
    to: '/dashboard',
    icon: 'i-heroicons-squares-2x2',
    label: 'nav.collections',
    itemClass: 'tab-dashboard',
  },
  {
    to: '/saved',
    icon: 'i-heroicons-globe-alt',
    label: 'nav.interesting',
    itemClass: 'tab-saved',
  },
  {
    to: '/profile',
    icon: 'i-heroicons-user',
    label: 'nav.profile',
    itemClass: 'tab-profile',
  },
  {
    to: '/reserved',
    icon: 'i-heroicons-gift',
    label: 'nav.reserved',
    itemClass: 'tab-reserved',
  },
  {
    to: '/settings',
    icon: 'i-heroicons-cog-6-tooth',
    label: 'nav.settings',
    itemClass: 'tab-settings',
  },
]

const defaultTab = '/dashboard'

const activeTab = computed(() => {
  const currentItem = navItems.find((item) => route.path === localePath(item.to))
  return currentItem?.to ?? defaultTab
})

const tabItems = computed(() =>
  navItems.map((item) => ({
    label: t(item.label),
    icon: item.icon,
    value: item.to,
    class: item.itemClass,
  })),
)

async function onTabChange(value: string | number) {
  if (typeof value !== 'string') return

  const targetPath = localePath(value)
  if (route.path !== targetPath) {
    await navigateTo(targetPath)
  }

  emit('navigate')
}
</script>

<style scoped>
/* Animate only tab leading icons, never the moving indicator */
:deep([data-slot='list'] > button[data-slot='trigger']:nth-of-type(1):hover [data-slot='leadingIcon']) {
  transform: rotate(-6deg) scale(1.12);
}

:deep([data-slot='list'] > button[data-slot='trigger']:nth-of-type(2):hover [data-slot='leadingIcon']) {
  animation: world-rotate 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

:deep([data-slot='list'] > button[data-slot='trigger']:nth-of-type(3):hover [data-slot='leadingIcon']) {
  transform: scale(1.14);
}

:deep([data-slot='list'] > button[data-slot='trigger']:nth-of-type(4):hover [data-slot='leadingIcon']) {
  transform: rotate(10deg) translateY(-1px) scale(1.1);
}

:deep([data-slot='list'] > button[data-slot='trigger']:nth-of-type(5):hover [data-slot='leadingIcon']) {
  transform: rotate(45deg) scale(1.08);
}

@keyframes world-rotate {
  from { transform: rotate(-180deg) scale(1); }
  to { transform: rotate(0deg) scale(1.14); }
}
</style>
