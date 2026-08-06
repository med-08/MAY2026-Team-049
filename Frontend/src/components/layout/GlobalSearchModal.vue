<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import {
  MagnifyingGlassIcon,
  UserGroupIcon,
  AcademicCapIcon,
  HomeIcon,
  XMarkIcon,
} from '@heroicons/vue/24/outline'

import { adminApi } from '../../services/adminApi'

const props = defineProps({
  open: { type: Boolean, default: false },
})
const emit = defineEmits(['close'])

const router = useRouter()
const inputRef = ref(null)

const query = ref('')
const loading = ref(false)
const error = ref(null)
const results = ref({ students: [], tutors: [], parents: [] })
const activeIndex = ref(-1)

const GROUPS = [
  { key: 'students', label: 'Students', routeName: 'students', icon: UserGroupIcon, accent: 'text-emerald-500 bg-emerald-100 dark:bg-emerald-500/20' },
  { key: 'tutors', label: 'Tutors', routeName: 'tutors', icon: AcademicCapIcon, accent: 'text-blue-500 bg-blue-100 dark:bg-blue-500/20' },
  { key: 'parents', label: 'Parents', routeName: 'parents', icon: HomeIcon, accent: 'text-violet-500 bg-violet-100 dark:bg-violet-500/20' },
]

// Flattened list (in display order) so arrow-key navigation and Enter can
// share one index across all three groups.
const flatResults = computed(() => {
  const flat = []
  for (const group of GROUPS) {
    for (const item of results.value[group.key] || []) {
      flat.push({ ...item, group })
    }
  }
  return flat
})

const hasQuery = computed(() => query.value.trim().length >= 2)
const hasResults = computed(() => flatResults.value.length > 0)

let debounceTimer = null
let requestSeq = 0

async function runSearch() {
  const q = query.value.trim()
  if (q.length < 2) {
    results.value = { students: [], tutors: [], parents: [] }
    error.value = null
    loading.value = false
    activeIndex.value = -1
    return
  }

  const seq = ++requestSeq
  loading.value = true
  error.value = null
  try {
    const { data } = await adminApi.globalSearch(q)
    if (seq !== requestSeq) return
    results.value = data
    activeIndex.value = -1
  } catch (e) {
    if (seq !== requestSeq) return
    error.value = e.message || 'Search failed. Please try again.'
    results.value = { students: [], tutors: [], parents: [] }
  } finally {
    if (seq === requestSeq) loading.value = false
  }
}

watch(query, () => {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(runSearch, 250)
})

watch(
  () => props.open,
  async (isOpen) => {
    if (isOpen) {
      query.value = ''
      results.value = { students: [], tutors: [], parents: [] }
      error.value = null
      activeIndex.value = -1
      await nextTick()
      inputRef.value?.focus()
    }
  }
)

function close() {
  emit('close')
}

function goToResult(item) {
  router.push({ name: item.group.routeName, query: { q: item.name } })
  close()
}

function onKeydown(e) {
  if (e.key === 'Escape') {
    close()
    return
  }
  if (!hasResults.value) return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    activeIndex.value = (activeIndex.value + 1) % flatResults.value.length
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    activeIndex.value = (activeIndex.value - 1 + flatResults.value.length) % flatResults.value.length
  } else if (e.key === 'Enter') {
    e.preventDefault()
    const target = flatResults.value[activeIndex.value] ?? flatResults.value[0]
    if (target) goToResult(target)
  }
}

function statusClasses(status) {
  if (status === 'Active') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300'
  if (status === 'Blocked') return 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300'
  if (status === 'Pending') return 'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300'
  return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
}

function isActive(item) {
  const idx = flatResults.value.findIndex(
    (r) => r.group.key === item.group.key && r.id === item.id
  )
  return idx === activeIndex.value
}
</script>

<template>
  <transition name="fade">
    <div
      v-if="open"
      class="fixed inset-0 z-[100] flex items-start justify-center px-4 pt-20 sm:pt-28"
      @keydown="onKeydown"
    >
      <!-- Backdrop -->
      <div
        class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
        @click="close"
      ></div>

      <!-- Panel -->
      <div
        class="relative z-10 w-full max-w-xl overflow-hidden rounded-2xl bg-white dark:bg-slate-900 shadow-soft-lg"
      >
        <!-- Search Input -->
        <div class="flex items-center gap-3 border-b border-slate-100 dark:border-slate-800 px-5 py-4">
          <MagnifyingGlassIcon class="h-5 w-5 shrink-0 text-slate-400" />
          <input
            ref="inputRef"
            v-model="query"
            type="text"
            placeholder="Search students, tutors, or parents by name or email…"
            class="w-full bg-transparent text-sm text-slate-800 placeholder:text-slate-400 outline-none dark:text-slate-100"
          />
          <button
            class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
            @click="close"
            aria-label="Close search"
          >
            <XMarkIcon class="h-4 w-4" />
          </button>
        </div>

        <!-- Results -->
        <div class="max-h-96 overflow-y-auto p-2">
          <!-- Prompt -->
          <div
            v-if="!hasQuery"
            class="px-4 py-10 text-center text-sm text-slate-400"
          >
            Type at least 2 characters to search across every user record on the platform.
          </div>

          <!-- Loading -->
          <div
            v-else-if="loading"
            class="space-y-2 p-2"
          >
            <div
              v-for="n in 3"
              :key="n"
              class="h-12 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800"
            />
          </div>

          <!-- Error -->
          <div
            v-else-if="error"
            class="px-4 py-10 text-center text-sm text-rose-500"
          >
            {{ error }}
          </div>

          <!-- No matches -->
          <div
            v-else-if="!hasResults"
            class="px-4 py-10 text-center text-sm text-slate-400"
          >
            No matches for “{{ query }}”.
          </div>

          <!-- Grouped matches -->
          <template v-else>
            <div
              v-for="group in GROUPS"
              :key="group.key"
            >
              <div
                v-if="results[group.key]?.length"
                class="mb-1 mt-2 px-3 text-xs font-semibold uppercase tracking-wider text-slate-400 first:mt-0"
              >
                {{ group.label }}
              </div>

              <button
                v-for="item in results[group.key]"
                :key="`${group.key}-${item.id}`"
                type="button"
                class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left transition-colors"
                :class="isActive({ ...item, group })
                  ? 'bg-sky-50 dark:bg-sky-900/20'
                  : 'hover:bg-slate-50 dark:hover:bg-slate-800/60'"
                @click="goToResult({ ...item, group })"
                @mouseenter="activeIndex = flatResults.findIndex((r) => r.group.key === group.key && r.id === item.id)"
              >
                <span
                  class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full"
                  :class="group.accent"
                >
                  <component :is="group.icon" class="h-4.5 w-4.5" />
                </span>

                <span class="min-w-0 flex-1">
                  <span class="block truncate text-sm font-medium text-slate-800 dark:text-slate-100">
                    {{ item.name }}
                  </span>
                  <span class="block truncate text-xs text-slate-500 dark:text-slate-400">
                    {{ item.email }}
                  </span>
                </span>

                <span
                  class="shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold"
                  :class="statusClasses(item.status)"
                >
                  {{ item.status }}
                </span>
              </button>
            </div>
          </template>
        </div>

        <!-- Footer hint -->
        <div class="flex items-center justify-between border-t border-slate-100 dark:border-slate-800 px-5 py-2.5 text-[11px] text-slate-400">
          <span>↑↓ to navigate · Enter to select · Esc to close</span>
          <span>Ctrl/Cmd + K</span>
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
