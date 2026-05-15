<template>
  <div class="space-y-5">
    <UiAlert
      :show="!!error"
      color="error"
      variant="soft"
      :description="error"
    />

    <URadioGroup
      v-model="form.visibility"
      :legend="t('wishlists.visibility.label')"
      :items="visibilityOptions"
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

    <Transition
      mode="out-in"
      enter-active-class="animate-in fade-in-0 slide-in-from-top-1 duration-200 ease-out"
      leave-active-class="animate-out fade-out-0 slide-out-to-top-1 duration-150 ease-in"
    >
      <div v-if="form.visibility !== 'private'">
        <UButton
          variant="outline"
          color="neutral"
          icon="i-heroicons-link"
          :label="
            linkCopied
              ? t('wishlists.settings.link_copied')
              : t('wishlists.settings.copy_link')
          "
          @click="copyLink"
        />
      </div>
      <div v-else class="space-y-3">
        <UiAlert
          :show="!!inviteError"
          color="error"
          variant="soft"
          :description="inviteError"
        />
        <div class="flex gap-2">
          <UInput
            v-model="inviteEmail"
            :placeholder="t('wishlists.settings.invite_email_placeholder')"
            class="flex-1"
          />
          <UButton
            :loading="inviting"
            :label="t('wishlists.settings.invite_submit')"
            @click="submitInvite"
          />
        </div>

        <div v-if="invites.length > 0" class="space-y-2">
          <p class="text-body-gray dark:text-muted-gray text-xs font-medium">
            {{ t('wishlists.settings.invite_label') }}
          </p>
          <div
            v-for="invite in invites"
            :key="invite.id"
            class="flex items-center justify-between gap-2 text-sm"
          >
            <span class="truncate text-black dark:text-white">{{
              invite.email
            }}</span>
            <UButton
              variant="ghost"
              color="neutral"
              size="xs"
              :label="t('wishlists.settings.invite_revoke')"
              @click="revokeInvite(invite.id)"
            />
          </div>
        </div></div
    ></Transition>
  </div>
</template>

<script setup lang="ts">
import type {
  ApiFetchError,
  WishlistResponse,
  WishlistVisibility,
} from '~/types/api'

const props = defineProps<{
  wishlist: WishlistResponse
  open: boolean
}>()
const emit = defineEmits<{
  (e: 'close'): void
}>()

const { t } = useI18n()
const { update, invites, fetchInvites, addInvite, removeInvite } =
  useWishlists()

const visibilityOptions = computed(() => [
  {
    value: 'public',
    label: t('wishlists.visibility.public'),
    description: t('wishlists.visibility.public_desc'),
  },
  {
    value: 'link_only',
    label: t('wishlists.visibility.link_only'),
    description: t('wishlists.visibility.link_only_desc'),
  },
  {
    value: 'private',
    label: t('wishlists.visibility.private'),
    description: t('wishlists.visibility.private_desc'),
  },
])

const form = reactive({
  visibility: props.wishlist.visibility as WishlistVisibility,
})
const error = ref<string | null>(null)
const saving = ref(false)
const linkCopied = ref(false)
const inviteEmail = ref('')
const inviting = ref(false)
const inviteError = ref<string | null>(null)

watch(
  () => props.wishlist.visibility,
  (visibility) => {
    form.visibility = visibility as WishlistVisibility
  }
)

watch(
  () => form.visibility,
  async (v) => {
    if (v === 'private' && invites.value.length === 0) {
      await fetchInvites(props.wishlist.id)
    }
  }
)

watch(
  () => props.open,
  async (v) => {
    if (v && form.visibility === 'private') {
      await fetchInvites(props.wishlist.id)
    }
  }
)

async function save() {
  saving.value = true
  error.value = null

  try {
    await update(props.wishlist.id, { visibility: form.visibility })

    emit('close')
  } catch {
    error.value = t('wishlists.errors.unknown')
  } finally {
    saving.value = false
  }
}

async function copyLink() {
  const url = `${window.location.origin}/w/${props.wishlist.slug}`
  await navigator.clipboard.writeText(url)

  linkCopied.value = true

  setTimeout(() => {
    linkCopied.value = false
  }, 2000)
}

async function submitInvite() {
  if (!inviteEmail.value.trim()) return

  inviting.value = true
  inviteError.value = null

  try {
    await addInvite(props.wishlist.id, inviteEmail.value.trim())
    inviteEmail.value = ''
  } catch (err: unknown) {
    const code = (err as ApiFetchError)?.data?.error?.code ?? 'unknown'
    const knownCodes = ['INVITE_ALREADY_SENT', 'INVITE_NOT_APPLICABLE']
    const key = knownCodes.includes(code) ? code : 'unknown'

    inviteError.value = t(`wishlists.errors.${key}`)
  } finally {
    inviting.value = false
  }
}

async function revokeInvite(inviteId: string) {
  await removeInvite(props.wishlist.id, inviteId)
}
</script>
