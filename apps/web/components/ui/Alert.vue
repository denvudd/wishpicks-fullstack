<template>
  <Transition name="alert">
    <UAlert v-if="show" v-bind="$attrs" />
  </Transition>
</template>

<script setup lang="ts">
defineProps<{ show: boolean }>()
defineOptions({ inheritAttrs: false })
</script>

<style>
.alert-enter-active,
.alert-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}
.alert-enter-from,
.alert-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
