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
        title: 'Blocked Students',
        value: data.blocked_students,
        subtitle: 'Currently blocked',
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
    error.value = e.message || 'Failed to load dashboard statistics.'
  } finally {
    loading.value = false
  }
}

onMounted(loadStats)
</script>

<template>
  <div class="space-y-8">
    <!-- Header -->
    <div>
      <h2
        class="text-2xl font-display font-bold text-slate-800 dark:text-slate-100"
      >
        Overview
      </h2>

      <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
        A snapshot of everything happening on LearnAtHome today.
      </p>
    </div>

    <EmptyState
      v-if="error"
      title="Couldn't load the dashboard"
      :message="error"
    />

    <!-- Dashboard Cards -->
    <div
      v-else
      class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3"
    >
      <template v-if="loading">
        <div
          v-for="n in 6"
          :key="n"
          class="card h-28 animate-pulse"
        />
      </template>

      <StatCard
        v-else
        v-for="card in stats"
        :key="card.title"
        :title="card.title"
        :value="card.value"
        :subtitle="card.subtitle"
        :color="card.color"
        :icon="card.icon"
      />
    </div>
  </div>
</template>