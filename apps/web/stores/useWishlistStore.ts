import { defineStore } from 'pinia'

export const useWishlistStore = defineStore('wishlist', {
  state: () => ({
    wishlists: [] as unknown[],
  }),
  actions: {
    // TODO: implement in Phase 1
  },
})
