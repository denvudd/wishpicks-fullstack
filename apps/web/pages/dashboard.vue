<template>
  <div class="p-6">
    <!-- Page header -->
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-black dark:text-white">
        {{ t('wishlists.title') }}
      </h1>
      <UButton
        icon="i-heroicons-plus"
        :label="t('wishlists.new')"
        @click="createOpen = true"
      />
    </div>

    <!-- Skeleton -->
    <div v-if="isLoading" class="grid grid-cols-2 md:grid-cols-3 gap-4">
      <USkeleton v-for="n in 3" :key="n" class="h-28 rounded-xl" />
    </div>

    <!-- Empty state -->
    <WishlistEmptyState
      v-else-if="wishlists.length === 0"
      @create="createOpen = true"
    />

    <!-- Grid -->
    <div v-else class="grid grid-cols-2 gap-x-6 gap-y-4 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 xl:gap-x-8 2xl:grid-cols-5">
      <WishlistCard
        v-for="wishlist in wishlists"
        :key="wishlist.id"
        :wishlist="wishlist"
      />
    </div>

    <!-- Create modal -->
    <WishlistCreateModal v-model:open="createOpen" />
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

const { t } = useI18n()
const { wishlists, isLoading, fetchList } = useWishlists()

const createOpen = ref(false)

onMounted(() => fetchList())
</script>
