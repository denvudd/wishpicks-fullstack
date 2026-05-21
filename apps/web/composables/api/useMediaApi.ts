import { apiFetch } from '~/composables/useApiFetch'

export interface UploadedImage {
  url: string
  width: number
  height: number
}

export const useMediaApi = () => {
  async function uploadImage(file: File, folder: string): Promise<UploadedImage> {
    const form = new FormData()
    form.append('file', file)
    form.append('folder', folder)
    const res = await apiFetch<{ data: UploadedImage }>('/api/media/upload', {
      method: 'POST',
      body: form,
    })
    return res.data
  }

  return { uploadImage }
}
