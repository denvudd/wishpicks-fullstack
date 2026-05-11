import type { SharedItemResponse, SharedWishlistMeta, SharedWishlistResponse } from '~/types/api'

export const useSharedWishlist = (slug: MaybeRefOrGetter<string>) => {
  const config = useRuntimeConfig()
  const baseURL = import.meta.server
    ? (config.apiBaseUrl || config.public.apiBaseUrl)
    : config.public.apiBaseUrl

  const { data, pending, error } = useFetch<SharedWishlistResponse>(
    () => `/api/w/${toValue(slug)}`,
    {
      baseURL,
      credentials: 'include',
    },
  )

  const wishlist = computed<SharedWishlistMeta | null>(() => data.value?.data.wishlist ?? null)
  const items = computed<SharedItemResponse[]>(() => data.value?.data.items ?? [])

  return { wishlist, items, pending, error }
}
