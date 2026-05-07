<template>
  <div class="p-6 max-w-2xl">
    <!-- Identity card -->
    <UCard>
      <div class="flex items-start gap-5">
        <!-- Avatar placeholder -->
        <div
          class="size-16 rounded-full bg-chip-gray dark:bg-white/10 flex items-center justify-center shrink-0"
        >
          <UIcon name="i-heroicons-user" class="size-8 text-muted-gray" />
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
                    :loading="saving"
                    :label="saving ? $t('profile.saving') : $t('profile.save')"
                    @click="save"
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

          <!-- Username (read-only) -->
          <div>
            <p class="text-sm font-medium text-black dark:text-white mb-1">
              {{ $t('profile.username_label') }}
            </p>
            <p class="text-sm text-body-gray dark:text-muted-gray">
              @{{ user?.username }}
            </p>
          </div>

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

definePageMeta({ layout: 'app', middleware: 'auth', ssr: false })

const { t } = useI18n()
const toast = useToast()
const { user } = useAuth()
const { updateProfile } = useUsers()

const displayNameDraft = ref(user.value?.display_name ?? '')
const saving = ref(false)
const isEditingDisplayName = ref(false)

watch(
  () => user.value?.display_name,
  (val) => {
    if (!saving.value) displayNameDraft.value = val ?? ''
  },
)

const isDirty = computed(
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

async function save() {
  if (!isDirty.value) {
    isEditingDisplayName.value = false
    return
  }

  saving.value = true
  try {
    await updateProfile({ display_name: displayNameDraft.value })
    isEditingDisplayName.value = false
  } catch (err: unknown) {
    const code = (err as ApiFetchError)?.data?.error?.code ?? 'unknown'
    toast.add({ title: t(`auth.errors.${code}` as string), color: 'error' })
  } finally {
    saving.value = false
  }
}

function shareProfile() {
  const url = `${window.location.origin}/u/${user.value?.username}`
  navigator.clipboard.writeText(url)
  toast.add({ title: t('profile.share_copied') })
}
</script>
