import { apiFetch } from '~/composables/useApiFetch'
import type {
  ApiResponse,
  WishItemResponse,
  WishItemCreateBody,
  WishItemUpdateBody,
  ItemFilters,
} from '~/types/api'

interface ItemListData {
  items: WishItemResponse[]
  total: number
  limit: number
  offset: number
  available_stores: string[]
}

export const useItemsApi = () => {
  async function getOne(itemId: string): Promise<WishItemResponse> {
    const res = await apiFetch<ApiResponse<WishItemResponse>>(`/api/items/${itemId}`)
    return res.data
  }

  async function list(
    wishlistId: string,
    filters?: Partial<ItemFilters>,
    limit = 50,
    offset = 0,
  ): Promise<{ items: WishItemResponse[]; total: number; availableStores: string[] }> {
    const query: Record<string, unknown> = { limit, offset }
    if (filters) {
      if (filters.is_reserved !== null && filters.is_reserved !== undefined)
        query.is_reserved = filters.is_reserved
      if (filters.is_fulfilled !== null && filters.is_fulfilled !== undefined)
        query.is_fulfilled = filters.is_fulfilled
      if (filters.priority && filters.priority.length > 0)
        query.priority = filters.priority
      if (filters.store !== null && filters.store !== undefined)
        query.store = filters.store
    }
    const res = await apiFetch<ApiResponse<ItemListData>>(
      `/api/wishlists/${wishlistId}/items`,
      { query },
    )
    return {
      items: res.data.items,
      total: res.data.total,
      availableStores: res.data.available_stores,
    }
  }

  async function create(
    wishlistId: string,
    body: WishItemCreateBody,
  ): Promise<WishItemResponse> {
    const res = await apiFetch<ApiResponse<WishItemResponse>>(
      `/api/wishlists/${wishlistId}/items`,
      { method: 'POST', body },
    )
    return res.data
  }

  async function update(
    itemId: string,
    body: WishItemUpdateBody,
  ): Promise<WishItemResponse> {
    const res = await apiFetch<ApiResponse<WishItemResponse>>(
      `/api/items/${itemId}`,
      { method: 'PATCH', body },
    )
    return res.data
  }

  async function remove(itemId: string): Promise<void> {
    await apiFetch(`/api/items/${itemId}`, { method: 'DELETE' })
  }

  async function updatePosition(
    itemId: string,
    position: number,
  ): Promise<WishItemResponse> {
    const res = await apiFetch<ApiResponse<WishItemResponse>>(
      `/api/items/${itemId}/position`,
      { method: 'PATCH', body: { position } },
    )
    return res.data
  }

  return { getOne, list, create, update, remove, updatePosition }
}
