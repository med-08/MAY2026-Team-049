<script setup>
import { ArrowRightOnRectangleIcon } from "@heroicons/vue/24/outline"

defineProps({ open: Boolean })
const emit = defineEmits(["cancel", "confirm"])
</script>

<template>
  <Transition name="fade">
    <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="emit('cancel')"></div>
      <div class="card relative w-full max-w-sm p-6 text-center">
        <div class="w-12 h-12 rounded-full bg-danger/10 text-danger flex items-center justify-center mx-auto mb-4">
          <ArrowRightOnRectangleIcon class="w-6 h-6" />
        </div>
        <h3 class="font-display font-bold text-lg">Log out of LearnAtHome?</h3>
        <p class="text-sm text-ink-soft dark:text-slate-400 mt-1.5">You'll need to sign in again to access your dashboard.</p>
        <div class="flex gap-3 mt-6">
          <button
            class="flex-1 py-2.5 rounded-xl font-semibold text-sm border border-slate-200 dark:border-border-dark hover:bg-slate-50 dark:hover:bg-white/5 transition"
            @click="emit('cancel')"
          >
            Cancel
          </button>
          <button
            class="flex-1 py-2.5 rounded-xl font-semibold text-sm text-white bg-danger hover:bg-red-600 transition"
            @click="emit('confirm')"
          >
            Logout
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .18s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
