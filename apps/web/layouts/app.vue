<template>
  <div class="bg-brand-white dark:bg-brand-black">
    <LayoutAppHeader @open-sidebar="sidebarOpen = true" />

    <UDashboardGroup :ui="{ base: 'relative flex overflow-visible' }">
      <UDashboardSidebar
        v-model:open="sidebarOpen"
        mode="slideover"
        :ui="{
          root: 'relative hidden lg:flex flex-col sticky top-16 h-[calc(100dvh-4rem)] min-w-16 w-(--width) shrink-0 bg-brand-white dark:bg-brand-black border-r border-black/10 dark:border-white/10',
          body: 'flex flex-col flex-1 overflow-y-auto p-0',
        }"
      >
        <LayoutAppSidebar @navigate="sidebarOpen = false" />
      </UDashboardSidebar>

      <main class="flex-1 min-w-0">
        <slot />
      </main>
    </UDashboardGroup>
  </div>
</template>

<script setup lang="ts">
const sidebarOpen = ref(false)
</script>
