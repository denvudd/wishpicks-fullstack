<template>
  <div class="p-6">
    <!-- Page header -->
    <div class="mb-4 flex items-center justify-between">
      <h1 class="text-xl font-bold text-black dark:text-white">
        {{ t('wishlists.title') }}
      </h1>
      <UButton
        v-if="activeTab === 'my'"
        icon="i-heroicons-plus"
        :label="t('wishlists.new')"
        @click="createOpen = true"
      />
    </div>

    <UTabs
      :items="tabs"
      :model-value="activeTab"
      color="neutral"
      variant="pill"
      size="sm"
      class="mb-6 w-fit"
      @update:model-value="(v) => { if (typeof v === 'string') setTab(v) }"
    />

    <!-- My wishlists -->
    <template v-if="activeTab === 'my'">
      <div v-if="isLoadingMy" class="grid grid-cols-2 gap-4 md:grid-cols-3">
        <USkeleton v-for="n in 3" :key="n" class="h-48 rounded-xl" />
      </div>
      <WishlistEmptyState
        v-else-if="wishlists.length === 0"
        @create="createOpen = true"
      />
      <div
        v-else
        class="grid grid-cols-2 gap-x-6 gap-y-4 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 xl:gap-x-8 2xl:grid-cols-5"
      >
        <WishlistCard
          v-for="wishlist in wishlists"
          :key="wishlist.id"
          :wishlist="wishlist"
          :href="`/wishlists/${wishlist.id}`"
        />
      </div>
    </template>

    <!-- Saved wishlists -->
    <template v-else-if="activeTab === 'saved'">
      <div v-if="isLoadingSaved" class="grid grid-cols-2 gap-4 md:grid-cols-3">
        <USkeleton v-for="n in 3" :key="n" class="h-48 rounded-xl" />
      </div>
      <div
        v-else-if="savedWishlists.length === 0"
        class="flex flex-col items-center justify-center py-16 text-center"
      >
        <p class="mb-1 text-sm font-semibold text-black dark:text-white">
          {{ t('saved.empty_wishlists_title') }}
        </p>
        <p class="text-body-gray dark:text-muted-gray text-xs">
          {{ t('saved.empty_wishlists_body') }}
        </p>
      </div>
      <div
        v-else
        class="grid grid-cols-2 gap-x-6 gap-y-4 md:grid-cols-3 lg:grid-cols-3 xl:grid-cols-4 xl:gap-x-8 2xl:grid-cols-5"
      >
        <WishlistCard
          v-for="wishlist in savedWishlists"
          :key="wishlist.id"
          :wishlist="wishlist"
          :can-save="true"
          :is-saved="true"
          @unsave="onUnsave(wishlist.id)"
        />
      </div>
    </template>

    <!-- Create modal -->
    <WishlistCreateModal v-model:open="createOpen" />
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const { wishlists, isLoading: isLoadingMy, fetchList } = useWishlists()
const { savedWishlists, isLoading: isLoadingSaved, fetchWishlists, unsaveWishlist } = useSaved()

const createOpen = ref(false)

const tabs = computed(() => [
  { label: t('saved.tab_my'), value: 'my' },
  { label: t('saved.tab_saved'), value: 'saved' },
])

const activeTab = ref<string>(route.query.tab === 'saved' ? 'saved' : 'my')

function setTab(tab: string) {
  activeTab.value = tab
  router.replace({ query: tab === 'my' ? {} : { tab } })
}

watch(activeTab, (tab) => {
  if (tab === 'saved') {
    fetchWishlists()
  }
}, { immediate: true })

async function onUnsave(id: string) {
  await unsaveWishlist(id)
}

onMounted(() => fetchList())
</script>
