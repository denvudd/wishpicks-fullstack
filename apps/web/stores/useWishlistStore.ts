import { defineStore } from 'pinia'
import type { WishlistResponse } from '~/types/api'

type WishlistStatus = 'idle' | 'loading' | 'error'

export const useWishlistStore = defineStore('wishlist', {
  state: () => ({
    wishlists: [] as WishlistResponse[],
    current: null as WishlistResponse | null,
    total: 0,
    status: 'idle' as WishlistStatus,
  }),
  actions: {
    setList(wishlists: WishlistResponse[], total: number) {
      this.wishlists = wishlists
      this.total = total
      this.status = 'idle'
    },
    setCurrent(wishlist: WishlistResponse | null) {
      this.current = wishlist
    },
    prependOne(wishlist: WishlistResponse) {
      this.wishlists.unshift(wishlist)
      this.total += 1
    },
    updateOne(wishlist: WishlistResponse) {
      const idx = this.wishlists.findIndex((w) => w.id === wishlist.id)
      if (idx !== -1) this.wishlists[idx] = wishlist
      if (this.current?.id === wishlist.id) this.current = wishlist
    },
    removeOne(id: string) {
      this.wishlists = this.wishlists.filter((w) => w.id !== id)
      this.total = Math.max(0, this.total - 1)
      if (this.current?.id === id) this.current = null
    },
    setStatus(status: WishlistStatus) {
      this.status = status
    },
  },
})
