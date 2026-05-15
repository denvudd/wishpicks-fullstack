import { apiFetch } from '~/composables/useApiFetch'
import type {
  ApiResponse,
  SavedWishlistResponse,
  SavedItemResponse,
  CopyItemRequest,
  WishItemResponse,
} from '~/types/api'

interface SavedListData<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export const useSavedApi = () => {
  async function listWishlists(
    limit = 20,
    offset = 0,
  ): Promise<{ items: SavedWishlistResponse[]; total: number }> {
    const res = await apiFetch<ApiResponse<SavedListData<SavedWishlistResponse>>>(
      '/api/saved/wishlists',
      { query: { limit, offset } },
    )
    return { items: res.data.items, total: res.data.total }
  }

  async function saveWishlist(id: string): Promise<SavedWishlistResponse> {
    const res = await apiFetch<ApiResponse<SavedWishlistResponse>>(
      `/api/saved/wishlists/${id}`,
      { method: 'POST' },
    )
    return res.data
  }

  async function unsaveWishlist(id: string): Promise<void> {
    await apiFetch(`/api/saved/wishlists/${id}`, { method: 'DELETE' })
  }

  async function listItems(
    limit = 20,
    offset = 0,
  ): Promise<{ items: SavedItemResponse[]; total: number }> {
    const res = await apiFetch<ApiResponse<SavedListData<SavedItemResponse>>>(
      '/api/saved/items',
      { query: { limit, offset } },
    )
    return { items: res.data.items, total: res.data.total }
  }

  async function copyItem(
    sourceItemId: string,
    body: CopyItemRequest,
  ): Promise<WishItemResponse> {
    const res = await apiFetch<ApiResponse<WishItemResponse>>(
      `/api/saved/items/${sourceItemId}`,
      { method: 'POST', body },
    )
    return res.data
  }

  async function unsaveItem(sourceItemId: string): Promise<void> {
    await apiFetch(`/api/saved/items/${sourceItemId}`, { method: 'DELETE' })
  }

  return { listWishlists, saveWishlist, unsaveWishlist, listItems, copyItem, unsaveItem }
}
