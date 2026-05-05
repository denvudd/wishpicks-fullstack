<template>
  <section class="mx-auto max-w-[1136px] px-6 pt-24 pb-20" :class="{ 'hero-loaded': loaded }">
    <div
      class="grid items-center gap-16"
      :class="
        layout === 'center' ? 'grid-cols-1' : 'grid-cols-1 lg:grid-cols-2'
      "
    >
      <!-- Copy -->
      <div
        class="hero-copy"
        :class="layout === 'center' ? 'mx-auto max-w-2xl text-center' : ''"
      >
        <div
          class="bg-chip-gray text-body-gray dark:text-muted-gray hero-badge mb-7 inline-flex items-center gap-2 rounded-full px-3.5 py-1.5 text-xs font-medium dark:bg-white/10"
        >
          <span
            class="pulse-dot h-1.5 w-1.5 rounded-full bg-black dark:bg-white"
          />
          {{ $t('landing.badge') }}
        </div>

        <h1
          class="font-heading hero-h1 mb-6 leading-[1.18] font-bold tracking-[-0.03em] whitespace-pre-line text-black dark:text-white"
          style="font-size: clamp(2.4rem, 5vw, 3.5rem)"
        >
          {{ $t('landing.title') }}
        </h1>

        <p
          class="text-body-gray dark:text-muted-gray hero-sub mb-8 text-lg leading-relaxed"
          :class="
            layout === 'center' ? 'mx-auto max-w-[440px]' : 'max-w-[440px]'
          "
        >
          {{ $t('landing.tagline') }}
        </p>

        <div
          class="hero-btns flex flex-wrap gap-3"
          :class="layout === 'center' ? 'justify-center' : ''"
        >
          <UButton
            size="lg"
            color="neutral"
            variant="solid"
            class="rounded-full px-7 font-medium"
            trailing-icon="i-lucide-arrow-right"
            :to="localePath('/register')"
          >
            {{ $t('landing.register') }}
          </UButton>
          <UButton
            size="lg"
            color="neutral"
            variant="outline"
            class="rounded-full border-black px-7 font-medium dark:border-white"
            @click="$emit('scroll-to-steps')"
          >
            {{ $t('landing.login') }}
          </UButton>
        </div>

        <p class="text-muted-gray hero-note mt-5 text-sm">
          {{ $t('landing.note') }}
        </p>
      </div>

      <div v-if="layout !== 'center'" class="hero-preview flex justify-end">
        <WishlistPreview />
      </div>
    </div>

    <div
      v-if="layout === 'center'"
      class="hero-preview mt-16 flex justify-center"
    >
      <WishlistPreview />
    </div>
  </section>
</template>

<script setup lang="ts">
import WishlistPreview from './WishlistPreview.vue'

defineProps<{ layout?: 'left' | 'center' }>()
defineEmits<{ 'scroll-to-steps': [] }>()

const localePath = useLocalePath()
const loaded = ref(false)

onMounted(() => {
  requestAnimationFrame(() => {
    setTimeout(() => { loaded.value = true }, 60)
  })
})
</script>

<style scoped>
.hero-badge,
.hero-h1,
.hero-sub,
.hero-btns,
.hero-note,
.hero-preview {
  opacity: 0;
}
.hero-badge {
  transform: translateY(14px);
}
.hero-h1 {
  transform: translateY(18px);
}
.hero-sub {
  transform: translateY(18px);
}
.hero-btns {
  transform: translateY(18px);
}
.hero-note {
  transform: translateY(10px);
}
.hero-preview {
  transform: translateX(28px) scale(0.97);
}

.hero-loaded .hero-badge {
  animation: wpFadeUp 0.55s cubic-bezier(0.22, 1, 0.36, 1) 0.05s forwards;
}
.hero-loaded .hero-h1 {
  animation: wpFadeUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.15s forwards;
}
.hero-loaded .hero-sub {
  animation: wpFadeUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.25s forwards;
}
.hero-loaded .hero-btns {
  animation: wpFadeUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) 0.33s forwards;
}
.hero-loaded .hero-note {
  animation: wpFadeUp 0.5s cubic-bezier(0.22, 1, 0.36, 1) 0.42s forwards;
}
.hero-loaded .hero-preview {
  animation: wpSlideRight 0.75s cubic-bezier(0.22, 1, 0.36, 1) 0.2s forwards;
}

@keyframes wpFadeUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
@keyframes wpSlideRight {
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

.pulse-dot {
  animation: wpPulse 2.2s ease-in-out infinite;
}
@keyframes wpPulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.4;
    transform: scale(0.65);
  }
}
</style>
