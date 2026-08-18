<script setup>
import { ref, onMounted } from 'vue'
import {
  UserGroupIcon,
  AcademicCapIcon,
  HomeIcon,
  NoSymbolIcon,
  ClipboardDocumentCheckIcon,
  BookOpenIcon
} from '@heroicons/vue/24/outline'

import StatCard from '../../components/ui/StatCard.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import { adminApi } from '../../services/adminApi'

const loading = ref(true)
const error = ref(null)
const stats = ref([])

async function loadStats() {
  loading.value = true
  error.value = null

  try {
    const { data } = await adminApi.getStats()

    stats.value = [
      {
        title: 'Total Students',
        value: data.total_students,
        subtitle: 'Registered students',
        color: 'emerald',
        icon: UserGroupIcon
      },
      {
        title: 'Total Tutors',
        value: data.total_tutors,
        subtitle: 'Active tutors',
        color: 'blue',
        icon: AcademicCapIcon
      },
      {
        title: 'Total Parents',
        value: data.total_parents,
        subtitle: 'Registered parents',
        color: 'purple',
        icon: HomeIcon
      },
      {
        title: 'Blocked Users',
        value: data.blocked_users,
        subtitle: 'Students, tutors & parents',
        color: 'red',
        icon: NoSymbolIcon
      },
      {
        title: 'Pending Approvals',
        value: data.pending_approvals,
        subtitle: 'Awaiting approval',
        color: 'amber',
        icon: ClipboardDocumentCheckIcon
      },
      {
        title: 'Subjects',
        value: data.total_subjects,
        subtitle: 'Available subjects',
        color: 'teal',
        icon: BookOpenIcon
      }
    ]
  } catch (e) {
    error.value =
      e.message || 'Failed to load dashboard statistics.'
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<template>
  <div class="space-y-8">

    <!-- Header -->
    <div
      class="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between"
    >
      <div>
        <p
          class="mb-1 text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400"
        >
          Admin Dashboard
        </p>

        <h2
          class="text-2xl font-display font-bold tracking-tight text-slate-800 dark:text-slate-100 sm:text-3xl"
        >
          Overview
        </h2>

        <p class="mt-1.5 max-w-2xl text-sm leading-6 text-slate-500 dark:text-slate-400">
          A snapshot of everything happening on LearnAtHome today.
        </p>
      </div>
    </div>

    <!-- Error State -->
    <EmptyState
      v-if="error"
      title="Couldn't load the dashboard"
      :message="error"
    />

    <!-- Dashboard -->
    <div v-else>

      <!-- Stats Grid -->
      <div
        class="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3"
      >

        <!-- Loading Skeleton -->
        <template v-if="loading">
          <div
            v-for="n in 6"
            :key="n"
            class="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800"
          >
            <div class="flex items-start justify-between">
              <div
                class="h-11 w-11 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-700"
              />

              <div
                class="h-4 w-16 animate-pulse rounded bg-slate-200 dark:bg-slate-700"
              />
            </div>

            <div
              class="mt-5 h-8 w-24 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700"
            />

            <div
              class="mt-3 h-4 w-36 animate-pulse rounded bg-slate-200 dark:bg-slate-700"
            />
          </div>
        </template>

        <!-- Stat Cards -->
        <template v-else>
          <div
            v-for="card in stats"
            :key="card.title"
            class="transition duration-200 hover:-translate-y-0.5"
          >
            <StatCard
              :title="card.title"
              :value="card.value"
              :subtitle="card.subtitle"
              :color="card.color"
              :icon="card.icon"
            />
          </div>
        </template>

      </div>

    </div>
  </div>
</template>