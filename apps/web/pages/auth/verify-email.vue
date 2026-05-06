<template>
  <div
    class="bg-brand-white dark:bg-brand-black font-body flex min-h-screen flex-col items-center justify-center px-4 py-16"
  >
    <div class="w-full max-w-sm space-y-6">
      <div class="space-y-1 text-center">
        <NuxtLink
          :to="localePath('/')"
          class="font-heading text-2xl font-bold tracking-tight text-black dark:text-white"
        >
          {{ $t('app.name') }}
        </NuxtLink>
        <p class="text-body-gray dark:text-muted-gray text-sm">
          {{ $t('auth.verify_email.subtitle') }}
        </p>
      </div>

      <UCard>
        <template #header>
          <h1 class="text-base font-semibold text-black dark:text-white">
            {{ $t('auth.verify_email.title') }}
          </h1>
        </template>

        <div class="space-y-4">
          <p class="text-body-gray dark:text-muted-gray text-sm">
            {{ $t('auth.verify_email.instructions', { email: user?.email }) }}
          </p>

          <UiAlert
            :show="!!errorKey"
            color="error"
            variant="soft"
            :description="errorKey ? $t(errorKey) : ''"
          />
          <UiAlert
            :show="resendSuccess"
            color="success"
            variant="soft"
            :description="$t('auth.verify_email.resend_success')"
          />

          <UForm :state="form" class="space-y-4" @submit="handleSubmit">
            <UFormField :label="$t('auth.verify_email.code')" name="code">
              <UInput
                v-model="form.code"
                type="text"
                class="w-full"
                :placeholder="$t('auth.verify_email.code_placeholder')"
                maxlength="6"
                autocomplete="one-time-code"
                inputmode="numeric"
                required
              />
            </UFormField>

            <UButton
              type="submit"
              color="neutral"
              variant="solid"
              block
              :loading="isSubmitting"
              :label="
                isSubmitting
                  ? $t('auth.verify_email.submitting')
                  : $t('auth.verify_email.submit')
              "
            />
          </UForm>

          <div class="flex items-center justify-between text-sm">
            <span class="text-body-gray dark:text-muted-gray">
              {{ $t('auth.verify_email.no_code') }}
            </span>
            <UButton
              variant="link"
              color="neutral"
              :label="
                cooldown > 0
                  ? $t('auth.verify_email.resend_cooldown', {
                      seconds: cooldown,
                    })
                  : $t('auth.verify_email.resend')
              "
              :disabled="cooldown > 0 || isResending"
              :loading="isResending"
              @click="handleResend"
            />
          </div>
        </div>

        <template #footer>
          <p class="text-body-gray dark:text-muted-gray text-center text-sm">
            <NuxtLink
              :to="localePath('/dashboard')"
              class="font-medium text-black underline underline-offset-4 dark:text-white"
            >
              {{ $t('auth.verify_email.skip') }}
            </NuxtLink>
          </p>
        </template>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ApiFetchError } from '~/types/api'

definePageMeta({ middleware: 'auth' })

const localePath = useLocalePath()
const store = useAuthStore()
const { user, verifyEmail, resendVerification } = useAuth()

onMounted(() => {
  if (store.user?.is_email_verified) {
    navigateTo(localePath('/dashboard'), { replace: true })
  }
})

const form = reactive({ code: '' })
const isSubmitting = ref(false)
const isResending = ref(false)
const errorCode = ref<string | null>(null)
const resendSuccess = ref(false)
const cooldown = ref(0)

const errorKey = computed(() =>
  errorCode.value ? `auth.errors.${errorCode.value}` : null
)

let cooldownTimer: ReturnType<typeof setInterval> | null = null

function startCooldown() {
  cooldown.value = 60
  cooldownTimer = setInterval(() => {
    cooldown.value--
    if (cooldown.value <= 0 && cooldownTimer) {
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }, 1000)
}

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})

async function handleSubmit() {
  isSubmitting.value = true
  errorCode.value = null
  try {
    await verifyEmail(form.code)
  } catch (err: unknown) {
    const code = (err as ApiFetchError)?.data?.error?.code
    errorCode.value = code ?? 'unknown'
  } finally {
    isSubmitting.value = false
  }
}

async function handleResend() {
  isResending.value = true
  errorCode.value = null
  resendSuccess.value = false
  try {
    await resendVerification()
    resendSuccess.value = true
    startCooldown()
  } catch (err: unknown) {
    const code = (err as ApiFetchError)?.data?.error?.code
    errorCode.value = code ?? 'unknown'
  } finally {
    isResending.value = false
  }
}
</script>
