<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Bars3Icon, MagnifyingGlassIcon, SunIcon, MoonIcon } from '@heroicons/vue/24/outline'
import { useTheme } from '../../composables/useTheme'

const emit = defineEmits(['open-sidebar', 'open-search'])
const route = useRoute()
const { isDark, toggleTheme } = useTheme()

const pageTitle = computed(() => route.meta?.title || 'Dashboard')
</script>

<template>
  <header class="sticky top-0 z-30 bg-white/80 dark:bg-slate-900/70 backdrop-blur-md border-b border-slate-100 dark:border-slate-800">
    <div class="flex items-center justify-between gap-4 px-4 sm:px-6 h-16">
      <div class="flex items-center gap-3 min-w-0">
        <button class="lg:hidden text-slate-500 dark:text-slate-400" @click="emit('open-sidebar')">
          <Bars3Icon class="w-6 h-6" />
        </button>
        <div class="min-w-0">
          <h1 class="font-display font-bold text-slate-800 dark:text-slate-100 leading-tight truncate">
            Welcome, Admin 🎯
          </h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">Simplify. Manage. Grow.</p>
        </div>
      </div>

      <div class="relative flex-1 max-w-md hidden md:flex items-center gap-2">
        <button
          type="button"
          class="flex w-full items-center gap-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 px-3.5 h-10 text-sm text-slate-400 dark:text-slate-500 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
          title="Search all students, tutors & parents (Ctrl/Cmd + K)"
          @click="emit('open-search')"
        >
          <MagnifyingGlassIcon class="w-4 h-4 shrink-0" />
          <span class="flex-1 text-left">Search students, tutors, parents…</span>
          <kbd class="hidden lg:inline rounded border border-slate-200 dark:border-slate-600 bg-slate-50 dark:bg-slate-900 px-1.5 py-0.5 text-[10px] font-semibold shrink-0">⌘K</kbd>
        </button>
      </div>

      <button
        type="button"
        class="md:hidden w-9 h-9 rounded-lg flex items-center justify-center bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
        title="Search all students, tutors & parents"
        @click="emit('open-search')"
      >
        <MagnifyingGlassIcon class="w-5 h-5" />
      </button>

      <div class="flex items-center gap-3 shrink-0">
        <button
          class="w-9 h-9 rounded-lg flex items-center justify-center bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          @click="toggleTheme"
          aria-label="Toggle dark mode"
        >
          <SunIcon v-if="isDark" class="w-5 h-5" />
          <MoonIcon v-else class="w-5 h-5" />
        </button>
        <router-link to="/admin/profile" class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-full bg-gradient-to-br from-brand-green-500 via-brand-blue-500 to-brand-purple-500 flex items-center justify-center text-white text-sm font-semibold shadow-soft">
            A
          </div>
          <span class="text-sm font-semibold text-slate-700 dark:text-slate-200 hidden sm:inline">Admin</span>
        </router-link>
      </div>
    </div>
  </header>
</template>
