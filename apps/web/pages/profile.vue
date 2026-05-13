<template>
  <div class="p-6 max-w-2xl">
    <!-- Identity card -->
    <UCard>
      <div class="flex items-start gap-5">
        <!-- Avatar -->
        <div class="shrink-0">
          <button
            type="button"
            class="group relative size-16 cursor-pointer overflow-hidden rounded-full bg-chip-gray dark:bg-white/10 focus:outline-none"
            :aria-label="$t('profile.avatar_change')"
            :disabled="isUploadingAvatar"
            @click="fileInput?.click()"
          >
            <Transition name="wp-avatar">
              <img
                v-if="currentAvatarSrc"
                :key="currentAvatarSrc"
                :src="currentAvatarSrc"
                alt=""
                class="size-full object-cover"
              />
              <div
                v-else
                class="flex size-full items-center justify-center"
              >
                <span class="text-xl font-bold text-muted-gray">
                  {{ initials }}
                </span>
              </div>
            </Transition>

            <div
              class="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 transition-opacity duration-150 group-hover:opacity-100"
              :class="{ 'opacity-100': isUploadingAvatar }"
            >
              <UIcon
                v-if="!isUploadingAvatar"
                name="i-heroicons-camera"
                class="size-5 text-white"
              />
              <UIcon
                v-else
                name="i-heroicons-arrow-path"
                class="size-5 text-white animate-spin"
              />
            </div>
          </button>

          <input
            ref="fileInput"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            class="hidden"
            @change="onAvatarFileChange"
          />
        </div>

        <div class="flex-1 space-y-4">
          <UFormField>
            <div class="min-h-9">
              <Transition
                mode="out-in"
                enter-active-class="animate-in fade-in-0 slide-in-from-top-1 duration-200 ease-out"
                leave-active-class="animate-out fade-out-0 slide-out-to-top-1 duration-150 ease-in"
              >
                <div
                  v-if="isEditingDisplayName"
                  key="display-name-edit"
                  class="flex gap-2"
                >
                  <UInput
                    v-model="displayNameDraft"
                    class="flex-1"
                    size="sm"
                    :placeholder="$t('profile.display_name')"
                  />
                  <UButton
                    color="neutral"
                    variant="outline"
                    size="sm"
                    :label="$t('profile.cancel')"
                    @click="cancelEditingDisplayName"
                  />
                  <UButton
                    color="neutral"
                    variant="solid"
                    :loading="isSavingDisplayName"
                    :label="isSavingDisplayName ? $t('profile.saving') : $t('profile.save')"
                    @click="saveDisplayName"
                  />
                </div>
                <div
                  v-else
                  key="display-name-view"
                  class="flex items-center justify-between gap-3"
                >
                  <p class="text-sm text-body-gray dark:text-muted-gray py-2">
                    {{ user?.display_name || '—' }}
                  </p>
                  <UButton
                    color="neutral"
                    variant="outline"
                    size="sm"
                    :label="$t('profile.edit')"
                    @click="startEditingDisplayName"
                  />
                </div>
              </Transition>
            </div>
          </UFormField>

          <!-- Username -->
          <UFormField :label="$t('profile.username_label')">
            <div class="min-h-9">
              <Transition
                mode="out-in"
                enter-active-class="animate-in fade-in-0 slide-in-from-top-1 duration-200 ease-out"
                leave-active-class="animate-out fade-out-0 slide-out-to-top-1 duration-150 ease-in"
              >
                <div
                  v-if="isEditingUsername"
                  key="username-edit"
                  class="flex flex-col gap-1.5"
                >
                  <div class="flex gap-2">
                    <UInput
                      v-model="usernameDraft"
                      class="flex-1"
                      size="sm"
                      autocomplete="username"
                      @input="usernameError = ''"
                    />
                    <UButton
                      color="neutral"
                      variant="outline"
                      size="sm"
                      :label="$t('profile.cancel')"
                      @click="cancelEditingUsername"
                    />
                    <UButton
                      color="neutral"
                      variant="solid"
                      size="sm"
                      :loading="isSavingUsername"
                      :label="isSavingUsername ? $t('profile.saving') : $t('profile.save')"
                      @click="saveUsername"
                    />
                  </div>
                  <p v-if="usernameError" class="text-xs text-red-500">
                    {{ usernameError }}
                  </p>
                </div>
                <div
                  v-else
                  key="username-view"
                  class="flex items-center justify-between gap-3"
                >
                  <p class="text-sm text-body-gray dark:text-muted-gray py-2">
                    @{{ user?.username || '—' }}
                  </p>
                  <UButton
                    color="neutral"
                    variant="outline"
                    size="sm"
                    :label="$t('profile.edit')"
                    @click="startEditingUsername"
                  />
                </div>
              </Transition>
            </div>
          </UFormField>

          <!-- Share profile -->
          <UButton
            variant="outline"
            color="neutral"
            icon="i-heroicons-share"
            :label="$t('profile.share')"
            @click="shareProfile"
          />
        </div>
      </div>
    </UCard>

    <!-- Wishlists section stub -->
    <section class="mt-8">
      <h2 class="text-lg font-bold text-black dark:text-white mb-3">
        {{ $t('profile.wishlists_section') }}
      </h2>
      <UCard>
        <p class="text-sm text-body-gray dark:text-muted-gray">
          {{ $t('profile.coming_soon') }}
        </p>
      </UCard>
    </section>

    <!-- Wish board section stub -->
    <section class="mt-8">
      <h2 class="text-lg font-bold text-black dark:text-white mb-3">
        {{ $t('profile.board_section') }}
      </h2>
      <UCard>
        <p class="text-sm text-body-gray dark:text-muted-gray">
          {{ $t('profile.coming_soon') }}
        </p>
      </UCard>
    </section>
  </div>
