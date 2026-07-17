<script setup>
import {
  UserGroupIcon,
  AcademicCapIcon,
  HomeIcon,
  NoSymbolIcon,
  ClipboardDocumentCheckIcon,
  BookOpenIcon
} from '@heroicons/vue/24/outline'

import StatCard from '../../components/ui/StatCard.vue'
import {
  students,
  tutors,
  parents,
  pendingApprovals,
  subjects
} from '../../data/mockData'

const stats = [
  {
    title: 'Total Students',
    value: students.length,
    subtitle: 'Registered students',
    color: 'emerald',
    icon: UserGroupIcon
  },
  {
    title: 'Total Tutors',
    value: tutors.length,
    subtitle: 'Active tutors',
    color: 'blue',
    icon: AcademicCapIcon
  },
  {
    title: 'Total Parents',
    value: parents.length,
    subtitle: 'Registered parents',
    color: 'purple',
    icon: HomeIcon
  },
  {
    title: 'Blocked Students',
    value: students.filter((s) => s.status === 'Blocked').length,
    subtitle: 'Currently blocked',
    color: 'red',
    icon: NoSymbolIcon
  },
  {
    title: 'Pending Approvals',
    value: pendingApprovals.filter((p) => p.status === 'Pending').length,
    subtitle: 'Awaiting approval',
    color: 'amber',
    icon: ClipboardDocumentCheckIcon
  },
  {
    title: 'Subjects',
    value: subjects.length,
    subtitle: 'Available subjects',
    color: 'teal',
    icon: BookOpenIcon
  }
]
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

    <!-- Dashboard Cards -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
      <StatCard
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