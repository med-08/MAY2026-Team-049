<script setup>
defineProps({
  title: String,
  subtitle: String,
})
</script>

<template>
  <div class="mb-6">
    <h1 class="text-2xl md:text-3xl font-display font-bold">{{ title }}</h1>
    <p v-if="subtitle" class="text-sm text-ink-soft dark:text-slate-400 mt-1">{{ subtitle }}</p>
  </div>
</template>
