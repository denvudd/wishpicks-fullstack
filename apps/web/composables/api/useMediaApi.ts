import { apiFetch } from '~/composables/useApiFetch'

export const useMediaApi = () => {
  async function uploadImage(file: File, folder: string): Promise<string> {
    const form = new FormData()
    form.append('file', file)
    form.append('folder', folder)
    const res = await apiFetch<{ data: { url: string } }>('/api/media/upload', {
      method: 'POST',
      body: form,
    })
    return res.data.url
  }

  return { uploadImage }
}
