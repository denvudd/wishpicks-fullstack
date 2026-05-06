<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-brand-white dark:bg-brand-black px-4 py-16 font-body">
    <div class="w-full max-w-sm space-y-6">
      <div class="text-center space-y-1">
        <NuxtLink
          :to="localePath('/')"
          class="text-2xl font-bold font-heading text-black dark:text-white tracking-tight"
        >
          {{ $t('app.name') }}
        </NuxtLink>
        <p class="text-sm text-body-gray dark:text-muted-gray">
          {{ $t('auth.register.subtitle') }}
        </p>
      </div>

      <UCard>
        <template #header>
          <h1 class="text-base font-semibold text-black dark:text-white">
            {{ $t('auth.register.title') }}
          </h1>
        </template>

        <div class="space-y-4">
          <UAlert
            v-if="errorKey"
            color="error"
            variant="soft"
            :description="$t(errorKey)"
          />

          <UForm :state="form" class="space-y-4" @submit="handleSubmit">
            <UFormField :label="$t('auth.register.display_name')" name="display_name">
              <UInput
                v-model="form.display_name"
                type="text"
                class="w-full"
                :placeholder="$t('auth.register.display_name_placeholder')"
                autocomplete="name"
              />
            </UFormField>

            <UFormField :label="$t('auth.register.email')" name="email">
              <UInput
                v-model="form.email"
                type="email"
                class="w-full"
                :placeholder="$t('auth.register.email_placeholder')"
                autocomplete="email"
                required
              />
            </UFormField>

            <UFormField :label="$t('auth.register.password')" name="password">
              <UInput
                v-model="form.password"
                type="password"
                class="w-full"
                :placeholder="$t('auth.register.password_placeholder')"
                autocomplete="new-password"
                required
              />
            </UFormField>

            <UButton
              type="submit"
              color="neutral"
              variant="solid"
              block
              :loading="isLoading"
              :label="isLoading ? $t('auth.register.submitting') : $t('auth.register.submit')"
            />
          </UForm>

          <USeparator :label="$t('auth.register.or')" />

          <UButton
            variant="outline"
            color="neutral"
            block
            leading-icon="i-simple-icons-google"
            :label="$t('auth.register.google')"
            @click="loginWithGoogle"
          />
        </div>

        <template #footer>
          <p class="text-center text-sm text-body-gray dark:text-muted-gray">
            {{ $t('auth.register.have_account') }}
            <NuxtLink
              :to="localePath('/login')"
              class="font-medium text-black dark:text-white underline underline-offset-4"
            >
              {{ $t('auth.register.login_link') }}
            </NuxtLink>
          </p>
        </template>
      </UCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ApiFetchError } from '~/types/api'

definePageMeta({ middleware: 'guest' })

const localePath = useLocalePath()
const { register, loginWithGoogle } = useAuth()

const form = reactive({ display_name: '', email: '', password: '' })
const isLoading = ref(false)
const errorCode = ref<string | null>(null)

const errorKey = computed(() => errorCode.value ? `auth.errors.${errorCode.value}` : null)

async function handleSubmit() {
  isLoading.value = true
  errorCode.value = null
  try {
    await register({
      email: form.email,
      password: form.password,
      display_name: form.display_name || undefined,
    })
  } catch (err: unknown) {
    const code = (err as ApiFetchError)?.data?.error?.code
    errorCode.value = code ?? 'unknown'
  } finally {
    isLoading.value = false
  }
}
</script>
