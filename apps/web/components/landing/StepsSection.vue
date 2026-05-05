<template>
    <section ref="sectionRef" class="max-w-[1136px] mx-auto px-6 py-24">
      <div class="reveal mb-16" :class="{ visible: inView }">
        <span class="text-[11px] font-bold tracking-[0.12em] uppercase text-muted-gray">
          {{ $t('landing.steps_label') }}
        </span>
      </div>
  
      <div class="grid grid-cols-1 md:grid-cols-3">
        <div
          v-for="(step, i) in steps" :key="i"
          class="reveal step-card px-9 py-10"
          :class="[{ visible: inView }, i > 0 ? 'border-t md:border-t-0 md:border-l border-black/10 dark:border-white/10' : '']"
          :style="{ transitionDelay: inView ? `${i * 0.1}s` : '0s' }"
        >
          <p class="text-[11px] font-bold tracking-[0.1em] text-muted-gray mb-5 tabular-nums">{{ step.n }}</p>
          <h3 class="step-title font-heading font-bold text-[22px] leading-[1.25] tracking-[-0.02em] text-black dark:text-white mb-3.5 inline-block">
            {{ step.title }}
          </h3>
          <p class="text-[15px] text-body-gray dark:text-muted-gray leading-relaxed">{{ step.body }}</p>
        </div>
      </div>
    </section>
  </template>
  
  <script setup lang="ts">
  const { tm } = useI18n()
  const steps = computed(() => tm('landing.steps') as { n: string; title: string; body: string }[])
  const sectionRef = ref<HTMLElement | null>(null)
  const inView = ref(false)
  onMounted(() => {
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) { inView.value = true; obs.disconnect() } },
      { threshold: 0.12 }
    )
    if (sectionRef.value) obs.observe(sectionRef.value)
    onUnmounted(() => obs.disconnect())
  })
  </script>
  
  <style scoped>
  .reveal { opacity: 0; transform: translateY(26px); transition: opacity 0.6s cubic-bezier(0.22,1,0.36,1), transform 0.6s cubic-bezier(0.22,1,0.36,1); }
  .reveal.visible { opacity: 1; transform: translateY(0); }
  .step-title::after { content: ''; display: block; height: 2px; width: 0; background: currentColor; margin-top: 5px; transition: width 0.35s cubic-bezier(0.22,1,0.36,1); }
  .step-card:hover .step-title::after { width: 28px; }
  </style>