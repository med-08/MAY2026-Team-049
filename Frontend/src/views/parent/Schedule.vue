<script setup>
import { ClockIcon } from '@heroicons/vue/24/outline'
import EmptyState from '../../components/ui/EmptyState.vue'
</script>

<template>
  <div class="space-y-6">
    <div class="card p-5">
      <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4 flex items-center gap-2">
        <ClockIcon class="w-5 h-5 text-brand-blue-500" />
        Schedule
      </h3>

      <EmptyState
        title="Schedule API not connected yet"
        message="This page was using mock data before. Add backend session/schedule routes to make this page fully live."
      />
    </div>
  </div>
</template>