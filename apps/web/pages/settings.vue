<template>
  <div class="p-6">
    <div class="mx-auto max-w-lg space-y-8">
      <!-- Header -->
      <div>
        <h1 class="text-xl font-bold text-black dark:text-white">
          {{ t('settings.title') }}
        </h1>
        <p class="mt-1 text-sm text-body-gray dark:text-muted-gray">
          {{ user?.email }}
        </p>
      </div>

      <!-- Card -->
      <div
        class="space-y-6 rounded-xl border border-black/10 bg-white p-6 dark:border-white/10 dark:bg-brand-black"
      >
        <!-- Avatar -->
        <div class="flex flex-col items-center gap-2">
          <button
            type="button"
            class="group relative size-20 cursor-pointer overflow-hidden rounded-full bg-chip-gray focus:outline-none dark:bg-white/10"
            :aria-label="t('settings.avatar_change')"
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
                <span class="text-2xl font-bold text-muted-gray">
                  {{ initials }}
                </span>
              </div>
            </Transition>

            <!-- Camera overlay on hover -->
            <div
              class="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 transition-opacity duration-150 group-hover:opacity-100"
            >
              <UIcon name="i-heroicons-camera" class="size-6 text-white" />
            </div>
          </button>

          <button
            type="button"
            class="text-xs text-body-gray transition-colors hover:text-black dark:text-muted-gray dark:hover:text-white"
            @click="fileInput?.click()"
          >
            {{ t('settings.avatar_change') }}
          </button>

          <input
            ref="fileInput"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            class="hidden"
            @change="onFileChange"
          />
        </div>

        <!-- display_name -->
        <UFormField :label="t('settings.display_name')">
          <UInput
            v-model="form.display_name"
            class="w-full"
            autocomplete="name"
          />
        </UFormField>

        <!-- username -->
        <UFormField
          :label="t('settings.username')"
          :error="usernameError || undefined"
        >
          <UInput
            v-model="form.username"
            class="w-full"
            autocomplete="username"
            @input="usernameError = ''"
          />
        </UFormField>
      </div>

      <!-- Save -->
      <div class="flex justify-end">
        <UButton
          :disabled="!isDirty || isSaving"
          :loading="isSaving"
          color="neutral"
          @click="save"
        >
          {{ isSaving ? t('settings.saving') : t('settings.save') }}
        </UButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMediaApi } from '~/composables/api/useMediaApi'

definePageMeta({ layout: 'app', middleware: 'auth' })

const { t } = useI18n()
const toast = useToast()
const authStore = useAuthStore()
const user = computed(() => authStore.user)
const mediaApi = useMediaApi()
const users = useUsers()

const fileInput = ref<HTMLInputElement | null>(null)
const pendingFile = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const isSaving = ref(false)
const usernameError = ref('')

const form = reactive({
  display_name: user.value?.display_name ?? '',
  username: user.value?.username ?? '',
})

watch(
  user,
  (u) => {
    if (u && !isSaving.value) {
      form.display_name = u.display_name ?? ''
      form.username = u.username ?? ''
    }
  },
  { immediate: false },
)

const currentAvatarSrc = computed(
  () => previewUrl.value ?? user.value?.avatar_url ?? null,
)

const initials = computed(() => {
  const src =
    user.value?.display_name ?? user.value?.username ?? user.value?.email ?? ''
  return src.charAt(0).toUpperCase()
})

const isDirty = computed(() => {
  if (!user.value) return false
  return (
    form.display_name !== (user.value.display_name ?? '') ||
    form.username !== (user.value.username ?? '') ||
    pendingFile.value !== null
  )
})

function onFileChange(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  pendingFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

async function save() {
  isSaving.value = true
  usernameError.value = ''

  let avatarUrl: string | undefined

  if (pendingFile.value) {
    try {
      avatarUrl = await mediaApi.uploadImage(pendingFile.value, 'avatars')
    } catch {
      toast.add({ title: t('settings.errors.upload_failed'), color: 'error' })
      isSaving.value = false
      return
    }
  }

  try {
    await users.updateProfile({
      display_name: form.display_name || null,
      username: form.username || null,
      ...(avatarUrl !== undefined ? { avatar_url: avatarUrl } : {}),
    })

    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
    pendingFile.value = null
    previewUrl.value = null

    toast.add({ title: t('settings.saved'), color: 'success' })
  } catch (err: unknown) {
    const code = (err as { data?: { error?: { code?: string } } })?.data?.error
      ?.code
    if (code === 'USERNAME_TAKEN') {
      usernameError.value = t('settings.errors.USERNAME_TAKEN')
    } else {
      toast.add({ title: t('settings.errors.unknown'), color: 'error' })
    }
  } finally {
    isSaving.value = false
  }
}

onBeforeUnmount(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})
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
