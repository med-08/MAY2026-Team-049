<script setup>
import * as Icons from "@heroicons/vue/24/outline"

const props = defineProps({
  label: String,
  value: [String, Number],
  subtitle: String,
  icon: String,
  tone: { type: String, default: "blue" },
})

const toneClasses = {
  blue: "bg-brand-blue/10 text-brand-blue dark:bg-brand-blue/20",
  green: "bg-brand-green/10 text-brand-green-dark dark:bg-brand-green/20 dark:text-brand-green",
  amber: "bg-amber/10 text-amber-600 dark:bg-amber/20 dark:text-amber",
}
</script>

<template>
  <div class="card card-hover p-5 flex items-start gap-4">
    <div class="shrink-0 w-11 h-11 rounded-xl flex items-center justify-center" :class="toneClasses[tone]">
      <component :is="Icons[icon]" class="w-6 h-6" />
    </div>
    <div class="min-w-0">
      <p class="text-2xl font-display font-bold leading-tight">{{ value }}</p>
      <p class="text-sm font-medium text-ink-soft dark:text-slate-300 mt-0.5">{{ label }}</p>
      <p class="text-xs text-ink-soft/70 dark:text-slate-400 mt-0.5">{{ subtitle }}</p>
    </div>
  </div>
</template>
