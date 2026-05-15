import { defineStore } from 'pinia'
import type { SavedWishlistResponse, SavedItemResponse } from '~/types/api'

type SavedStatus = 'idle' | 'loading' | 'error'

export const useSavedStore = defineStore('saved', {
  state: () => ({
    wishlists: [] as SavedWishlistResponse[],
    wishlistIds: new Set<string>(),
    items: [] as SavedItemResponse[],
    wishlistsTotal: 0,
    itemsTotal: 0,
    status: 'idle' as SavedStatus,
  }),
  actions: {
    setWishlists(wishlists: SavedWishlistResponse[], total: number) {
      this.wishlists = wishlists
      this.wishlistIds = new Set(wishlists.map((w) => w.id))
      this.wishlistsTotal = total
      this.status = 'idle'
    },
    addWishlist(w: SavedWishlistResponse) {
      this.wishlists.unshift(w)
      this.wishlistIds.add(w.id)
      this.wishlistsTotal += 1
    },
    removeWishlist(id: string) {
      this.wishlists = this.wishlists.filter((w) => w.id !== id)
      this.wishlistIds.delete(id)
      this.wishlistsTotal = Math.max(0, this.wishlistsTotal - 1)
    },
    setItems(items: SavedItemResponse[], total: number) {
      this.items = items
      this.itemsTotal = total
      this.status = 'idle'
    },
    setStatus(status: SavedStatus) {
      this.status = status
    },
  },
})
