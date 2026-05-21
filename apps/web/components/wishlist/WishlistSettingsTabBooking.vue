<template>
  <div class="space-y-5">
    <UiAlert
      :show="!!error"
      color="error"
      variant="soft"
      :description="error ?? ''"
    />

    <URadioGroup
      v-model="form.reservation_mode"
      :legend="t('wishlists.reservation.label')"
      :items="reservationOptions"
      color="neutral"
    />

    <UButton
      class="w-full"
      :loading="saving"
      :label="
        saving ? t('wishlists.settings.saving') : t('wishlists.settings.save')
      "
      @click="save"
    />
  </div>
</template>

<script setup lang="ts">
import type { ReservationMode, WishlistResponse } from '~/types/api'

const props = defineProps<{
  wishlist: WishlistResponse
}>()
const emit = defineEmits<{
  (e: 'close'): void
}>()

const { t } = useI18n()
const { update } = useWishlists()

const reservationOptions = computed(() => [
  {
    value: 'anonymous',
    label: t('wishlists.reservation.anonymous'),
    description: t('wishlists.reservation.anonymous_desc'),
  },
  {
    value: 'registered_only',
    label: t('wishlists.reservation.registered_only'),
    description: t('wishlists.reservation.registered_only_desc'),
  },
])

const form = reactive({
  reservation_mode: props.wishlist.reservation_mode as ReservationMode,
})
const saving = ref(false)
const error = ref<string | null>(null)

watch(
  () => props.wishlist.reservation_mode,
  (reservationMode) => {
    form.reservation_mode = reservationMode as ReservationMode
  }
)

async function save() {
  saving.value = true
  error.value = null
  
  try {
    await update(props.wishlist.id, {
      reservation_mode: form.reservation_mode,
    })

    emit('close')
  } catch {
    error.value = t('wishlists.errors.unknown')
  } finally {
    saving.value = false
  }
}
</script>
