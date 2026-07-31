<script setup>
import { CheckCircleIcon, XCircleIcon, XMarkIcon } from '@heroicons/vue/24/solid'
import { useToast } from '../../composables/useToast'

const { toasts, dismissToast } = useToast()
</script>

<template>
  <div class="fixed top-5 right-5 z-[100] flex flex-col gap-2.5 w-[min(360px,90vw)]">
    <transition-group name="toast">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="card flex items-start gap-3 px-4 py-3.5 shadow-soft-lg border-l-4"
        :class="t.type === 'success' ? 'border-l-brand-green-500' : 'border-l-rose-500'"
      >
        <CheckCircleIcon v-if="t.type === 'success'" class="w-5 h-5 text-brand-green-500 shrink-0 mt-0.5" />
        <XCircleIcon v-else class="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
        <p class="text-sm text-slate-700 dark:text-slate-200 flex-1">{{ t.message }}</p>
        <button @click="dismissToast(t.id)" class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200">
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.toast-enter-active, .toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
