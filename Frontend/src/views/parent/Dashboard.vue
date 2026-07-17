<script setup>
import { computed, ref } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Filler
} from 'chart.js'
import {
  CheckBadgeIcon,
  ChartBarIcon,
  CalendarDaysIcon,
  BellAlertIcon,
  VideoCameraIcon,
  ArrowRightIcon,
  BookOpenIcon,
  LightBulbIcon
} from '@heroicons/vue/24/outline'

import StatCard from '../../components/ui/StatCard.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import { useToast } from '../../composables/useToast'
import { useParentPortal } from '../../composables/useParentPortal'

ChartJS.register(LineElement, PointElement, CategoryScale, LinearScale, Tooltip, Filler)

const { showToast } = useToast()

// parent_id 1 stands in for the logged-in parent's session.
const {
  parent,
  children,
  upcomingSession,
  completedSessions,
  assignmentsFor,
  quizTrend,
  latestWeeklySummary
} = useParentPortal(1)

const selectedChildId = ref(children.value[0]?.student_id)
const selectedChild = computed(() => children.value.find((c) => c.student_id === selectedChildId.value))

const session = computed(() => upcomingSession(selectedChildId.value))
const sessionHistory = computed(() => completedSessions(selectedChildId.value))
const assignmentList = computed(() => assignmentsFor(selectedChildId.value))
const scores = computed(() => quizTrend(selectedChildId.value))
const summary = computed(() => latestWeeklySummary(selectedChildId.value))

const completedCount = computed(
  () => sessionHistory.value.filter((s) => s.progress?.session_completion_status === 'Completed').length
)
const avgScore = computed(() => {
  if (!scores.value.length) return 0
  return Math.round(scores.value.reduce((sum, s) => sum + s.score, 0) / scores.value.length)
})
const latestScore = computed(() => scores.value[scores.value.length - 1]?.score ?? 0)
const needsPracticeCount = computed(
  () => sessionHistory.value.filter((s) => s.progress?.learning_pace === 'Needs Practice').length
)
const pendingAssignments = computed(
  () => assignmentList.value.filter((a) => !a.submission || a.submission.status === 'Pending').length
)

const stats = computed(() => [
  {
    title: 'Sessions Completed',
    value: completedCount.value,
    subtitle: `${sessionHistory.value.length} sessions on record`,
    color: 'emerald',
    icon: CheckBadgeIcon
  },
  {
    title: 'Average Quiz Score',
    value: `${avgScore.value}%`,
    subtitle: `Latest quiz: ${latestScore.value}%`,
    color: 'blue',
    icon: ChartBarIcon
  },
  {
    title: 'Upcoming Session',
    value: session.value ? formatDate(session.value.session_date, true) : '\u2014',
    subtitle: session.value ? `${session.value.subjectName} \u00b7 ${session.value.start_time}` : 'None scheduled',
    color: 'purple',
    icon: CalendarDaysIcon
  },
  {
    title: 'Needs Attention',
    value: needsPracticeCount.value,
    subtitle: `${pendingAssignments.value} assignment(s) pending`,
    color: 'amber',
    icon: BellAlertIcon
  }
])

const chartData = computed(() => ({
  labels: scores.value.map((s) => s.week),
  datasets: [
    {
      label: 'Quiz Score (%)',
      data: scores.value.map((s) => s.score),
      borderColor: '#3b82f6',
      backgroundColor: (ctx) => {
        const { chart } = ctx
        const { ctx: c, chartArea } = chart
        if (!chartArea) return 'rgba(59,130,246,0)'
        const gradient = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom)
        gradient.addColorStop(0, 'rgba(59,130,246,0.28)')
        gradient.addColorStop(1, 'rgba(59,130,246,0)')
        return gradient
      },
      tension: 0.4,
      fill: true,
      pointBackgroundColor: '#3b82f6',
      pointBorderColor: '#fff',
      pointBorderWidth: 2,
      pointRadius: 4
    }
  ]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false } },
    y: { beginAtZero: true, max: 100, grid: { color: 'rgba(148,163,184,0.15)' } }
  }
}

function formatDate(dateStr, short = false) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', short
    ? { month: 'short', day: 'numeric' }
    : { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
}
</script>

