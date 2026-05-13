<template>
  <div
    class="bg-brand-white dark:bg-brand-black font-body flex min-h-screen flex-col"
  >
    <!-- Scroll progress bar -->
    <div
      class="bg-brand-black dark:bg-brand-white pointer-events-none fixed top-0 left-0 z-60 h-[2px] origin-left"
      :style="{ transform: `scaleX(${scrollProgress})` }"
    />

    <!-- Navigation -->
    <header
      class="sticky top-0 z-50 border-b border-black/10 bg-white/90 backdrop-blur-md dark:border-white/10 dark:bg-black/90"
    >
      <div
        class="mx-auto flex h-16 max-w-[1136px] items-center justify-between px-6"
      >
        <NuxtLink
          :to="localePath('/')"
          class="font-heading text-xl font-bold tracking-tight text-black transition-opacity select-none hover:opacity-80 dark:text-white"
        >
          {{ $t('app.name') }}
        </NuxtLink>

        <div class="flex items-center gap-2">
          <UiLanguageSwitcher />

          <UiColorModeToggle />

          <UButton
            color="neutral"
            variant="outline"
            class="rounded-full border-black font-medium dark:border-white"
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
      <LandingHeroSection layout="left" @scroll-to-steps="scrollToSteps" />

      <div class="border-t border-black/10 dark:border-white/10" />

      <div ref="stepsRef">
        <LandingStepsSection />
      </div>

      <div class="border-t border-black/10 dark:border-white/10" />

      <LandingFeaturesSection />

      <div class="border-t border-black/10 dark:border-white/10" />

      <LandingPrivacySection />

      <div class="border-t border-black/10 dark:border-white/10" />

      <LandingCtaSection />
    </main>

    <!-- Footer -->
    <footer class="border-t border-black/10 py-7 dark:border-white/10">
      <div
        class="mx-auto flex max-w-[1136px] flex-wrap items-center justify-between gap-4 px-6"
      >
        <span
          class="text-sm font-bold tracking-tight text-black dark:text-white"
        >
          {{ $t('app.name') }}
        </span>
        <span class="text-muted-gray text-sm">© 2026 Wishpicks</span>
        <div class="flex gap-5">
          <a
            v-for="link in footerLinks"
            :key="link.label"
            :href="link.href"
            class="text-muted-gray text-sm transition-colors hover:text-black dark:hover:text-white"
          >
            {{ link.label }}
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ middleware: 'guest', hideHeader: true })

const localePath = useLocalePath()
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
  {
    label: t('nav.language') === 'Мова' ? 'Конфіденційність' : 'Privacy',
    href: '#',
  },
  { label: t('nav.language') === 'Мова' ? 'Умови' : 'Terms', href: '#' },
  { label: 'GitHub', href: '#' },
])
</script>
