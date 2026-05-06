export default defineNuxtRouteMiddleware(({ meta }) => {
  const store = useAuthStore()
  const localePath = useLocalePath()

  // Skip on server — client plugin handles initialization
  if (!store.isInitialized) return

  if (store.isAuthenticated && meta.middleware !== 'guest') {
    return navigateTo(localePath('/dashboard'))
  }
})
