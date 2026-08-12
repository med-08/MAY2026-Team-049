<script setup>
import { InboxIcon } from '@heroicons/vue/24/outline'
defineProps({
  title: { type: String, default: 'Nothing here yet' },
  message: { type: String, default: 'Try adjusting your search or filters.' }
})
</script>

<template>
  <div class="flex flex-col items-center justify-center text-center py-16 px-4">
    <div class="w-14 h-14 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center mb-4">
      <InboxIcon class="w-7 h-7 text-slate-400" />
    </div>
    <h4 class="font-display font-semibold text-slate-700 dark:text-slate-200 mb-1">{{ title }}</h4>
    <p class="text-sm text-slate-500 dark:text-slate-400 max-w-xs">{{ message }}</p>
  </div>
</template>
