<template>
  <component
    :is="dialogComponent"
    v-model:open="open"
    :title="isEdit ? t('items.form_title_edit') : t('items.form_title_create')"
  >
    <template #body>
      <div class="space-y-5">
        <UAlert
          v-if="error"
          color="error"
          variant="soft"
          :description="error"
        />

        <div
          class="bg-chip-gray flex items-center gap-3 rounded-xl p-3 dark:bg-neutral-800"
        >
          <div
            class="bg-hover-gray flex h-14 w-14 shrink-0 items-center justify-center rounded-lg dark:bg-neutral-700"
          >
            <UIcon name="i-heroicons-gift" class="text-muted-gray h-7 w-7" />
          </div>
          <div class="min-w-0 space-y-0.5">
            <p class="text-muted-gray text-xs">
              {{ t('items.preview_label') }}
            </p>
            <p
              class="truncate text-sm font-semibold text-black dark:text-white"
            >
              {{ form.title || '—' }}
            </p>
            <Transition
              mode="out-in"
              enter-active-class="animate-in fade-in-0 slide-in-from-top-1 duration-200 ease-out"
              leave-active-class="animate-out fade-out-0 slide-out-to-top-1 duration-150 ease-in"
            >
              <p
                v-if="pricePreview"
                class="text-body-gray dark:text-muted-gray text-xs"
              >
                {{ pricePreview }}
              </p>
            </Transition>
          </div>
        </div>

        <UFormField :label="t('items.fields.product_url')">
          <UInput
            v-model="form.product_url"
            :placeholder="t('items.fields.product_url_placeholder')"
            type="url"
          />
        </UFormField>

        <UFormField :label="t('items.fields.title')" required>
          <UInput
            v-model="form.title"
            :placeholder="t('items.fields.title_placeholder')"
            :maxlength="200"
          />
        </UFormField>

        <UFormField>
          <div class="space-y-3">
            <USelect
              :ui="{
                base: 'p-0 bg-transparent! ring-0 focus:ring-0 w-fit',
                value: 'mr-6',
                trailing: 'pe-0',
                content: 'min-w-3xs',
              }"
              v-model="form.price_mode"
              :items="[
                { value: 'exact', label: t('items.fields.price_exact') },
                { value: 'range', label: t('items.fields.price_range') },
              ]"
            />

            <UFieldGroup class="w-full">
              <UInput
                v-model="form.price_min"
                :placeholder="
                  form.price_mode === 'range'
                    ? t('items.fields.price_min_placeholder')
                    : t('items.fields.price_placeholder')
                "
                type="number"
                :min="0"
                color="neutral"
                variant="outline"
                class="min-w-0 flex-1"
              />
              <UBadge
                v-if="form.price_mode === 'range'"
                color="neutral"
                variant="outline"
                size="sm"
                class="shrink-0 rounded-none px-2 font-normal"
                label="–"
              />
              <UInput
                v-if="form.price_mode === 'range'"
                v-model="form.price_max"
                :placeholder="t('items.fields.price_max_placeholder')"
                type="number"
                :min="0"
                color="neutral"
                variant="outline"
                class="min-w-0 flex-1"
              />
              <USelect
                v-model="form.currency"
                :items="currencyOptions"
                color="neutral"
                variant="outline"
                class="w-24 shrink-0"
              />
            </UFieldGroup>
          </div>
        </UFormField>

        <UFormField :label="t('items.fields.wishlist')">
          <USelect v-model="form.wishlist_id" :items="wishlistOptions" />
        </UFormField>

        <UFormField :label="t('items.fields.notes')">
          <UTextarea
            v-model="form.notes"
            :placeholder="t('items.fields.notes_placeholder')"
            :rows="2"
          />
        </UFormField>

        <UCollapsible :unmount-on-hide="false" class="flex flex-col">
          <UButton
            class="group w-full justify-start gap-1.5 px-0 py-0.5 text-sm font-medium text-black dark:text-white"
            variant="link"
            color="neutral"
            :label="t('items.advanced.title')"
            icon="i-heroicons-chevron-down"
            :ui="{
              leadingIcon:
                'size-4 group-data-[state=open]:rotate-180 transition-transform duration-200',
            }"
          />

          <template #content>
            <div class="mt-4 space-y-5">
              <UFormField :label="t('items.advanced.priority')">
                <div class="flex gap-2">
                  <UButton
                    v-for="opt in priorityChoices"
                    :key="opt.value"
                    type="button"
                    class="flex-1 gap-1 whitespace-normal"
                    :variant="form.priority === opt.value ? 'solid' : 'outline'"
                    color="neutral"
                    :aria-pressed="form.priority === opt.value"
                    @click="form.priority = opt.value"
                  >
                    <span class="text-xl leading-none" aria-hidden="true">{{
                      opt.emoji
                    }}</span>
                    <span class="text-center text-xs leading-snug font-medium">
                      {{ opt.label }}
                    </span>
                  </UButton>
                </div>
              </UFormField>

              <UFormField :label="t('items.advanced.tags')">
                <div class="space-y-2">
                  <UInput
                    v-model="tagInput"
                    :placeholder="t('items.advanced.tags_placeholder')"
                    @keydown="onTagKeydown"
                  />
                  <div v-if="form.tags.length" class="flex flex-wrap gap-1.5">
                    <span
                      v-for="tag in form.tags"
                      :key="tag"
                      class="bg-chip-gray inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs text-black dark:bg-neutral-700 dark:text-white"
                    >
                      {{ tag }}
                      <button
                        class="leading-none transition-colors hover:text-red-500"
                        @click="removeTag(tag)"
                      >
                        <UIcon name="i-heroicons-x-mark" class="h-3 w-3" />
                      </button>
                    </span>
                  </div>
                </div>
              </UFormField>

              <UFormField :label="t('items.advanced.description')">
                <UTextarea
                  v-model="form.description"
                  :placeholder="t('items.advanced.description_placeholder')"
                  :rows="3"
                />
              </UFormField>
            </div>
          </template>
        </UCollapsible>

        <template v-if="isEdit">
          <UiAlert
            :show="showDeleteConfirm"
            color="error"
            variant="soft"
            :description="t('items.delete_confirm_body')"
            :actions="[
              {
                label: deleting
                  ? t('items.deleting')
                  : t('items.delete_confirm_yes'),
                color: 'error',
                loading: deleting,
                onClick: doDelete,
              },
              {
                label: t('items.delete_cancel'),
                color: 'neutral',
                variant: 'outline',
                onClick: () => (showDeleteConfirm = false),
              },
            ]"
          />
          <UButton
            v-if="!showDeleteConfirm"
            variant="ghost"
            color="error"
            :label="t('items.delete')"
            icon="i-heroicons-trash"
            @click="showDeleteConfirm = true"
          />
        </template>
      </div>
    </template>

    <template #footer>
      <UButton
        class="w-full"
        :loading="submitting"
        :disabled="!form.title.trim() || submitting"
        :label="
          submitting
            ? t('items.submitting')
            : isEdit
              ? t('items.submit_edit')
              : t('items.submit_create')
        "
        @click="submit"
      />
    </template>
  </component>
