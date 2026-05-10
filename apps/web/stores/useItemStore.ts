import { defineStore } from 'pinia'
import type { WishItemResponse } from '~/types/api'

type ItemStatus = 'idle' | 'loading' | 'error'

export const useItemStore = defineStore('item', {
  state: () => ({
    items: [] as WishItemResponse[],
    total: 0,
    status: 'idle' as ItemStatus,
    availableStores: [] as string[],
  }),
  actions: {
    setItems(items: WishItemResponse[], total: number) {
      this.items = items
      this.total = total
      this.status = 'idle'
    },
    appendOne(item: WishItemResponse) {
      this.items.push(item)
      this.total += 1
    },
    updateOne(item: WishItemResponse) {
      const idx = this.items.findIndex((i) => i.id === item.id)
      if (idx !== -1) this.items[idx] = item
    },
    removeOne(id: string) {
      this.items = this.items.filter((i) => i.id !== id)
      this.total = Math.max(0, this.total - 1)
    },
    setStatus(status: ItemStatus) {
      this.status = status
    },
    setAvailableStores(stores: string[]) {
      this.availableStores = stores
    },
    clear() {
      this.items = []
      this.total = 0
      this.status = 'idle'
      this.availableStores = []
    },
  },
})
