<script setup>
import { ChevronLeftIcon, ChevronRightIcon } from '@heroicons/vue/24/outline'
import { computed } from 'vue'

const props = defineProps({
  page: { type: Number, required: true },
  perPage: { type: Number, required: true },
  total: { type: Number, required: true }
})
const emit = defineEmits(['update:page'])

const totalPages = computed(() => Math.max(1, Math.ceil(props.total / props.perPage)))
const rangeStart = computed(() => (props.total === 0 ? 0 : (props.page - 1) * props.perPage + 1))
const rangeEnd = computed(() => Math.min(props.page * props.perPage, props.total))

function go(p) {
  if (p < 1 || p > totalPages.value) return
  emit('update:page', p)
}
</script>

<template>
  <div class="flex items-center justify-between flex-wrap gap-3 px-1 py-3">
    <p class="text-xs text-slate-500 dark:text-slate-400">
      Showing <span class="font-semibold text-slate-700 dark:text-slate-200">{{ rangeStart }}–{{ rangeEnd }}</span>
      of <span class="font-semibold text-slate-700 dark:text-slate-200">{{ total }}</span>
    </p>
    <div class="flex items-center gap-1.5">
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        :disabled="page === 1"
        @click="go(page - 1)"
      >
        <ChevronLeftIcon class="w-4 h-4" />
      </button>
      <button
        v-for="p in totalPages"
        :key="p"
        class="w-8 h-8 flex items-center justify-center rounded-lg text-xs font-semibold transition-colors"
        :class="p === page
          ? 'bg-gradient-to-r from-brand-green-500 to-brand-blue-500 text-white shadow-soft'
          : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'"
        @click="go(p)"
      >
        {{ p }}
      </button>
      <button
        class="w-8 h-8 flex items-center justify-center rounded-lg border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        :disabled="page === totalPages"
        @click="go(page + 1)"
      >
        <ChevronRightIcon class="w-4 h-4" />
      </button>
    </div>
  </div>
</template>
