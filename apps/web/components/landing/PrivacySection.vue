<template>
    <section ref="sectionRef" class="max-w-[1136px] mx-auto px-6 py-24">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-20 items-center">
        <div class="reveal reveal-left" :class="{ visible: inView }">
          <span class="block text-[11px] font-bold tracking-[0.12em] uppercase text-muted-gray mb-6">
            {{ $t('landing.privacy_label') }}
          </span>
          <h2
            class="font-heading font-bold tracking-[-0.03em] leading-[1.2] text-black dark:text-white mb-5"
            style="font-size: clamp(1.8rem, 3vw, 2.6rem)"
          >
            {{ $t('landing.privacy_heading_1') }}<br />
            <span class="text-muted-gray dark:text-[#6b6b6b]">{{ $t('landing.privacy_heading_2') }}</span>
          </h2>
          <p class="text-base text-body-gray dark:text-muted-gray leading-relaxed max-w-[380px] mb-8">
            {{ $t('landing.privacy_body') }}
          </p>
          <div class="flex flex-col gap-3">
            <div
              v-for="(bullet, i) in bullets" :key="i"
              class="reveal" :class="{ visible: inView }"
              :style="{ transitionDelay: inView ? `${0.15 + i * 0.1}s` : '0s' }"
            >
              <div class="flex items-center gap-2.5">
                <div class="w-[22px] h-[22px] rounded-full bg-black dark:bg-white flex items-center justify-center shrink-0">
                  <UIcon name="i-lucide-check" class="w-3 h-3 text-white dark:text-black" style="stroke-width:3" />
                </div>
                <span class="text-[15px] text-body-gray dark:text-muted-gray">{{ bullet }}</span>
              </div>
            </div>
          </div>
        </div>
  
        <div class="reveal reveal-right flex justify-end" :class="{ visible: inView }" style="transition-delay:0.05s">
          <LandingWishlistPreview />
        </div>
      </div>
    </section>
  </template>
  
  <script setup lang="ts">
  const { tm } = useI18n()
  const bullets = computed(() => tm('landing.bullets') as string[])
  const sectionRef = ref<HTMLElement | null>(null)
  const inView = ref(false)
  onMounted(() => {
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) { inView.value = true; obs.disconnect() } },
      { threshold: 0.1 }
    )
    if (sectionRef.value) obs.observe(sectionRef.value)
    onUnmounted(() => obs.disconnect())
  })
  </script>
  
  <style scoped>
  .reveal { opacity: 0; transform: translateY(24px); transition: opacity 0.65s cubic-bezier(0.22,1,0.36,1), transform 0.65s cubic-bezier(0.22,1,0.36,1); }
  .reveal.visible { opacity: 1; transform: translateY(0); }
  .reveal-left  { transform: translateX(-28px); }
  .reveal-right { transform: translateX(28px); }
  .reveal-left.visible  { transform: translateX(0); }
  .reveal-right.visible { transform: translateX(0); }
  </style>