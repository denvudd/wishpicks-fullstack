import { defineStore } from 'pinia'

export const useSavedStore = defineStore('saved', {
  state: () => ({
    wishlists: [] as unknown[],
    items: [] as unknown[],
  }),
  actions: {
    // TODO: implement in Phase 1
  },
})
