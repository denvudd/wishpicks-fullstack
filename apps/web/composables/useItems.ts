import type {
  WishItemResponse,
  WishItemCreateBody,
  WishItemUpdateBody,
  ItemFilters,
} from '~/types/api'
import { useItemsApi } from './api/useItemsApi'

export const useItems = () => {
  const store = useItemStore()
  const api = useItemsApi()

  const items = computed(() => store.items)
  const total = computed(() => store.total)
  const isLoading = computed(() => store.status === 'loading')
  const availableStores = computed(() => store.availableStores)

  async function fetchList(
    wishlistId: string,
    filters?: Partial<ItemFilters>,
  ): Promise<void> {
    store.setStatus('loading')
    try {
      const { items, total, availableStores } = await api.list(wishlistId, filters)
      store.setItems(items, total)
      store.setAvailableStores(availableStores)
    } catch {
      store.setStatus('error')
    }
  }

  async function createItem(
    wishlistId: string,
    body: WishItemCreateBody,
  ): Promise<WishItemResponse> {
    const item = await api.create(wishlistId, body)
    store.appendOne(item)
    return item
  }

  async function updateItem(
    itemId: string,
    body: WishItemUpdateBody,
  ): Promise<WishItemResponse> {
    const item = await api.update(itemId, body)
    store.updateOne(item)
    return item
  }

  async function removeItem(itemId: string): Promise<void> {
    await api.remove(itemId)
    store.removeOne(itemId)
  }

  async function fetchOne(itemId: string): Promise<WishItemResponse | null> {
    try {
      return await api.getOne(itemId)
    } catch {
      return null
    }
  }

  function clear(): void {
    store.clear()
  }

  return { items, total, isLoading, availableStores, fetchOne, fetchList, createItem, updateItem, removeItem, clear }
}
