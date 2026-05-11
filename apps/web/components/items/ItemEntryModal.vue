<template>
  <component
    :is="dialogComponent"
    v-model:open="open"
    :title="t('items.entry_title')"
  >
    <template #body>
      <div class="space-y-4">
        <UAlert
          v-if="isUrl"
          color="neutral"
          variant="soft"
          :description="t('items.entry_url_note')"
        />
        <UFormField :label="t('items.fields.title')">
          <UInput
            v-model="input"
            :placeholder="t('items.entry_placeholder')"
            autofocus
            @keydown.enter="proceed"
          />
        </UFormField>
      </div>
    </template>

    <template #footer>
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

const open = defineModel<boolean>('open', { default: false })
const emit = defineEmits<{
  proceed: [payload: { title: string; productUrl: string | null }]
}>()

const { t } = useI18n()

const UModal = resolveComponent('UModal')
const UDrawer = resolveComponent('UDrawer')
const isMobile = ref(false)

onMounted(() => {
  isMobile.value = window.matchMedia('(max-width: 767px)').matches
})

const dialogComponent = computed(() => (isMobile.value ? UDrawer : UModal))

const input = ref('')

const isUrl = computed(() => {
  const v = input.value.trim()
  return v.startsWith('http://') || v.startsWith('https://')
})

function proceed() {
  const v = input.value.trim()
  if (!v) return
  emit('proceed', {
    title: isUrl.value ? '' : v,
    productUrl: isUrl.value ? v : null,
  })
  input.value = ''
  open.value = false
}

watch(open, (val) => {
  if (!val) input.value = ''
})
</script>
