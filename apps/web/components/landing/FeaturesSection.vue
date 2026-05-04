<template>
    <section ref="sectionRef" class="max-w-[1136px] mx-auto px-6 py-24">
      <div class="reveal mb-16" :class="{ visible: inView }">
        <span class="text-[11px] font-bold tracking-[0.12em] uppercase text-muted-gray">
          {{ $t('landing.features_label') }}
        </span>
      </div>
  
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-px bg-black/10 dark:bg-white/10 border border-black/10 dark:border-white/10 rounded-2xl overflow-hidden">
        <div
          v-for="(feat, i) in features" :key="i"
          class="feat-card reveal bg-white dark:bg-black px-10 py-10"
          :class="{ visible: inView }"
          :style="{ transitionDelay: inView ? `${i * 0.08}s` : '0s' }"
        >
          <div class="feat-icon w-11 h-11 rounded-xl bg-chip-gray dark:bg-white/10 flex items-center justify-center text-xl mb-5">
            {{ feat.icon }}
          </div>
          <h4 class="font-heading font-bold text-lg tracking-[-0.01em] text-black dark:text-white mb-2.5">{{ feat.title }}</h4>
          <p class="text-sm text-body-gray dark:text-muted-gray leading-relaxed">{{ feat.body }}</p>
        </div>
      </div>
    </section>
  </template>
  
  <script setup lang="ts">
  const { tm } = useI18n()
  const features = computed(() => tm('landing.features') as { icon: string; title: string; body: string }[])
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
  .reveal { opacity: 0; transform: translateY(24px); transition: opacity 0.6s cubic-bezier(0.22,1,0.36,1), transform 0.6s cubic-bezier(0.22,1,0.36,1); }
  .reveal.visible { opacity: 1; transform: translateY(0); }
  .feat-card { transition: background 0.18s, transform 0.22s cubic-bezier(0.22,1,0.36,1); }
  .feat-card:hover { transform: translateY(-3px); }
  .feat-card:hover .feat-icon { animation: wpWiggle 0.4s cubic-bezier(0.22,1,0.36,1); }
  @keyframes wpWiggle {
    0%   { transform: scale(1) rotate(0deg); }   40%  { transform: scale(1.15) rotate(-6deg); }
    70%  { transform: scale(1.08) rotate(4deg); } 100% { transform: scale(1) rotate(0deg); }
  }
  </style>