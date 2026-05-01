<template>
  <div class="min-h-screen flex flex-col items-center justify-center px-4 py-16">
    <div class="w-full max-w-sm space-y-6">
      <div class="text-center space-y-1">
        <NuxtLink :to="localePath('/')" class="text-2xl font-bold tracking-tight">
          {{ $t('app.name') }}
        </NuxtLink>
        <p class="text-sm text-gray-500 dark:text-gray-400">{{ $t('auth.login.subtitle') }}</p>
      </div>

      <UCard>
        <div class="space-y-4">
          <UAlert
            v-if="errorKey"
            color="error"
            variant="soft"
            :description="$t(errorKey)"
          />

          <form class="space-y-4" @submit.prevent="handleSubmit">
            <UFormField :label="$t('auth.login.email')" name="email">
              <UInput
                v-model="form.email"
                type="email"
                :placeholder="$t('auth.login.email_placeholder')"
                autocomplete="email"
                required
                class="w-full"
              />
            </UFormField>

            <UFormField :label="$t('auth.login.password')" name="password">
              <UInput
                v-model="form.password"
                type="password"
                :placeholder="$t('auth.login.password_placeholder')"
                autocomplete="current-password"
                required
                class="w-full"
              />
            </UFormField>

            <UButton type="submit" class="w-full" :loading="isLoading">
              {{ isLoading ? $t('auth.login.submitting') : $t('auth.login.submit') }}
            </UButton>
          </form>

          <div class="flex items-center gap-3">
            <div class="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
            <span class="text-xs text-gray-400">{{ $t('auth.login.or') }}</span>
            <div class="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
          </div>

          <UButton
            variant="outline"
            color="neutral"
            class="w-full"
            leading-icon="i-simple-icons-google"
            @click="loginWithGoogle"
          >
            {{ $t('auth.login.google') }}
          </UButton>
        </div>
      </UCard>

      <p class="text-center text-sm text-gray-500 dark:text-gray-400">
        {{ $t('auth.login.no_account') }}
        <NuxtLink
          :to="localePath('/register')"
          class="font-medium text-primary underline-offset-4 hover:underline"
        >
          {{ $t('auth.login.register_link') }}
        </NuxtLink>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ApiFetchError } from '~/types/api'

definePageMeta({ middleware: 'guest' })

const localePath = useLocalePath()
const { login, loginWithGoogle } = useAuth()

const form = reactive({ email: '', password: '' })
const isLoading = ref(false)
const errorCode = ref<string | null>(null)

const errorKey = computed(() => {
  if (!errorCode.value) return null
  return `auth.errors.${errorCode.value}`
})

async function handleSubmit() {
  isLoading.value = true
  errorCode.value = null
  try {
    await login(form)
  } catch (err: unknown) {
    const code = (err as ApiFetchError)?.data?.error?.code
    errorCode.value = code ?? 'unknown'
  } finally {
    isLoading.value = false
  }
}
</script>
