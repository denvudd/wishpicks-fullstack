import { defineStore } from 'pinia'

type AuthStatus = 'idle' | 'loading' | 'authenticated' | 'unauthenticated'

export interface AuthUser {
  id: string
  email: string
  username: string | null
  display_name: string | null
  avatar_url: string | null
  is_active: boolean
  is_email_verified: boolean
  created_at: string
  updated_at: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as AuthUser | null,
    status: 'idle' as AuthStatus,
  }),
  getters: {
    isAuthenticated: (state) => state.user !== null,
    isInitialized: (state) => state.status !== 'idle',
    displayName: (state) =>
      state.user?.display_name ?? state.user?.username ?? state.user?.email ?? '',
  },
  actions: {
    setUser(user: AuthUser) {
      this.user = user
      this.status = 'authenticated'
    },
    clearUser() {
      this.user = null
      this.status = 'unauthenticated'
    },
    setStatus(status: AuthStatus) {
      this.status = status
    },
  },
})
