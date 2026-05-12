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

export type ItemPriority = 0 | 1 | 2

export interface WishItemResponse {
  id: string
  wishlist_id: string
  title: string
  description: string | null
  image_url: string | null
  product_url: string | null
  price_min: string | null
  price_max: string | null
  currency: string
  priority: ItemPriority
  is_surprise: boolean
  position: number
  notes: string | null
  tags: string[] | null
  images: string[] | null
  is_reserved: boolean
  is_fulfilled: boolean
  created_at: string
  updated_at: string
}

export interface ItemFilters {
  is_reserved: boolean | null
  is_fulfilled: boolean | null
  priority: number[]
  store: string | null
}

export interface WishItemCreateBody {
  title: string
  description?: string | null
  image_url?: string | null
  product_url?: string | null
  price_min?: number | null
  price_max?: number | null
  currency?: string
  priority?: number
  is_surprise?: boolean
  notes?: string | null
  tags?: string[] | null
  images?: string[] | null
}

export interface WishItemUpdateBody {
  title?: string
  description?: string | null
  image_url?: string | null
  product_url?: string | null
  price_min?: number | null
  price_max?: number | null
  currency?: string | null
  priority?: number | null
  is_surprise?: boolean | null
  notes?: string | null
  tags?: string[] | null
  images?: string[] | null
}

// --- Shared wishlist (public guest view) ---

export interface MyReservation {
  anon_token: string | null
}

export interface SharedItemResponse {
  id: string
  title: string
  description: string | null
  image_url: string | null
  product_url: string | null
  price_min: string | null
  price_max: string | null
  currency: string
  priority: ItemPriority
  position: number
  notes: string | null
  tags: string[] | null
  is_reserved: boolean
  is_fulfilled: boolean
  my_reservation: MyReservation | null
}

export interface SharedWishlistAuthor {
  display_name: string | null
  avatar_url: string | null
}

export interface SharedWishlistMeta {
  id: string
  title: string
  description: string | null
  cover_url: string | null
  event_type: EventType | null
  event_date: string | null
  reservation_mode: ReservationMode
  slug: string
  created_at: string
  author: SharedWishlistAuthor
}

export interface SharedWishlistData {
  wishlist: SharedWishlistMeta
  items: SharedItemResponse[]
}

export interface SharedWishlistResponse {
  data: SharedWishlistData
}

// --- Reservations ---

export interface ReservationResponse {
  id: string
  item_id: string
  reserver_name: string | null
  is_fulfilled: boolean
  anon_token: string | null
  created_at: string
}

export interface ReservationSingleResponse {
  data: ReservationResponse
}
