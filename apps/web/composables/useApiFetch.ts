import type { ApiFetchError } from '~/types/api'

type ApiFetchOptions = Parameters<typeof $fetch>[1]

let isRefreshing = false

export async function apiFetch<T = unknown>(
  url: string,
  options?: ApiFetchOptions,
): Promise<T> {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBaseUrl

  const fetchOptions: ApiFetchOptions = {
    baseURL,
    credentials: 'include',
    ...options,
  }

  try {
    return await $fetch<T>(url, fetchOptions)
  } catch (err: unknown) {
    const status = (err as ApiFetchError)?.status
    const isRefreshEndpoint = url.includes('/api/auth/refresh')

    if (status === 401 && !isRefreshEndpoint && !isRefreshing) {
      isRefreshing = true

      try {
        await $fetch('/api/auth/refresh', {
          method: 'POST',
          baseURL,
          credentials: 'include',
        })

        isRefreshing = false
        return await $fetch<T>(url, fetchOptions)
      } catch {
        isRefreshing = false

        useAuthStore().clearUser()
        await navigateTo(useLocalePath()('/login'))
        
        throw err
      }
    }

    throw err
  }
}
