import { defineStore } from 'pinia'

interface AuthUser {
  id: string
  email: string
  display_name: string | null
  avatar_url: string | null
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as AuthUser | null,
  }),
  getters: {
    isAuthenticated: (state) => state.user !== null,
  },
  actions: {
    // TODO: implement in Phase 1
  },
})
