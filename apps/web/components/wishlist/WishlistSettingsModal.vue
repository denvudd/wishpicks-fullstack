<template>
  <component
    :is="dialogComponent"
    v-model:open="open"
    :title="t('wishlists.settings.title')"
  >
    <template #body>
      <!-- Tabs -->
      <UTabs
        :items="tabs"
        :model-value="activeTab"
        color="neutral"
        variant="pill"
        size="sm"
        class="mb-5"
        @update:model-value="
          (v) => {
            if (typeof v === 'string') activeTab = v
          }
        "
      />

      <div
        class="overflow-hidden transition-[height] duration-300 ease-[cubic-bezier(0.33,1,0.68,1)]"
        :style="
          tabShellHeight != null ? { height: `${tabShellHeight}px` } : undefined
        "
      >
        <div ref="tabInnerRef">
          <WishlistSettingsTabBasic
            v-if="activeTab === 'basic'"
            :wishlist="props.wishlist"
            @close="open = false"
            @deleted="handleDeleted"
          />

          <WishlistSettingsTabAccess
            v-if="activeTab === 'access'"
            :wishlist="props.wishlist"
            :open="open"
            @close="open = false"
          />

          <WishlistSettingsTabBooking
            v-if="activeTab === 'booking'"
            :wishlist="props.wishlist"
            @close="open = false"
          />
        </div>
      </div>
    </template>
  </component>
</template>

<script setup lang="ts">
import { resolveComponent } from 'vue'
import type { WishlistResponse } from '~/types/api'

const props = defineProps<{ wishlist: WishlistResponse }>()
const open = defineModel<boolean>('open', { default: false })
const emit = defineEmits<{ deleted: [] }>()

const { t } = useI18n()

const UModal = resolveComponent('UModal')
const UDrawer = resolveComponent('UDrawer')

const isMobile = ref(false)

onMounted(() => {
  isMobile.value = window.matchMedia('(max-width: 767px)').matches
})

const dialogComponent = computed(() => (isMobile.value ? UDrawer : UModal))

const activeTab = ref('basic')

const tabShellHeight = ref<number | null>(null)
const tabInnerRef = ref<HTMLElement | null>(null)

function measureTabPanelHeight() {
  const el = tabInnerRef.value
  if (!el || !open.value) return

  tabShellHeight.value = el.scrollHeight
}

watch([open, activeTab], async () => {
  if (!open.value) {
    tabShellHeight.value = null
    return
  }

  await nextTick()
  requestAnimationFrame(() => measureTabPanelHeight())
})

let tabPanelResizeObserver: ResizeObserver | null = null
let stopTabInnerWatch: (() => void) | null = null

onMounted(() => {
  tabPanelResizeObserver = new ResizeObserver(() => {
    if (open.value) measureTabPanelHeight()
  })

  stopTabInnerWatch = watch(
    tabInnerRef,
    (el, prev) => {
      if (prev && tabPanelResizeObserver) tabPanelResizeObserver.unobserve(prev)
      if (el && tabPanelResizeObserver) tabPanelResizeObserver.observe(el)
    },
    { flush: 'post', immediate: true }
  )
})

onBeforeUnmount(() => {
  stopTabInnerWatch?.()
  tabPanelResizeObserver?.disconnect()
})

const tabs = computed(() => [
  { label: t('wishlists.settings.tab_basic'), value: 'basic' },
  { label: t('wishlists.settings.tab_access'), value: 'access' },
  { label: t('wishlists.settings.tab_booking'), value: 'booking' },
])

function handleDeleted() {
  open.value = false
  emit('deleted')
}
</script>
