<template>
  <component
    :is="dialogComponent"
    v-model:open="open"
    :title="t('wishlists.create.title')"
  >
    <template #body>
      <div class="space-y-6">
        <UAlert
          v-if="errorCode"
          color="error"
          variant="soft"
          :description="t(`wishlists.errors.${errorCode}`)"
        />

        <UFormField :label="t('wishlists.create.name_label')">
          <UInput
            v-model="form.title"
            :placeholder="t('wishlists.create.name_placeholder')"
            :maxlength="100"
          />
        </UFormField>

        <URadioGroup
          v-model="form.visibility"
          :legend="t('wishlists.visibility.label')"
          :items="visibilityOptions"
          color="neutral"
        />

        <URadioGroup
          v-model="form.reservation_mode"
          :legend="t('wishlists.reservation.label')"
          :items="reservationOptions"
          color="neutral"
        />
      </div>
    </template>

    <template #footer>
      <UButton
        class="w-full"
        :loading="submitting"
        :disabled="!form.title.trim()"
        :label="submitting ? t('wishlists.create.submitting') : t('wishlists.create.submit')"
        @click="submit"
      />
    </template>
  </component>
</template>

<script setup lang="ts">
import { resolveComponent } from 'vue'
import type { ApiFetchError, WishlistVisibility, ReservationMode } from '~/types/api'

const open = defineModel<boolean>('open', { default: false })
defineEmits<{ created: [] }>()

const { t } = useI18n()
const { create } = useWishlists()

const UModal = resolveComponent('UModal')
const UDrawer = resolveComponent('UDrawer')

const isMobile = ref(false)

onMounted(() => {
  isMobile.value = window.matchMedia('(max-width: 767px)').matches
})

const dialogComponent = computed(() => isMobile.value ? UDrawer : UModal)

const form = reactive({
  title: '',
  visibility: 'link_only' as WishlistVisibility,
  reservation_mode: 'anonymous' as ReservationMode,
})

const submitting = ref(false)
const errorCode = ref<string | null>(null)

const visibilityOptions = computed(() => [
  { value: 'public', label: t('wishlists.visibility.public'), description: t('wishlists.visibility.public_desc') },
  { value: 'link_only', label: t('wishlists.visibility.link_only'), description: t('wishlists.visibility.link_only_desc') },
  { value: 'private', label: t('wishlists.visibility.private'), description: t('wishlists.visibility.private_desc') },
])

const reservationOptions = computed(() => [
  { value: 'anonymous', label: t('wishlists.reservation.anonymous'), description: t('wishlists.reservation.anonymous_desc') },
  { value: 'registered_only', label: t('wishlists.reservation.registered_only'), description: t('wishlists.reservation.registered_only_desc') },
])

async function submit() {
  if (!form.title.trim()) return
  submitting.value = true
  errorCode.value = null
  try {
    await create({
      title: form.title.trim(),
      visibility: form.visibility,
      reservation_mode: form.reservation_mode,
    })
    form.title = ''
    form.visibility = 'link_only'
    form.reservation_mode = 'anonymous'
    open.value = false
  } catch (err: unknown) {
    const code = (err as ApiFetchError)?.data?.error?.code
    errorCode.value = code === 'WISHLIST_LIMIT_REACHED' ? code : 'unknown'
  } finally {
    submitting.value = false
  }
}
</script>
