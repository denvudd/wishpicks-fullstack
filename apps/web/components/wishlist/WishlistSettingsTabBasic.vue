<template>
  <div class="space-y-5">
    <UiAlert
      :show="!!error"
      color="error"
      variant="soft"
      :description="error"
    />

    <UFormField :label="t('wishlists.create.name_label')">
      <UInput v-model="form.title" :maxlength="100" />
    </UFormField>

    <UFormField :label="t('wishlists.settings.description_label')">
      <UTextarea
        v-model="form.description"
        :placeholder="t('wishlists.settings.description_placeholder')"
        :rows="3"
      />
    </UFormField>

    <UFormField :label="t('wishlists.settings.event_type_label')">
      <USelect v-model="form.event_type" :items="eventTypeOptions" />
    </UFormField>

    <UFormField :label="t('wishlists.settings.event_date_label')">
      <UiDatepicker
        v-model="form.event_date"
        :locale="eventDateLocale"
        :placeholder="t('wishlists.settings.event_date_placeholder')"
      />
    </UFormField>

    <UAlert
      variant="soft"
      color="error"
      :title="t('wishlists.settings.delete')"
      :description="t('wishlists.settings.delete_confirm_body')"
      :actions="[
        {
          label: deleting
            ? t('wishlists.settings.deleting')
            : t('wishlists.settings.delete_confirm_yes'),
          color: 'error',
          onClick: confirmDelete,
        },
      ]"
    >
      <UButton
        variant="soft"
        color="error"
        :label="t('wishlists.settings.delete')"
        @click="showDeleteConfirm = true"
      />
    </UAlert>

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
import type { EventType, WishlistResponse } from '~/types/api'

const emit = defineEmits<{
  deleted: [],
  close: [],
}>()

const { t, locale: i18nLocale } = useI18n()
const { update, remove } = useWishlists()

const eventDateLocale = computed(() =>
  i18nLocale.value === 'uk' ? 'uk-UA' : 'en-US'
)
const eventTypeOptions = computed(() => [
  { label: t('wishlists.settings.event_type_none'), value: null },
  { label: t('wishlists.event_type.birthday'), value: 'birthday' },
  { label: t('wishlists.event_type.wedding'), value: 'wedding' },
  { label: t('wishlists.event_type.anniversary'), value: 'anniversary' },
  { label: t('wishlists.event_type.new_year'), value: 'new_year' },
  { label: t('wishlists.event_type.other'), value: 'other' },
])

const props = defineProps<{
  wishlist: WishlistResponse
}>()

const form = reactive({
  title: props.wishlist.title,
  description: props.wishlist.description ?? '',
  event_type: props.wishlist.event_type as EventType | null,
  event_date: props.wishlist.event_date ?? '',
})
const saving = ref(false)
const error = ref<string | null>(null)
const showDeleteConfirm = ref(false)
const deleting = ref(false)

watch(
  () => props.wishlist,
  (wishlist) => {
    form.title = wishlist.title
    form.description = wishlist.description ?? ''
    form.event_type = wishlist.event_type as EventType | null
    form.event_date = wishlist.event_date ?? ''
  }
)

async function save() {
  saving.value = true
  error.value = null

  try {
    await update(props.wishlist.id, {
      title: form.title.trim(),
      description: form.description || null,
      event_type: form.event_type || null,
      event_date: form.event_date || null,
    })

    emit('close')
  } catch {
    error.value = t('wishlists.errors.unknown')
  } finally {
    saving.value = false
  }
}

async function confirmDelete() {
  deleting.value = true

  try {
    await remove(props.wishlist.id)
    emit('deleted')
  } catch {
    showDeleteConfirm.value = false
  } finally {
    deleting.value = false
  }
}
</script>
