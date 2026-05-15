import { defineStore } from 'pinia'

const STORAGE_KEY = 'wishpicks_reservation_tokens'

export const useReservationStore = defineStore('reservation', () => {
  const tokens = ref<Record<string, string>>({})

  function load() {
    if (!import.meta.client) return
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) tokens.value = JSON.parse(raw)
    } catch {
      // corrupted storage — start fresh
    }
  }

  function _persist() {
    if (!import.meta.client) return
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens.value))
  }

  function getToken(itemId: string): string | undefined {
    return tokens.value[itemId]
  }

  function setToken(itemId: string, token: string) {
    tokens.value[itemId] = token
    _persist()
  }

  function clearToken(itemId: string) {
    const { [itemId]: _removed, ...rest } = tokens.value
    tokens.value = rest
    _persist()
  }

  return { tokens, load, getToken, setToken, clearToken }
})
