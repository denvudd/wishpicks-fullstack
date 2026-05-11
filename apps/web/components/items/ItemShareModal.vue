<template>
  <UModal v-model:open="open" :title="t('items.share_title')">
    <template #body>
      <div class="space-y-5">
        <div class="space-y-2">
          <p class="text-muted-gray text-xs font-medium tracking-wide">
            {{ t('items.share_copy_link') }}
          </p>
          <div class="flex gap-2">
            <UInput
              :value="shareUrl"
              readonly
              class="flex-1 font-mono text-xs"
              @click="
                (e: MouseEvent) => (e.target as HTMLInputElement).select()
              "
            />
            <UButton
              color="neutral"
              class="duration-300 ease-in-out"
              :icon="
                copied ? 'i-heroicons-check' : 'i-heroicons-clipboard-document'
              "
              :label="copied ? t('items.share_link_copied') : undefined"
              @click="copyLink"
            />
          </div>
        </div>

        <div class="space-y-2">
          <p class="text-muted-gray text-xs font-medium tracking-wide">
            {{ t('items.share_via') }}
          </p>
          <div class="relative flex items-center justify-center">
            <div class="scrollbar-none flex gap-4 overflow-x-auto">
              <UButton
                v-for="social in socials"
                :key="social.icon"
                variant="outline"
                color="neutral"
                size="lg"
                square
                :icon="social.icon"
                :aria-label="social.name"
                @click="openSocial(social.url)"
              />
            </div>
          </div>
        </div>
      </div>
    </template>
  </UModal>
</template>

<script setup lang="ts">
import type { WishItemResponse } from '~/types/api'

const props = defineProps<{ item: WishItemResponse; slug?: string }>()
const open = defineModel<boolean>('open', { default: false })

const { t } = useI18n()
const localePath = useLocalePath()

const copied = ref(false)

const shareUrl = computed(() => {
  if (import.meta.server) return ''
  const path = props.slug
    ? localePath(`/w/${props.slug}/wish/${props.item.id}`)
    : localePath(`/wishlists/${props.item.wishlist_id}/wish/${props.item.id}`)
  return `${window.location.origin}${path}`
})

const socials = computed(() => {
  const url = encodeURIComponent(shareUrl.value)
  const text = encodeURIComponent(props.item.title)
  return [
    {
      name: 'Telegram',
      icon: 'i-simple-icons-telegram',
      url: `https://t.me/share/url?url=${url}&text=${text}`,
    },
    {
      name: 'WhatsApp',
      icon: 'i-simple-icons-whatsapp',
      url: `https://wa.me/?text=${encodeURIComponent(`${props.item.title} ${shareUrl.value}`)}`,
    },
    {
      name: 'X',
      icon: 'i-simple-icons-x',
      url: `https://twitter.com/intent/tweet?url=${url}&text=${text}`,
    },
    {
      name: 'Facebook',
      icon: 'i-simple-icons-facebook',
      url: `https://www.facebook.com/sharer/sharer.php?u=${url}`,
    },
  ]
})

async function copyLink() {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    copied.value = true
    setTimeout(() => (copied.value = false), 2000)
  } catch {
    // fallback: select input
  }
}

function openSocial(url: string) {
  window.open(url, '_blank', 'noopener,noreferrer,width=600,height=400')
}

watch(open, (val) => {
  if (!val) copied.value = false
})
</script>
