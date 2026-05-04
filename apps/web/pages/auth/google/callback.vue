<template>
  <div class="min-h-screen flex items-center justify-center gap-3">
    <UIcon name="i-lucide-loader-circle" class="size-5 animate-spin text-gray-400" />
    <p class="text-sm text-gray-500 dark:text-gray-400">{{ $t('auth.callback.processing') }}</p>
  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath()
const { initialize } = useAuth()

onMounted(async () => {
  await initialize()
  await navigateTo(localePath('/dashboard'), { replace: true })
})
</script>
