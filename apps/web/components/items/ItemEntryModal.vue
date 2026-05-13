<template>
  <component
    :is="dialogComponent"
    v-model:open="open"
    :title="phase === 'idle' ? t('items.entry_title') : ''"
    :dismissible="phase === 'idle'"
  >
    <template #body>
      <Transition
        mode="out-in"
        enter-active-class="animate-in fade-in-0 slide-in-from-bottom-2 duration-200 ease-out"
        leave-active-class="animate-out fade-out-0 slide-out-to-top-2 duration-150 ease-in"
      >
        <!-- idle -->
        <div v-if="phase === 'idle'" key="idle" class="space-y-4">
          <UFormField :label="t('items.fields.title')">
            <UInput
              v-model="input"
              :placeholder="t('items.entry_placeholder')"
              autofocus
              @keydown.enter="proceed"
            />
          </UFormField>
        </div>

        <!-- scanning -->
        <div v-else-if="phase === 'scanning'" key="scanning" class="flex flex-col items-center py-6 text-center">
          <UIcon
            name="i-heroicons-arrow-path"
            class="h-8 w-8 animate-spin text-black dark:text-white"
          />
          <div class="mt-4 space-y-1">
            <p class="text-sm font-semibold text-black dark:text-white">
              {{ t('items.scanning.title') }}
            </p>
            <p class="max-w-[200px] truncate text-xs text-muted-gray">
              {{ hostname }}
            </p>
          </div>
        </div>

        <!-- success -->
        <div v-else-if="phase === 'success'" key="success" class="flex flex-col items-center py-6 text-center">
          <UIcon
            name="i-heroicons-check-circle"
            class="h-8 w-8 text-black dark:text-white"
            style="animation: wp-spin-in 0.45s cubic-bezier(0.22, 1, 0.36, 1) both"
          />
          <div class="mt-4 space-y-1">
            <p class="text-sm font-semibold text-black dark:text-white">
              {{ t('items.scanning.success') }}
            </p>
          </div>
        </div>

        <!-- error -->
        <div v-else key="error" class="flex w-full flex-col items-center gap-4 py-6 text-center">
          <UIcon
            name="i-heroicons-exclamation-circle"
            class="h-8 w-8 text-black dark:text-white"
          />
          <div class="space-y-1">
            <p class="text-sm font-semibold text-black dark:text-white">
              {{ t('items.scanning.error') }}
            </p>
            <p class="text-xs text-muted-gray">
              {{ t('items.scanning.error_body') }}
            </p>
          </div>
          <UButton
            class="w-full"
            color="neutral"
            :label="t('items.scanning.proceed')"
            @click="onErrorProceed"
          />
        </div>
      </Transition>
    </template>

    <template v-if="phase === 'idle'" #footer>
      <UButton
        class="w-full"
        :disabled="!input.trim()"
        :label="t('items.entry_continue')"
        @click="proceed"
      />
    </template>
  </component>
</template>

<script setup lang="ts">
import { resolveComponent } from 'vue'
import type { ParseUrlData } from '~/types/api'

const props = defineProps<{
  parseUrlFn?: (url: string) => Promise<ParseUrlData>
}>()

const open = defineModel<boolean>('open', { default: false })
const emit = defineEmits<{
  proceed: [payload: { title: string; productUrl: string | null; parsedData?: ParseUrlData | null }]
}>()

const { t } = useI18n()

const UModal = resolveComponent('UModal')
const UDrawer = resolveComponent('UDrawer')
const isMobile = ref(false)

onMounted(() => {
  isMobile.value = window.matchMedia('(max-width: 767px)').matches
})

const dialogComponent = computed(() => (isMobile.value ? UDrawer : UModal))

type Phase = 'idle' | 'scanning' | 'success' | 'error'
const phase = ref<Phase>('idle')
const input = ref('')
const scannedData = ref<ParseUrlData | null>(null)

const isUrl = computed(() => {
  const v = input.value.trim()
  return v.startsWith('http://') || v.startsWith('https://')
})

const hostname = computed(() => {
  try {
    return new URL(input.value.trim()).hostname.replace('www.', '')
  } catch {
    return input.value.trim()
  }
})

async function proceed() {
  const v = input.value.trim()
  if (!v) return

  if (isUrl.value && props.parseUrlFn) {
    phase.value = 'scanning'
    try {
      const data = await props.parseUrlFn(v)
      scannedData.value = data
      phase.value = 'success'
      setTimeout(() => {
        emit('proceed', { title: '', productUrl: v, parsedData: data })
        reset()
      }, 800)
    } catch {
      phase.value = 'error'
    }
  } else {
    emit('proceed', {
      title: isUrl.value ? '' : v,
      productUrl: isUrl.value ? v : null,
    })
    reset()
  }
}

function onErrorProceed() {
  const v = input.value.trim()
  emit('proceed', { title: '', productUrl: v, parsedData: null })
  reset()
}

function reset() {
  input.value = ''
  open.value = false
  phase.value = 'idle'
  scannedData.value = null
}

watch(open, (val) => {
  if (!val) {
    input.value = ''
    phase.value = 'idle'
    scannedData.value = null
  }
})
</script>
