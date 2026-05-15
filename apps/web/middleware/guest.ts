export default defineNuxtRouteMiddleware(() => {
  const store = useAuthStore()
  const localePath = useLocalePath()

  if (!store.isInitialized) return

  if (store.isAuthenticated) {
    return navigateTo(localePath('/dashboard'))
  }
})