</template>

<script setup lang="ts">
import type { ApiFetchError } from '~/types/api'
import { useMediaApi } from '~/composables/api/useMediaApi'

definePageMeta({ layout: 'app', middleware: 'auth', ssr: false })

const { t } = useI18n()
const toast = useToast()
const { user } = useAuth()
const { updateProfile } = useUsers()
const mediaApi = useMediaApi()

// Avatar
const fileInput = ref<HTMLInputElement | null>(null)
const previewUrl = ref<string | null>(null)
const isUploadingAvatar = ref(false)

const currentAvatarSrc = computed(
  () => previewUrl.value ?? user.value?.avatar_url ?? null,
)

const initials = computed(() => {
  const src =
    user.value?.display_name ?? user.value?.username ?? user.value?.email ?? ''
  return src.charAt(0).toUpperCase()
})

async function onAvatarFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return

  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = URL.createObjectURL(file)
  isUploadingAvatar.value = true

  try {
    const avatarUrl = await mediaApi.uploadImage(file, 'avatars')
    await updateProfile({ avatar_url: avatarUrl })
    URL.revokeObjectURL(previewUrl.value!)
    previewUrl.value = null
  } catch {
    toast.add({ title: t('profile.errors.upload_failed'), color: 'error' })
    URL.revokeObjectURL(previewUrl.value!)
    previewUrl.value = null
  } finally {
    isUploadingAvatar.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

onBeforeUnmount(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})

// Display name
const displayNameDraft = ref(user.value?.display_name ?? '')
const isSavingDisplayName = ref(false)
const isEditingDisplayName = ref(false)

watch(
  () => user.value?.display_name,
  (val) => {
    if (!isSavingDisplayName.value) displayNameDraft.value = val ?? ''
  },
)

const isDisplayNameDirty = computed(
  () => displayNameDraft.value !== (user.value?.display_name ?? ''),
)

function startEditingDisplayName() {
  displayNameDraft.value = user.value?.display_name ?? ''
  isEditingDisplayName.value = true
}

function cancelEditingDisplayName() {
  displayNameDraft.value = user.value?.display_name ?? ''
  isEditingDisplayName.value = false
}

async function saveDisplayName() {
  if (!isDisplayNameDirty.value) {
    isEditingDisplayName.value = false
    return
  }

  isSavingDisplayName.value = true
  try {
    await updateProfile({ display_name: displayNameDraft.value })
    isEditingDisplayName.value = false
  } catch {
    toast.add({ title: t('profile.errors.unknown'), color: 'error' })
  } finally {
    isSavingDisplayName.value = false
  }
}

// Username
const usernameDraft = ref(user.value?.username ?? '')
const isSavingUsername = ref(false)
const isEditingUsername = ref(false)
const usernameError = ref('')

watch(
  () => user.value?.username,
  (val) => {
    if (!isSavingUsername.value) usernameDraft.value = val ?? ''
  },
)

const isUsernameDirty = computed(
  () => usernameDraft.value !== (user.value?.username ?? ''),
)

function startEditingUsername() {
  usernameDraft.value = user.value?.username ?? ''
  usernameError.value = ''
  isEditingUsername.value = true
}

function cancelEditingUsername() {
  usernameDraft.value = user.value?.username ?? ''
  usernameError.value = ''
  isEditingUsername.value = false
}

async function saveUsername() {
  if (!isUsernameDirty.value) {
    isEditingUsername.value = false
    return
  }

  isSavingUsername.value = true
  usernameError.value = ''
  try {
    await updateProfile({ username: usernameDraft.value })
    isEditingUsername.value = false
  } catch (err: unknown) {
    const code = (err as ApiFetchError)?.data?.error?.code
    if (code === 'USERNAME_TAKEN') {
      usernameError.value = t('profile.errors.username_taken')
    } else {
      toast.add({ title: t('profile.errors.unknown'), color: 'error' })
    }
  } finally {
    isSavingUsername.value = false
  }
}

function shareProfile() {
  const url = `${window.location.origin}/u/${user.value?.username}`
  navigator.clipboard.writeText(url)
  toast.add({ title: t('profile.share_copied') })
}
</script>

<style scoped>
.wp-avatar-enter-active {
  transition: opacity 200ms ease-out, transform 200ms ease-out;
}
.wp-avatar-enter-from {
  opacity: 0;
  transform: scale(0.9);
}
</style>
