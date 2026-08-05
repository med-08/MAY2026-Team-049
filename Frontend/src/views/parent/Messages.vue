<script setup>
import { ChatBubbleLeftRightIcon } from '@heroicons/vue/24/outline'
import EmptyState from '../../components/ui/EmptyState.vue'
</script>

<template>
  <div class="space-y-6">
    <div class="card p-5">
      <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4 flex items-center gap-2">
        <ChatBubbleLeftRightIcon class="w-5 h-5 text-brand-green-500" />
        Messages with Tutor
      </h3>

      <EmptyState
        title="Messages API not connected yet"
        message="This page was using mock data before. Add backend message routes to make this page fully live."
      />
    </div>
  </div>
</template>