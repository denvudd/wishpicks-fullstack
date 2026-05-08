export interface ApiResponse<T> {
  data: T
}

export interface ValidationDetail {
  field: string
  message: string
}

export interface ApiError {
  code: string
  message: string
  details?: ValidationDetail[]
}

export interface ApiErrorResponse {
  error: ApiError
}

/** Shape of the error thrown by $fetch when the API returns a non-2xx response */
export interface ApiFetchError {
  status?: number
  statusText?: string
  data?: ApiErrorResponse
  message?: string
}

export type WishlistVisibility = 'public' | 'link_only' | 'private'
export type ReservationMode = 'anonymous' | 'registered_only'
export type EventType = 'birthday' | 'wedding' | 'anniversary' | 'new_year' | 'other'

export interface WishlistResponse {
  id: string
  title: string
  description: string | null
  visibility: WishlistVisibility
  event_type: EventType | null
  event_date: string | null
  reservation_mode: ReservationMode
  slug: string
  cover_url: string | null
  item_count: number
  created_at: string
  updated_at: string
}

export interface WishlistInviteResponse {
  id: string
  wishlist_id: string
  email: string
  invited_at: string
}

export interface WishlistCreateBody {
  title: string
  description?: string | null
  visibility: WishlistVisibility
  event_type?: EventType | null
  event_date?: string | null
  reservation_mode: ReservationMode
}

export interface WishlistUpdateBody {
  title?: string
  description?: string | null
  visibility?: WishlistVisibility
  event_type?: EventType | null
  event_date?: string | null
  reservation_mode?: ReservationMode
}
