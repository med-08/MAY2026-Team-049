<script setup>
import PageHeader from "../../components/student/PageHeader.vue"
import StatCard from "../../components/student/StudentStatCard.vue"
import LineChart from "../../components/student/LineChart.vue"
import BarChart from "../../components/student/BarChart.vue"
import NextSessionCard from "../../components/student/NextSessionCard.vue"
import StatusBadge from "../../components/student/StatusBadge.vue"
import { CheckCircleIcon } from "@heroicons/vue/24/outline"
import { summaryStats, weeklyQuizProgress, subjectQuizScores, nextSession, todaysTasks, student } from "../../data/studentMockData"
</script>

<template>
  <div>
    <PageHeader title="Dashboard" subtitle="Here's a quick look at your progress this week." />

    <!-- Summary cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard v-for="s in summaryStats" :key="s.key" v-bind="s" />
    </div>

    <!-- Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-6">
      <div class="card p-5">
        <h3 class="font-display font-bold mb-1">Weekly Quiz Progress</h3>
        <p class="text-xs text-ink-soft dark:text-slate-400 mb-3">Your average quiz score over the last 6 weeks</p>
        <LineChart :labels="weeklyQuizProgress.labels" :data="weeklyQuizProgress.data" />
      </div>
      <div class="card p-5">
        <h3 class="font-display font-bold mb-1">Subject-wise Quiz Scores</h3>
        <p class="text-xs text-ink-soft dark:text-slate-400 mb-3">Latest quiz performance by subject</p>
        <BarChart :labels="subjectQuizScores.labels" :data="subjectQuizScores.data" />
      </div>
    </div>

    <!-- Next session + Today's tasks -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-6">
      <NextSessionCard :session="nextSession" />

      <div class="card p-5">
        <h3 class="font-display font-bold mb-4">Today's Tasks</h3>

        <div v-if="todaysTasks.length" class="space-y-3">
          <div
            v-for="task in todaysTasks"
            :key="task.id"
            class="flex items-start justify-between gap-3 p-3.5 rounded-xl bg-slate-50 dark:bg-white/5"
          >
            <div class="min-w-0">
              <p class="text-xs font-semibold text-brand-blue">{{ task.subject }}</p>
              <p class="text-sm font-semibold mt-0.5 truncate">{{ task.task }}</p>
              <p class="text-xs text-ink-soft dark:text-slate-400 mt-0.5">{{ task.time }}</p>
            </div>
            <StatusBadge :status="task.status" />
          </div>
        </div>

        <div v-else class="flex flex-col items-center justify-center py-10 text-center">
          <CheckCircleIcon class="w-10 h-10 text-brand-green mb-2" />
          <p class="text-sm text-ink-soft dark:text-slate-400">No tasks scheduled for today.</p>
        </div>
      </div>
    </div>
  </div>
</template>
