<template>
  <UModal v-model:open="open" :title="t('saved.copy_modal_title')">
    <template #body>
      <!-- Item preview -->
      <div
        class="mb-5 flex items-center gap-3 rounded-lg bg-neutral-50 p-3 dark:bg-neutral-800"
      >
        <img
          v-if="item.image_url"
          :src="item.image_url"
          :alt="item.title"
          class="h-14 w-14 shrink-0 rounded-lg object-cover"
        />
        <div
          v-else
          class="bg-chip-gray flex h-14 w-14 shrink-0 items-center justify-center rounded-lg dark:bg-neutral-700"
        >
          <UIcon name="i-heroicons-gift" class="text-muted-gray h-7 w-7" />
        </div>
        <div class="min-w-0 space-y-0.5">
          <p
            class="line-clamp-2 text-sm font-semibold text-black dark:text-white"
          >
            {{ item.title }}
          </p>
          <p
            v-if="pricePreview"
            class="text-body-gray dark:text-muted-gray text-xs"
          >
            {{ pricePreview }}
          </p>
        </div>
      </div>

      <!-- No wishlists prompt -->
      <div
        v-if="wishlists.length === 0 && !isLoadingWishlists"
        class="py-4 text-center"
      >
        <p class="text-body-gray dark:text-muted-gray mb-3 text-sm">
          {{ t('saved.copy_no_wishlists') }}
        </p>
        <UButton
          variant="outline"
          color="neutral"
          size="sm"
          :to="localePath('/dashboard')"
          @click="open = false"
        >
          {{ t('wishlists.new') }}
        </UButton>
      </div>

      <div v-else class="space-y-4">
        <!-- Wishlist select -->
        <UFormField :label="t('saved.copy_wishlist_label')" required>
          <USelect
            v-model="selectedWishlistId"
            :items="wishlistOptions"
            value-key="value"
            label-key="label"
            class="w-full"
          />
        </UFormField>

        <!-- Priority -->
        <UFormField :label="t('saved.copy_priority_label')">
          <ItemsItemPriorityPicker v-model="selectedPriority" />
        </UFormField>

        <!-- Notes -->
        <UFormField :label="t('saved.copy_notes_label')">
          <UTextarea
            v-model="notes"
            :placeholder="t('items.fields.notes_placeholder')"
            :rows="3"
            class="w-full"
          />
        </UFormField>

        <!-- Error -->
        <UAlert
          v-if="errorMsg"
          color="error"
          variant="subtle"
          :description="errorMsg"
        />

        <!-- Submit -->
        <UButton
          class="w-full"
          :loading="submitting"
          :label="
            submitting ? t('saved.copy_submitting') : t('saved.copy_submit')
          "
          :disabled="!selectedWishlistId"
          @click="onSubmit"
        />
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { SharedItemResponse, WishItemResponse } from '~/types/api'

const props = defineProps<{
  item: SharedItemResponse
}>()

const emit = defineEmits<{
  copied: [item: WishItemResponse]
}>()

const open = defineModel<boolean>('open', { default: false })

const { t } = useI18n()
const localePath = useLocalePath()
const toast = useToast()
const { wishlists, isLoading: isLoadingWishlists, fetchList } = useWishlists()
const { copyItem } = useSaved()

const selectedWishlistId = ref<string | undefined>(undefined)
const selectedPriority = ref<number>(0)
const notes = ref<string>('')
const submitting = ref(false)
const errorMsg = ref<string | null>(null)

const wishlistOptions = computed(() =>
  wishlists.value.map((w) => ({ value: w.id, label: w.title }))
)

const pricePreview = computed(() => {
  const min = props.item.price_min
  const max = props.item.price_max
  const currency = props.item.currency

  if (!min && !max) return null

  if (min && max && min !== max) {
    return `${min}–${max} ${currency}`
  }

  return min ? `${min} ${currency}` : null
})

watch(
  open,
  (val) => {
    if (val) {
      selectedWishlistId.value = wishlists.value[0]?.id ?? undefined
      selectedPriority.value = 0
      notes.value = ''
      errorMsg.value = null
      fetchList()
    }
  },
  { immediate: true, flush: 'sync' }
)

watch(wishlistOptions, (opts) => {
  if (opts.length && !selectedWishlistId.value) {
    selectedWishlistId.value = opts[0]?.value ?? undefined
  }
})

async function onSubmit() {
  if (!selectedWishlistId.value) return

  submitting.value = true
  errorMsg.value = null

  try {
    const result = await copyItem(props.item.id, {
      wishlist_id: selectedWishlistId.value,
      priority: selectedPriority.value,
      notes: notes.value || null,
    })

    const wishlistTitle =
      wishlists.value.find((w) => w.id === selectedWishlistId.value)?.title ??
      ''

    toast.add({
      title: t('saved.copy_success', { title: wishlistTitle }),
      color: 'success',
    })
    emit('copied', result)
    open.value = false
  } catch {
    errorMsg.value = t('saved.errors.unknown')
  } finally {
    submitting.value = false
  }
}
</script>
