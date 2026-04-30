import { defineStore } from 'pinia'

export const useItemStore = defineStore('item', {
  state: () => ({
    items: [] as unknown[],
  }),
  actions: {
    // TODO: implement in Phase 1
  },
})
