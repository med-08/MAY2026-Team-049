<script setup>
import { computed } from "vue"

const props = defineProps({
  status: String,
})

const styles = {
  Upcoming: "bg-brand-blue/10 text-brand-blue dark:bg-brand-blue/20",
  Completed: "bg-brand-green/10 text-brand-green-dark dark:bg-brand-green/20 dark:text-brand-green",
  Pending: "bg-amber/10 text-amber-600 dark:bg-amber/20 dark:text-amber",
  Overdue: "bg-danger/10 text-danger dark:bg-danger/20",
  "Not Started": "bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
  "In Progress": "bg-brand-blue/10 text-brand-blue dark:bg-brand-blue/20",
  High: "bg-danger/10 text-danger dark:bg-danger/20",
  Medium: "bg-amber/10 text-amber-600 dark:bg-amber/20 dark:text-amber",
  Low: "bg-brand-green/10 text-brand-green-dark dark:bg-brand-green/20 dark:text-brand-green",
  Easy: "bg-brand-green/10 text-brand-green-dark dark:bg-brand-green/20 dark:text-brand-green",
  Hard: "bg-danger/10 text-danger dark:bg-danger/20",
}

const cls = computed(() => styles[props.status] || "bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-300")
</script>

<template>
  <span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold" :class="cls">
    {{ status }}
  </span>
</template>
