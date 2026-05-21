import type { CopyItemRequest, WishItemResponse } from '~/types/api'
import { useSavedApi } from './api/useSavedApi'

export const useSaved = () => {
  const store = useSavedStore()
  const api = useSavedApi()
  const toast = useToast()
  const { t } = useI18n()

  const savedWishlists = computed(() => store.wishlists)
  const savedItems = computed(() => store.items)
  const isLoading = computed(() => store.status === 'loading')

  function isSaved(wishlistId: string): boolean {
    return store.wishlistIds.has(wishlistId)
  }

  async function fetchWishlists(): Promise<void> {
    if (store.status === 'loading') return
    store.setStatus('loading')
    try {
      const { items, total } = await api.listWishlists()
      store.setWishlists(items, total)
    } catch {
      store.setStatus('error')
    }
  }

  async function saveWishlist(id: string): Promise<void> {
    try {
      const saved = await api.saveWishlist(id)
      store.addWishlist(saved)
    } catch (err: unknown) {
      const status = (err as { status?: number })?.status
      if (status === 403) {
        toast.add({ title: t('saved.cannot_save_own'), color: 'error' })
      } else {
        toast.add({ title: t('saved.errors.unknown'), color: 'error' })
      }
    }
  }

  async function unsaveWishlist(id: string): Promise<void> {
    store.removeWishlist(id)
    try {
      await api.unsaveWishlist(id)
    } catch {
      await fetchWishlists()
    }
  }

  async function toggleWishlist(id: string): Promise<void> {
    if (isSaved(id)) {
      await unsaveWishlist(id)
    } else {
      await saveWishlist(id)
    }
  }

  async function fetchItems(): Promise<void> {
    store.setStatus('loading')
    try {
      const { items, total } = await api.listItems()
      store.setItems(items, total)
    } catch {
      store.setStatus('error')
    }
  }

  async function copyItem(
    sourceItemId: string,
    data: CopyItemRequest,
  ): Promise<WishItemResponse> {
    return api.copyItem(sourceItemId, data)
  }

  async function unsaveItem(id: string): Promise<void> {
    await api.unsaveItem(id)
  }

  return {
    savedWishlists,
    savedItems,
    isLoading,
    isSaved,
    fetchWishlists,
    saveWishlist,
    unsaveWishlist,
    toggleWishlist,
    fetchItems,
    copyItem,
    unsaveItem,
  }
}
