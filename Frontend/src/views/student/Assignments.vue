<script setup>
import PageHeader from "../../components/student/PageHeader.vue"
import StatusBadge from "../../components/student/StatusBadge.vue"
import ProgressBar from "../../components/student/ProgressBar.vue"
import {
  CalendarIcon,
  ClockIcon,
  SparklesIcon,
} from "@heroicons/vue/24/outline"

import { assignments } from "../../data/studentMockData"
</script>

<template>
  <div>
    <PageHeader
      title="Interactive Assignments"
      subtitle="Complete engaging assignments and receive personalized learning support as you progress."
    />

    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5">
      <div
        v-for="a in assignments"
        :key="a.id"
        class="card card-hover p-5 flex flex-col"
      >
        <!-- Title -->
        <div class="flex items-start justify-between mb-2">
          <h4 class="font-display font-bold text-lg leading-snug">
            {{ a.title }}
          </h4>
        </div>

        <!-- Subject -->
        <p class="text-sm font-semibold text-brand-blue mb-2">
          {{ a.subject }}
        </p>

        <!-- Description -->
        <p class="text-sm text-ink-soft dark:text-slate-300 mb-4">
          {{ a.description }}
        </p>

        <!-- Status -->
        <div class="flex flex-wrap gap-2 mb-4">
          <StatusBadge :status="a.status" />
        </div>

        <!-- Info -->
        <div
          class="space-y-2 text-xs text-ink-soft dark:text-slate-400 mb-4"
        >
          <p class="flex items-center gap-2">
            <CalendarIcon class="w-4 h-4" />
            Due: {{ a.dueDate }}
          </p>

          <p class="flex items-center gap-2">
            <ClockIcon class="w-4 h-4" />
            Estimated Time: {{ a.estimatedTime }}
          </p>

          <p
            class="flex items-center gap-2 text-brand-blue font-medium"
            v-if="a.aiEnabled"
          >
            <SparklesIcon class="w-4 h-4" />
            AI Personalized
          </p>
        </div>

        <!-- Progress -->
        <div class="mb-5">
          <div
            class="flex justify-between text-xs text-ink-soft dark:text-slate-400 mb-1"
          >
            <span>Progress</span>
            <span>{{ a.progress }}%</span>
          </div>

          <ProgressBar :value="a.progress" />
        </div>

        <!-- AI Note -->
        <div
          v-if="a.aiEnabled"
          class="rounded-xl bg-brand-blue/10 dark:bg-brand-blue/15 p-3 text-xs text-brand-blue mb-5"
        >
          Questions may adapt based on your learning progress.
        </div>

        <!-- Button -->
        <button
          class="mt-auto w-full py-2.5 rounded-xl font-semibold text-sm transition"
          :class="
            a.status === 'Completed'
              ? 'border border-slate-200 dark:border-border-dark text-ink-soft dark:text-slate-400 cursor-default'
              : 'bg-violet-100 text-violet-700 hover:bg-violet-200 dark:bg-violet-500/15 dark:text-violet-300 dark:hover:bg-violet-500/25'
          "
          :disabled="a.status === 'Completed'"
        >
          {{
            a.status === "Not Started"
              ? "Start Assignment"
              : a.status === "In Progress"
              ? "Continue Assignment"
              : "Completed"
          }}
        </button>
      </div>
    </div>
  </div>
</template>