<template>
  <div v-if="selectedChild" class="space-y-6">
    <!-- Child switcher -->
    <div v-if="children.length > 1" class="flex items-center gap-2">
      <button
        v-for="child in children"
        :key="child.student_id"
        class="pill-filter"
        :class="selectedChildId === child.student_id
          ? 'bg-gradient-to-r from-brand-green-500 to-brand-blue-500 text-white border-transparent'
          : 'text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800'"
        @click="selectedChildId = child.student_id"
      >
        {{ child.student_name }}
      </button>
    </div>

    <!-- Stat cards -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard v-for="card in stats" :key="card.title" v-bind="card" />
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <!-- Quiz score trend -->
        <div class="card p-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100">
              Weekly Quiz Performance — {{ selectedChild.student_name }}
            </h3>
            <router-link to="/parent/progress" class="text-xs font-semibold text-brand-blue-600 dark:text-brand-blue-400 hover:underline flex items-center gap-1">
              View details <ArrowRightIcon class="w-3.5 h-3.5" />
            </router-link>
          </div>
          <div class="h-64">
            <Line v-if="scores.length" :data="chartData" :options="chartOptions" />
            <EmptyState v-else title="No quiz attempts yet" message="Scores will show up here after the first weekly quiz." />
          </div>
        </div>

        <!-- Weekly summary -->
        <div class="card p-5" v-if="summary">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100">Latest Weekly Summary</h3>
            <span class="text-xs font-medium text-slate-400">{{ formatDate(summary.week_start, true) }} – {{ formatDate(summary.week_end, true) }}</span>
          </div>
          <div class="grid sm:grid-cols-3 gap-4 text-sm">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Topics Taught</p>
              <p class="text-slate-700 dark:text-slate-300">{{ summary.topics_taught }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Homework</p>
              <p class="text-slate-700 dark:text-slate-300">{{ summary.homework_summary }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Areas for Improvement</p>
              <p class="text-slate-700 dark:text-slate-300">{{ summary.areas_for_improvement }}</p>
            </div>
          </div>
        </div>

        <!-- Latest tips + resources -->
        <div class="card p-5" v-if="sessionHistory[0]">
          <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4 flex items-center gap-2">
            <LightBulbIcon class="w-5 h-5 text-amber-500" />
            Latest Study Tips & Resources
          </h3>
          <div v-if="sessionHistory[0].tips.length" class="space-y-2 mb-4">
            <p v-for="tip in sessionHistory[0].tips" :key="tip.tip_id" class="text-sm text-slate-600 dark:text-slate-300 bg-amber-50 dark:bg-amber-500/10 rounded-lg p-3">
              {{ tip.tip_text }}
            </p>
          </div>
          <div v-if="sessionHistory[0].resources.length" class="space-y-2">
            <a
              v-for="r in sessionHistory[0].resources"
              :key="r.resource_id"
              :href="r.resource_link"
              target="_blank"
              rel="noopener"
              class="flex items-center justify-between text-sm p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <span class="flex items-center gap-2 text-slate-700 dark:text-slate-300 font-medium truncate">
                <BookOpenIcon class="w-4 h-4 shrink-0 text-brand-blue-500" />
                {{ r.resource_title }}
              </span>
              <span class="text-xs text-slate-400 shrink-0 ml-2">{{ r.resource_type }}</span>
            </a>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <!-- Upcoming session -->
        <div class="card p-5" v-if="session">
          <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">Upcoming Session</h3>
          <div class="rounded-xl bg-grad-blue dark:bg-slate-800/60 p-4">
            <p class="text-xs font-semibold uppercase tracking-wider text-brand-blue-700 dark:text-brand-blue-400">{{ session.session_type }}</p>
            <p class="mt-1 font-display font-bold text-slate-800 dark:text-slate-100">{{ session.subjectName }}</p>
            <p class="text-sm text-slate-600 dark:text-slate-300 mt-1">with {{ session.tutorName }}</p>
            <p class="text-sm text-slate-500 dark:text-slate-400 mt-2">{{ formatDate(session.session_date) }}</p>
            <p class="text-sm text-slate-500 dark:text-slate-400">{{ session.start_time }} – {{ session.end_time }}</p>
            <button class="btn-primary mt-4 w-full justify-center" @click="showToast('Joining session...')">
              <VideoCameraIcon class="w-4 h-4" />
              Join Session
            </button>
          </div>
        </div>
        <EmptyState v-else title="No upcoming sessions" message="Nothing booked yet for this child." />

        <!-- Quick links -->
        <div class="card p-5">
          <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">Quick Links</h3>
          <div class="space-y-2">
            <router-link to="/parent/curriculum" class="flex items-center justify-between text-sm p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
              <span class="font-medium text-slate-700 dark:text-slate-300">Monthly Curriculum Plan</span>
              <ArrowRightIcon class="w-4 h-4 text-slate-400" />
            </router-link>
            <router-link to="/parent/schedule" class="flex items-center justify-between text-sm p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
              <span class="font-medium text-slate-700 dark:text-slate-300">Full Schedule</span>
              <ArrowRightIcon class="w-4 h-4 text-slate-400" />
            </router-link>
            <router-link to="/parent/messages" class="flex items-center justify-between text-sm p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
              <span class="font-medium text-slate-700 dark:text-slate-300">Message Tutor</span>
              <ArrowRightIcon class="w-4 h-4 text-slate-400" />
            </router-link>
            <router-link to="/parent/meetings" class="flex items-center justify-between text-sm p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
              <span class="font-medium text-slate-700 dark:text-slate-300">Meeting Requests</span>
              <ArrowRightIcon class="w-4 h-4 text-slate-400" />
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
