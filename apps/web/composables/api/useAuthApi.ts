import type { ApiResponse } from '~/types/api'
import type { AuthUser } from '~/stores/useAuthStore'

export const useAuthApi = () => {
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBaseUrl

  async function register(
    body: { email: string; password: string; display_name?: string },
    headers?: HeadersInit
  ): Promise<AuthUser> {
    const res = await $fetch<ApiResponse<AuthUser>>('/api/auth/register', {
      method: 'POST',
      baseURL,
      credentials: 'include',
      body,
      headers,
    })

    return res.data
  }

  async function login(
    body: { email: string; password: string },
    headers?: HeadersInit
  ): Promise<AuthUser> {
    const res = await $fetch<ApiResponse<AuthUser>>('/api/auth/login', {
      method: 'POST',
      baseURL,
      credentials: 'include',
      body,
      headers,
    })

    return res.data
  }

  async function logout(): Promise<void> {
    await $fetch('/api/auth/logout', {
      method: 'POST',
      baseURL,
      credentials: 'include',
    })
  }

  async function refresh(): Promise<void> {
    await $fetch('/api/auth/refresh', {
      method: 'POST',
      baseURL,
      credentials: 'include',
    })
  }

  async function me(headers?: HeadersInit): Promise<AuthUser> {
    const res = await $fetch<ApiResponse<AuthUser>>('/api/auth/me', {
      baseURL,
      credentials: 'include',
      headers,
    })

    return res.data
  }

  async function verifyEmail(code: string): Promise<AuthUser> {
    const res = await $fetch<ApiResponse<AuthUser>>('/api/auth/verify-email', {
      method: 'POST',
      baseURL,
      credentials: 'include',
      body: { code },
    })
    return res.data
  }

  async function resendVerification(): Promise<void> {
    await $fetch('/api/auth/resend-verification', {
      method: 'POST',
      baseURL,
      credentials: 'include',
    })
  }

  function googleAuthUrl(): string {
    return `${baseURL}/api/auth/google`
  }

  return { register, login, logout, refresh, me, verifyEmail, resendVerification, googleAuthUrl }
}
