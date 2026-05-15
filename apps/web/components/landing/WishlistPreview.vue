<template>
    <div class="w-full max-w-[400px] rounded-[20px] overflow-hidden shadow-medium bg-white dark:bg-[#111]">
      <!-- Browser chrome -->
      <div class="flex items-center gap-2 px-5 py-3 bg-hover-light dark:bg-black border-b border-black/[0.07] dark:border-white/[0.08]">
        <div class="flex gap-1.5">
          <span class="w-2.5 h-2.5 rounded-full bg-[#ff5f57]" />
          <span class="w-2.5 h-2.5 rounded-full bg-[#febc2e]" />
          <span class="w-2.5 h-2.5 rounded-full bg-[#28c840]" />
        </div>
        <div class="flex-1 flex items-center justify-center gap-1.5 h-6 bg-chip-gray dark:bg-white/10 rounded-md text-muted-gray">
          <UIcon name="i-lucide-link" class="w-3 h-3" />
          <span class="text-[11px] font-mono">{{ $t('landing.preview_url') }}</span>
        </div>
      </div>
  
      <div class="px-5 pt-6 pb-5">
        <p class="font-heading font-bold text-lg text-black dark:text-white">{{ $t('landing.preview_title') }}</p>
        <p class="text-[13px] text-body-gray dark:text-muted-gray mt-0.5">{{ $t('landing.preview_sub') }}</p>
  
        <div class="h-px bg-black/[0.07] dark:bg-white/[0.08] my-4" />
  
        <div class="flex flex-col gap-2.5">
          <div
            v-for="(item, i) in items" :key="i"
            class="flex items-center gap-3 px-3.5 py-3 rounded-xl bg-hover-light dark:bg-white/[0.04] border border-black/[0.06] dark:border-white/[0.07]"
          >
            <div class="w-11 h-11 shrink-0 rounded-lg bg-chip-gray dark:bg-[#1e1e1e] flex items-center justify-center">
              <UIcon name="i-lucide-image" class="w-4 h-4 text-muted-gray dark:text-[#4b4b4b]" />
            </div>
  
            <div class="flex-1 min-w-0">
              <p
                class="text-sm font-medium truncate transition-colors"
                :class="reserved[i] ? 'text-muted-gray line-through' : 'text-black dark:text-white'"
              >{{ item.name }}</p>
              <p class="text-xs text-muted-gray mt-0.5">{{ item.price }}</p>
            </div>
  
            <button
              :ref="el => { if (el) btnRefs[i] = el as HTMLButtonElement }"
              class="shrink-0 rounded-full px-3.5 py-1.5 text-xs font-medium transition-all duration-200 font-body"
              :class="reserved[i]
                ? 'bg-chip-gray dark:bg-white/[0.06] text-muted-gray cursor-default'
                : 'bg-black dark:bg-white text-white dark:text-black hover:scale-105 active:scale-95'"
              @click="handleReserve(i)"
            >
              <span v-if="reserved[i]" class="flex items-center gap-1">
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <polyline
                    points="20 6 9 17 4 12"
                    :class="drawn[i] ? 'check-drawn' : 'check-idle'"
                    class="check-path"
                  />
                </svg>
                {{ $t('landing.reserved') }}
              </span>
              <span v-else>{{ $t('landing.reserve') }}</span>
            </button>
          </div>
        </div>
  
        <p class="mt-4 text-[11px] text-center text-muted-gray dark:text-[#4b4b4b] leading-relaxed">
          {{ $t('landing.preview_note') }}
        </p>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  const { tm } = useI18n()
  const items = computed(() => tm('landing.preview_items') as { name: string; price: string }[])
  
  const reserved = ref<Record<number, boolean>>({ 1: true })
  const drawn = ref<Record<number, boolean>>({ 1: true })
  const btnRefs = ref<Record<number, HTMLButtonElement>>({})
  
  function handleReserve(i: number) {
    if (reserved.value[i]) return
    const btn = btnRefs.value[i]
    if (btn) {
      btn.classList.add('reserve-bounce')
      btn.addEventListener('animationend', () => btn.classList.remove('reserve-bounce'), { once: true })
    }
    reserved.value = { ...reserved.value, [i]: true }
    setTimeout(() => { drawn.value = { ...drawn.value, [i]: true } }, 80)
  }
  </script>
  
  <style scoped>
  .reserve-bounce { animation: wpBounce 0.42s cubic-bezier(0.22,1,0.36,1); }
  @keyframes wpBounce {
    0%   { transform: scale(1); }   28%  { transform: scale(0.87); }
    58%  { transform: scale(1.13); } 80%  { transform: scale(0.96); }
    100% { transform: scale(1); }
  }
  .check-path { stroke-dasharray: 28; }
  .check-idle   { stroke-dashoffset: 28; transition: none; }
  .check-drawn  { stroke-dashoffset: 0; transition: stroke-dashoffset 0.35s cubic-bezier(0.22,1,0.36,1) 0.06s; }
  </style>