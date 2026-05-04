export default defineNuxtRouteMiddleware(() => {
  const store = useAuthStore()
  const localePath = useLocalePath()
  
  // Skip on server — client plugin handles initialization
  if (!store.isInitialized) return

  if (!store.isAuthenticated) {
    return navigateTo(localePath('/login'))
  }
})
