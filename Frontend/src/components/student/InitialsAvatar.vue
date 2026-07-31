<script setup>
const props = defineProps({
  initials: String,
  size: { type: String, default: "sm" }, // "sm" | "lg"
})

const sizeClasses = {
  sm: "w-9 h-9 text-sm ring-2",
  lg: "w-24 h-24 text-3xl ring-4",
}
</script>

<template>
  <div
    class="rounded-full brand-gradient text-white font-display font-bold flex items-center justify-center shrink-0 ring-white dark:ring-card-dark select-none"
    :class="sizeClasses[size]"
  >
    {{ initials }}
  </div>
</template>
