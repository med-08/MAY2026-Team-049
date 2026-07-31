<script setup>
defineProps({
  value: { type: Number, default: 0 },
})
</script>

<template>
  <div class="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden">
    <div
      class="h-full rounded-full brand-gradient transition-all duration-500"
      :style="{ width: value + '%' }"
    ></div>
  </div>
</template>
