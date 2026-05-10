import { apiFetch } from '~/composables/useApiFetch'
import type {
  ApiResponse,
  WishItemResponse,
  WishItemCreateBody,
  WishItemUpdateBody,
} from '~/types/api'

interface ItemListData {
  items: WishItemResponse[]
  total: number
  limit: number
  offset: number
}

export const useItemsApi = () => {
  async function getOne(itemId: string): Promise<WishItemResponse> {
    const res = await apiFetch<ApiResponse<WishItemResponse>>(`/api/items/${itemId}`)
    return res.data
  }

  async function list(
    wishlistId: string,
    limit = 50,
    offset = 0,
  ): Promise<{ items: WishItemResponse[]; total: number }> {
    const res = await apiFetch<ApiResponse<ItemListData>>(
      `/api/wishlists/${wishlistId}/items`,
      { query: { limit, offset } },
    )
    return { items: res.data.items, total: res.data.total }
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
