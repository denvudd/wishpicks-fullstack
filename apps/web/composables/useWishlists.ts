import type {
  WishlistResponse,
  WishlistInviteResponse,
  WishlistCreateBody,
  WishlistUpdateBody,
  ApiFetchError,
} from '~/types/api'
import { useWishlistsApi } from './api/useWishlistsApi'

export const useWishlists = () => {
  const store = useWishlistStore()
  const api = useWishlistsApi()

  const invites = ref<WishlistInviteResponse[]>([])

  const wishlists = computed(() => store.wishlists)
  const current = computed(() => store.current)
  const isLoading = computed(() => store.status === 'loading')

  async function fetchList(): Promise<void> {
    store.setStatus('loading')
    try {
      const { items, total } = await api.list()
      store.setList(items, total)
    } catch {
      store.setStatus('error')
    }
  }

  async function fetchOne(id: string): Promise<WishlistResponse | null> {
    store.setStatus('loading')
    try {
      const wishlist = await api.get(id)
      store.setCurrent(wishlist)
      store.setStatus('idle')
      return wishlist
    } catch (err: unknown) {
      const status = (err as ApiFetchError)?.status
      if (status === 403 || status === 404) {
        store.setCurrent(null)
        store.setStatus('idle')
        return null
      }
      store.setStatus('error')
      return null
    }
  }

  async function create(body: WishlistCreateBody): Promise<WishlistResponse> {
    const wishlist = await api.create(body)
    store.prependOne(wishlist)
    return wishlist
  }

  async function update(id: string, body: WishlistUpdateBody): Promise<WishlistResponse> {
    const wishlist = await api.update(id, body)
    store.updateOne(wishlist)
    return wishlist
  }

  async function remove(id: string): Promise<void> {
    await api.remove(id)
    store.removeOne(id)
  }

  async function fetchInvites(wishlistId: string): Promise<void> {
    invites.value = await api.listInvites(wishlistId)
  }

  async function addInvite(wishlistId: string, email: string): Promise<void> {
    const invite = await api.createInvite(wishlistId, email)
    invites.value.push(invite)
  }

  async function removeInvite(wishlistId: string, inviteId: string): Promise<void> {
    await api.deleteInvite(wishlistId, inviteId)
    invites.value = invites.value.filter((i) => i.id !== inviteId)
  }

  return {
    wishlists,
    current,
    isLoading,
    invites,
    fetchList,
    fetchOne,
    create,
    update,
    remove,
    fetchInvites,
    addInvite,
    removeInvite,
  }
}