</template>

<script setup lang="ts">
import { resolveComponent } from 'vue'
import type { WishItemResponse } from '~/types/api'

interface Props {
  initialTitle?: string
  initialProductUrl?: string | null
  wishlistId: string
  item?: WishItemResponse | null
}

const props = withDefaults(defineProps<Props>(), {
  initialTitle: '',
  initialProductUrl: null,
  item: null,
})

const emit = defineEmits<{
  saved: [item: WishItemResponse]
  deleted: []
}>()

const open = defineModel<boolean>('open', { default: false })

const { t } = useI18n()
const { wishlists, fetchList: fetchWishlists } = useWishlists()
const { createItem, updateItem, removeItem } = useItems()

const UModal = resolveComponent('UModal')
const UDrawer = resolveComponent('UDrawer')
const isMobile = ref(false)

onMounted(async () => {
  isMobile.value = window.matchMedia('(max-width: 767px)').matches
  if (!wishlists.value.length) await fetchWishlists()
})

const dialogComponent = computed(() => (isMobile.value ? UDrawer : UModal))
const isEdit = computed(() => !!props.item)

function priceModeFromItem(item: WishItemResponse): 'exact' | 'range' {
  const min = item.price_min
  const max = item.price_max
  if (min == null || max == null || min === '' || max === '') return 'exact'
  const minN = parseFloat(String(min))
  const maxN = parseFloat(String(max))
  if (Number.isNaN(minN) || Number.isNaN(maxN)) return 'exact'
  return minN !== maxN ? 'range' : 'exact'
}

