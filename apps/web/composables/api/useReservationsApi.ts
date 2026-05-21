import { apiFetch } from '~/composables/useApiFetch'
import type { ApiResponse, MyReservationListData, ReservationSingleResponse } from '~/types/api'

export const useReservationsApi = () => {
  async function reserve(
    itemId: string,
    name?: string,
  ): Promise<ReservationSingleResponse> {
    return apiFetch<ReservationSingleResponse>(`/api/items/${itemId}/reserve`, {
      method: 'POST',
      body: { reserver_name: name ?? null },
    })
  }

  async function cancel(itemId: string, anonToken?: string): Promise<void> {
    await apiFetch(`/api/items/${itemId}/reserve`, {
      method: 'DELETE',
      headers: anonToken ? { 'X-Anon-Token': anonToken } : {},
    })
  }

  async function fulfill(
    itemId: string,
    isFulfilled: boolean,
    anonToken?: string,
  ): Promise<void> {
    await apiFetch(`/api/items/${itemId}/reserve/fulfill`, {
      method: 'PATCH',
      body: { is_fulfilled: isFulfilled },
      headers: anonToken ? { 'X-Anon-Token': anonToken } : {},
    })
  }

  async function listMine(limit = 50, offset = 0): Promise<MyReservationListData> {
    const res = await apiFetch<ApiResponse<MyReservationListData>>('/api/reservations', {
      query: { limit, offset },
    })
    return res.data
  }

  return { reserve, cancel, fulfill, listMine }
}
