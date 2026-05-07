import { useUsersApi } from './api/useUsersApi'

export const useUsers = () => {
  const usersApi = useUsersApi()
  const store = useAuthStore()

  async function updateProfile(body: {
    display_name?: string | null
    username?: string | null
  }): Promise<void> {
    const updated = await usersApi.updateProfile(body)
    store.setUser(updated)
  }

  return { updateProfile }
}
