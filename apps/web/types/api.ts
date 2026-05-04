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
