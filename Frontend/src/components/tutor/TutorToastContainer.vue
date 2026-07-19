<template>
  <div class="toasts" aria-live="polite" aria-atomic="true">
    <div v-for="toast in toasts" :key="toast.id" class="toast in">
      <span class="tic"><svg viewBox="0 0 24 24"><path d="m5 12 4 4 10-10"/></svg></span>
      <span>{{ toast.message }}</span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  toasts: { type: Array, required: true }
})
</script>
