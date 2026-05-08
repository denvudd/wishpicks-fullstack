import { apiFetch } from '~/composables/useApiFetch'
import type {
  ApiResponse,
  WishlistResponse,
  WishlistInviteResponse,
  WishlistCreateBody,
  WishlistUpdateBody,
} from '~/types/api'

interface WishlistListData {
  items: WishlistResponse[]
  total: number
  limit: number
  offset: number
}

export const useWishlistsApi = () => {
  async function list(limit = 20, offset = 0): Promise<{ items: WishlistResponse[]; total: number }> {
    const res = await apiFetch<ApiResponse<WishlistListData>>('/api/wishlists', {
      query: { limit, offset },
    })
    return { items: res.data.items, total: res.data.total }
  }

  async function create(body: WishlistCreateBody): Promise<WishlistResponse> {
    const res = await apiFetch<ApiResponse<WishlistResponse>>('/api/wishlists', {
      method: 'POST',
      body,
    })
    return res.data
  }

  async function get(id: string): Promise<WishlistResponse> {
    const res = await apiFetch<ApiResponse<WishlistResponse>>(`/api/wishlists/${id}`)
    return res.data
  }

  async function update(id: string, body: WishlistUpdateBody): Promise<WishlistResponse> {
    const res = await apiFetch<ApiResponse<WishlistResponse>>(`/api/wishlists/${id}`, {
      method: 'PATCH',
      body,
    })
    return res.data
  }

  async function remove(id: string): Promise<void> {
    await apiFetch(`/api/wishlists/${id}`, { method: 'DELETE' })
  }

  async function listInvites(wishlistId: string): Promise<WishlistInviteResponse[]> {
    const res = await apiFetch<ApiResponse<{ items: WishlistInviteResponse[] }>>(
      `/api/wishlists/${wishlistId}/invites`,
    )
    return res.data.items
  }

  async function createInvite(wishlistId: string, email: string): Promise<WishlistInviteResponse> {
    const res = await apiFetch<ApiResponse<WishlistInviteResponse>>(
      `/api/wishlists/${wishlistId}/invites`,
      { method: 'POST', body: { email } },
    )
    return res.data
  }

  async function deleteInvite(wishlistId: string, inviteId: string): Promise<void> {
    await apiFetch(`/api/wishlists/${wishlistId}/invites/${inviteId}`, { method: 'DELETE' })
  }

  return { list, create, get, update, remove, listInvites, createInvite, deleteInvite }
}
