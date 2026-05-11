<template>
  <UModal v-model:open="open" :title="t('reservation.reserve')">
    <template #body>
      <!-- Registered-only + not authenticated -->
      <div v-if="needsAuth" class="space-y-4">
        <p class="text-body-gray dark:text-muted-gray text-sm">
          {{ t('reservation.registered_only_prompt') }}
        </p>
        <div class="flex justify-end">
          <UButton
            color="neutral"
            :label="t('reservation.sign_in')"
            :to="localePath('/login')"
          />
        </div>
      </div>

      <!-- Authenticated: confirm -->
      <div v-else-if="isAuthenticated" class="space-y-4">
        <p class="text-body-gray dark:text-muted-gray text-sm">
          {{ item.title }}
        </p>
        <div class="flex justify-end gap-2">
          <UButton
            variant="outline"
            color="neutral"
            :label="t('items.delete_cancel')"
            @click="open = false"
          />
          <UButton
            color="neutral"
            :loading="isLoading"
            :label="t('reservation.confirm')"
            @click="submit"
          />
        </div>
      </div>

      <!-- Anonymous: name input -->
      <div v-else class="space-y-4">
        <UFormField :label="t('reservation.name_label')" :error="nameError">
          <UInput
            v-model="name"
            :placeholder="t('reservation.name_placeholder')"
            autofocus
            @keydown.enter="submit"
          />
        </UFormField>
        <div class="flex justify-end gap-2">
          <UButton
            variant="outline"
            color="neutral"
            :label="t('items.delete_cancel')"
            @click="open = false"
          />
          <UButton
            color="neutral"
            :loading="isLoading"
            :label="t('reservation.reserve')"
            @click="submit"
          />
        </div>
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { ReservationMode, SharedItemResponse } from '~/types/api'
import { useReservationsApi } from '~/composables/api/useReservationsApi'

const props = defineProps<{
  item: SharedItemResponse
  reservationMode: ReservationMode
  isAuthenticated: boolean
}>()

const emit = defineEmits<{
  reserved: [itemId: string, anonToken: string | null]
}>()

const open = defineModel<boolean>('open', { default: false })

const { t } = useI18n()
const localePath = useLocalePath()
const reservationsApi = useReservationsApi()

const name = ref('')
const nameError = ref<string | undefined>(undefined)
const isLoading = ref(false)

const needsAuth = computed(
  () => props.reservationMode === 'registered_only' && !props.isAuthenticated,
)

async function submit() {
  nameError.value = undefined

  if (!props.isAuthenticated && !name.value.trim()) {
    nameError.value = t('reservation.name_required')
    return
  }

  isLoading.value = true
  try {
    const res = await reservationsApi.reserve(
      props.item.id,
      props.isAuthenticated ? undefined : name.value.trim(),
    )
    emit('reserved', res.data.item_id, res.data.anon_token)
    open.value = false
    name.value = ''
  } finally {
    isLoading.value = false
  }
}
</script>
