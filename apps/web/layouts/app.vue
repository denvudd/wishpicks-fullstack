<template>
  <div class="min-h-screen bg-brand-white dark:bg-brand-black">
    <LayoutAppHeader @open-sidebar="sidebarOpen = true" />

    <div class="flex">
      <!-- Desktop sidebar (lg+) — always visible -->
      <aside
        class="hidden lg:block w-56 shrink-0 sticky top-16 h-[calc(100vh-4rem)] overflow-y-auto border-r border-black/10 dark:border-white/10"
      >
        <LayoutAppSidebar />
      </aside>

      <!-- Page content -->
      <main class="flex-1 min-w-0">
        <slot />
      </main>
    </div>

    <!-- Mobile/tablet USlideover drawer -->
    <USlideover v-model:open="sidebarOpen" side="left">
      <div class="flex flex-col h-full w-56 bg-brand-white dark:bg-brand-black">
        <div
          class="flex items-center justify-between px-4 h-16 border-b border-black/10 dark:border-white/10 shrink-0"
        >
          <span class="font-bold font-heading text-black dark:text-white">
            {{ $t('app.name') }}
          </span>
          <UButton
            variant="ghost"
            color="neutral"
            icon="i-heroicons-x-mark"
            @click="sidebarOpen = false"
          />
        </div>
        <LayoutAppSidebar @navigate="sidebarOpen = false" />
      </div>
    </USlideover>
  </div>
</template>

<script setup lang="ts">
const sidebarOpen = ref(false)
</script>