function resetFormForCreate() {
  form.title = props.initialTitle || ''
  form.product_url = props.initialProductUrl || ''
  form.price_mode = 'exact'
  form.price_min = ''
  form.price_max = ''
  form.currency = 'UAH'
  form.wishlist_id = props.wishlistId
  form.notes = ''
  form.priority = '0'
  form.tags = []
  form.description = ''
}

function applyFormFromItem(item: WishItemResponse) {
  form.title = item.title ?? ''
  form.product_url = item.product_url ?? ''
  form.price_mode = priceModeFromItem(item)
  form.price_min = item.price_min ?? ''
  form.price_max = item.price_max ?? ''
  form.currency = item.currency ?? 'UAH'
  form.wishlist_id = item.wishlist_id
  form.notes = item.notes ?? ''
  form.priority = String(item.priority ?? 0)
  form.tags = [...(item.tags ?? [])]
  form.description = item.description ?? ''
}

const form = reactive({
  title: '',
  product_url: '',
  price_mode: 'exact' as 'exact' | 'range',
  price_min: '',
  price_max: '',
  currency: 'UAH',
  wishlist_id: props.wishlistId,
  notes: '',
  priority: '0',
  tags: [] as string[],
  description: '',
})

watch(open, (val) => {
  if (!val) return
  if (props.item) applyFormFromItem(props.item)
  else resetFormForCreate()
  tagInput.value = ''
  showDeleteConfirm.value = false
  error.value = null
})

const submitting = ref(false)
const deleting = ref(false)
const showDeleteConfirm = ref(false)
const error = ref<string | null>(null)
const tagInput = ref('')

const currencyOptions = ['UAH', 'USD', 'EUR', 'GBP']

const wishlistOptions = computed(() =>
  wishlists.value.map((w) => ({ value: w.id, label: w.title }))
)

const priorityChoices = computed(() => [
  { value: '0', emoji: '✨', label: t('items.priority.normal') },
  { value: '1', emoji: '🔥', label: t('items.priority.high') },
  { value: '2', emoji: '💎', label: t('items.priority.must_have') },
])

const pricePreview = computed(() => {
  const min = form.price_min
  const max = form.price_max
  if (!min && !max) return null
  if (form.price_mode === 'range' && min && max && min !== max) {
    return `${min}–${max} ${form.currency}`
  }
  return min ? `${min} ${form.currency}` : null
})

function onTagKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault()
    addTag()
  }
}

function addTag() {
  const tag = tagInput.value.trim().replace(/,$/, '')
  if (tag && !form.tags.includes(tag)) {
    form.tags.push(tag)
  }
  tagInput.value = ''
}

function removeTag(tag: string) {
  form.tags = form.tags.filter((t) => t !== tag)
}

function buildBody() {
  const priceMin = form.price_min ? parseFloat(String(form.price_min)) : null
  const priceMax =
    form.price_mode === 'exact'
      ? priceMin
      : form.price_max
        ? parseFloat(String(form.price_max))
        : null
  return {
    title: form.title.trim(),
    description: form.description.trim() || null,
    product_url: form.product_url.trim() || null,
    price_min: priceMin,
    price_max: priceMax,
    currency: form.currency,
    priority: Number(form.priority),
    notes: form.notes.trim() || null,
    tags: form.tags.length ? form.tags : null,
  }
}

async function submit() {
  if (!form.title.trim()) return
  submitting.value = true
  error.value = null
  try {
    let saved: WishItemResponse
    if (isEdit.value && props.item) {
      saved = await updateItem(props.item.id, buildBody())
    } else {
      saved = await createItem(form.wishlist_id, buildBody())
    }
    emit('saved', saved)
    open.value = false
  } catch {
    error.value = t('items.errors.unknown')
  } finally {
    submitting.value = false
  }
}

async function doDelete() {
  if (!props.item) return
  deleting.value = true
  error.value = null
  try {
    await removeItem(props.item.id)
    emit('deleted')
    open.value = false
  } catch {
    error.value = t('items.errors.unknown')
    showDeleteConfirm.value = false
  } finally {
    deleting.value = false
  }
}
</script>
