import type { ApiResponse } from '~/types/api'
import type { AuthUser } from '~/stores/useAuthStore'
import { apiFetch } from '~/composables/useApiFetch'

export const useUsersApi = () => {
  async function updateProfile(body: {
    display_name?: string | null
    username?: string | null
    avatar_url?: string | null
  }): Promise<AuthUser> {
    const res = await apiFetch<ApiResponse<AuthUser>>('/api/users/me', {
      method: 'PATCH',
      body,
    })
    return res.data
  }

  return { updateProfile }
}
