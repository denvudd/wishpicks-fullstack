import type { ApiFetchError } from '~/types/api'
import { useAuthApi } from './api/useAuthApi'

export const useAuth = () => {
  const store = useAuthStore()
  const authApi = useAuthApi()
  const localePath = useLocalePath()

  async function initialize(headers?: HeadersInit): Promise<void> {
    store.setStatus('loading')

    try {
      const user = await authApi.me(headers)
      store.setUser(user)
    } catch (err: unknown) {
      const status = (err as ApiFetchError)?.status

      if (status === 401) {
        try {
          await authApi.refresh()
          const user = await authApi.me()
          store.setUser(user)
        } catch {
          store.clearUser()
        }
      } else {
        store.clearUser()
      }
    }
  }

  async function login(credentials: { email: string; password: string }): Promise<void> {
    store.setStatus('loading')

    try {
      const user = await authApi.login(credentials)
      store.setUser(user)

      await navigateTo(localePath('/dashboard'))
    } catch (err) {
      store.setStatus('unauthenticated')
      throw err
    }
  }

  async function register(data: {
    email: string
    password: string
    display_name?: string
  }): Promise<void> {
    store.setStatus('loading')

    try {
      const user = await authApi.register(data)
      store.setUser(user)
      
      await navigateTo(localePath('/dashboard'))
    } catch (err) {
      store.setStatus('unauthenticated')
      throw err
    }
  }

  async function logout(): Promise<void> {
    try {
      await authApi.logout()
    } catch {
      // best-effort — clear local state regardless
    }
    store.clearUser()
    await navigateTo(localePath('/'))
  }

  function loginWithGoogle(): void {
    window.location.href = authApi.googleAuthUrl()
  }

  return {
    user: computed(() => store.user),
    isAuthenticated: computed(() => store.isAuthenticated),
    isInitialized: computed(() => store.isInitialized),
    displayName: computed(() => store.displayName),
    initialize,
    login,
    register,
    logout,
    loginWithGoogle,
  }
}
