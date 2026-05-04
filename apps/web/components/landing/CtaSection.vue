<template>
    <section ref="sectionRef" class="py-28">
      <div class="max-w-[1136px] mx-auto px-6">
        <div class="reveal flex flex-col items-center text-center max-w-[560px] mx-auto" :class="{ visible: inView }">
          <h2
            class="font-heading font-bold tracking-[-0.03em] leading-[1.18] text-black dark:text-white mb-5"
            style="font-size: clamp(2rem, 4vw, 3rem)"
          >
            {{ $t('landing.cta_title') }}
          </h2>
          <p class="text-[17px] text-body-gray dark:text-muted-gray leading-relaxed mb-9">
            {{ $t('landing.cta_sub') }}
          </p>
          <UButton
            size="xl" color="neutral" variant="solid"
            class="rounded-full px-9 font-medium cta-btn"
            trailing-icon="i-lucide-arrow-right"
            :to="localePath('/register')"
          >
            {{ $t('landing.cta_btn') }}
          </UButton>
          <p class="mt-5 text-sm text-muted-gray">
            {{ $t('landing.cta_signin') }}
            <NuxtLink
              :to="localePath('/login')"
              class="font-medium text-black dark:text-white underline underline-offset-4 hover:opacity-70 transition-opacity"
            >
              {{ $t('auth.login.submit') }}
            </NuxtLink>
          </p>
        </div>
      </div>
    </section>
  </template>
  
  <script setup lang="ts">
  const localePath = useLocalePath()
  const sectionRef = ref<HTMLElement | null>(null)
  const inView = ref(false)
  onMounted(() => {
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) { inView.value = true; obs.disconnect() } },
      { threshold: 0.15 }
    )
    if (sectionRef.value) obs.observe(sectionRef.value)
    onUnmounted(() => obs.disconnect())
  })
  </script>
  
  <style scoped>
  .reveal { opacity: 0; transform: translateY(24px); transition: opacity 0.6s cubic-bezier(0.22,1,0.36,1), transform 0.6s cubic-bezier(0.22,1,0.36,1); }
  .reveal.visible { opacity: 1; transform: translateY(0); }
  .cta-btn :deep([class*='i-lucide-arrow-right']) { transition: transform 0.2s cubic-bezier(0.22,1,0.36,1); }
  .cta-btn:hover :deep([class*='i-lucide-arrow-right']) { transform: translateX(4px); }
  </style>