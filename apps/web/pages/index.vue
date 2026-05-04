<template>
  <div class="min-h-screen flex flex-col bg-brand-white dark:bg-brand-black font-body">

    <!-- Scroll progress bar -->
    <div
      class="fixed top-0 left-0 h-[2px] bg-brand-black dark:bg-brand-white z-60 origin-left pointer-events-none"
      :style="{ transform: `scaleX(${scrollProgress})` }"
    />

    <!-- Navigation -->
    <header class="sticky top-0 z-50 bg-white/90 dark:bg-black/90 backdrop-blur-md border-b border-black/10 dark:border-white/10">
      <div class="max-w-[1136px] mx-auto px-6 h-16 flex items-center justify-between">
        <NuxtLink
          :to="localePath('/')"
          class="text-xl font-bold font-heading text-black dark:text-white tracking-tight select-none hover:opacity-80 transition-opacity"
        >
          {{ $t('app.name') }}
        </NuxtLink>

        <div class="flex items-center gap-2">
          <LanguageSwitcher />

          <ClientOnly>
            <button
              class="w-9 h-9 rounded-full flex items-center justify-center text-black dark:text-white hover:bg-chip-gray dark:hover:bg-white/10 transition-all duration-200 theme-toggle"
              :aria-label="colorMode.value === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
              @click="colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark'"
            >
              <UIcon
                :name="colorMode.value === 'dark' ? 'i-lucide-sun' : 'i-lucide-moon'"
                class="w-4 h-4"
              />
            </button>
            <template #fallback>
              <button
                class="w-9 h-9 rounded-full flex items-center justify-center text-black dark:text-white hover:bg-chip-gray dark:hover:bg-white/10 transition-all duration-200 theme-toggle"
                aria-label="Toggle theme"
              >
                <UIcon name="i-lucide-moon" class="w-4 h-4" />
              </button>
            </template>
          </ClientOnly>

          <UButton
            color="neutral"
            variant="outline"
            class="rounded-full border-black dark:border-white font-medium"
            :to="localePath('/login')"
          >
            {{ $t('auth.login.submit') }}
          </UButton>

          <UButton
            color="neutral"
            variant="solid"
            class="rounded-full font-medium"
            :to="localePath('/register')"
          >
            {{ $t('auth.register.submit') }}
          </UButton>
        </div>
      </div>
    </header>

    <main class="flex-1">
      <HeroSection layout="left" @scroll-to-steps="scrollToSteps" />

      <div class="border-t border-black/10 dark:border-white/10" />

      <div ref="stepsRef">
        <StepsSection />
      </div>

      <div class="border-t border-black/10 dark:border-white/10" />

      <FeaturesSection />

      <div class="border-t border-black/10 dark:border-white/10" />

      <PrivacySection />

      <div class="border-t border-black/10 dark:border-white/10" />

      <CtaSection />
    </main>

    <!-- Footer -->
    <footer class="border-t border-black/10 dark:border-white/10 py-7">
      <div class="max-w-[1136px] mx-auto px-6 flex items-center justify-between flex-wrap gap-4">
        <span class="text-sm font-bold tracking-tight text-black dark:text-white">
          {{ $t('app.name') }}
        </span>
        <span class="text-sm text-muted-gray">© 2026 Wishpicks</span>
        <div class="flex gap-5">
          <a
            v-for="link in footerLinks"
            :key="link.label"
            :href="link.href"
            class="text-sm text-muted-gray hover:text-black dark:hover:text-white transition-colors"
          >
            {{ link.label }}
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import CtaSection from '~/components/landing/CtaSection.vue'
import FeaturesSection from '~/components/landing/FeaturesSection.vue'
import HeroSection from '~/components/landing/HeroSection.vue'
import PrivacySection from '~/components/landing/PrivacySection.vue'
import StepsSection from '~/components/landing/StepsSection.vue'
import LanguageSwitcher from '~/components/ui/LanguageSwitcher.vue'

definePageMeta({ middleware: 'guest' })

const localePath = useLocalePath()
const colorMode = useColorMode()
const { t } = useI18n()

const scrollProgress = ref(0)
function onScroll() {
  const el = document.documentElement
  scrollProgress.value = el.scrollTop / (el.scrollHeight - el.clientHeight) || 0
}
onMounted(() => window.addEventListener('scroll', onScroll, { passive: true }))
onUnmounted(() => window.removeEventListener('scroll', onScroll))

const stepsRef = ref<HTMLElement | null>(null)
function scrollToSteps() {
  if (!stepsRef.value) return
  const top = stepsRef.value.getBoundingClientRect().top + window.scrollY - 80
  window.scrollTo({ top, behavior: 'smooth' })
}

const footerLinks = computed(() => [
  { label: t('nav.language') === 'Мова' ? 'Конфіденційність' : 'Privacy', href: '#' },
  { label: t('nav.language') === 'Мова' ? 'Умови' : 'Terms', href: '#' },
  { label: 'GitHub', href: '#' },
])
</script>

<style scoped>
.theme-toggle {
  transition: background 0.15s, transform 0.2s cubic-bezier(0.22, 1, 0.36, 1);
}
.theme-toggle:hover { transform: rotate(18deg); }
</style>