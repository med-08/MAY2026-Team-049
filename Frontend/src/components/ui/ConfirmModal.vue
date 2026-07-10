<script setup>
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: 'Are you sure?' },
  message: { type: String, default: 'This action cannot be undone.' },
  confirmLabel: { type: String, default: 'Delete' }
})
const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <transition name="fade">
    <div v-if="open" class="fixed inset-0 z-[90] flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="emit('cancel')" />
      <div class="relative card w-full max-w-sm p-6 shadow-soft-lg">
        <div class="w-11 h-11 rounded-full bg-rose-100 dark:bg-rose-500/10 flex items-center justify-center mb-4">
          <ExclamationTriangleIcon class="w-6 h-6 text-rose-500" />
        </div>
        <h3 class="text-lg font-semibold font-display text-slate-800 dark:text-slate-100 mb-1.5">{{ title }}</h3>
        <p class="text-sm text-slate-500 dark:text-slate-400 mb-6">{{ message }}</p>
        <div class="flex justify-end gap-2.5">
          <button class="btn-secondary" @click="emit('cancel')">Cancel</button>
          <button
            class="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-rose-500 hover:bg-rose-600 text-white text-sm font-semibold transition-colors duration-200"
            @click="emit('confirm')"
          >
            {{ confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
