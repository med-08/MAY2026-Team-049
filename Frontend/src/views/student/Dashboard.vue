<script setup>
import { ref, onMounted, onUnmounted } from "vue"
import PageHeader from "../../components/student/PageHeader.vue"
import StatCard from "../../components/student/StudentStatCard.vue"
import LineChart from "../../components/student/LineChart.vue"
import BarChart from "../../components/student/BarChart.vue"
import NextSessionCard from "../../components/student/NextSessionCard.vue"
import StatusBadge from "../../components/student/StatusBadge.vue"
import { CheckCircleIcon } from "@heroicons/vue/24/outline"
import { studentApi } from "../../services/studentApi"

const student = ref(null)
const summaryStats = ref([])
const weeklyQuizProgress = ref({ labels: [], data: [] })
const subjectQuizScores = ref({ labels: [], data: [] })
const nextSession = ref({})
const todaysTasks = ref([])
const meetings = ref([])

const loading = ref(true)
const error = ref("")
let refreshTimer = null

async function loadDashboard() {
  try {
    const res = await studentApi.getDashboard()

    if (res.success && res.data) {
      const d = res.data
      student.value = d.student || null
      summaryStats.value = d.summaryStats || []
      weeklyQuizProgress.value = d.weeklyQuizProgress || { labels: [], data: [] }
      subjectQuizScores.value = d.subjectQuizScores || { labels: [], data: [] }
      nextSession.value = d.nextSession || {}
      todaysTasks.value = d.todaysTasks || []
      meetings.value = d.meetings || []
      error.value = ""
    } else {
      error.value = res.message || "Failed to load dashboard data"
    }
  } catch (err) {
    console.error("Dashboard fetch error:", err)
    error.value = err?.message || "Failed to load dashboard data"
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadDashboard()
  refreshTimer = window.setInterval(() => loadDashboard(), 15000)
})

onUnmounted(() => {
  if (refreshTimer) window.clearInterval(refreshTimer)
})
</script>

<template>
  <div>
    <PageHeader
      title="Dashboard"
      subtitle="Here's a quick look at your progress this week."
    />

    <div v-if="loading" class="flex justify-center items-center py-20">
      <p class="text-slate-500">Loading dashboard...</p>
    </div>

    <div v-else-if="error" class="text-center py-10 text-red-500">
      {{ error }}
    </div>

    <div v-else>
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard v-for="s in summaryStats" :key="s.key" v-bind="s" />
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-6">
        <div class="card p-5">
          <h3 class="font-display font-bold mb-1">Weekly Quiz Progress</h3>
          <p class="text-xs text-ink-soft dark:text-slate-400 mb-3">
            Your average quiz score over the last 6 weeks
          </p>
          <LineChart :labels="weeklyQuizProgress.labels" :data="weeklyQuizProgress.data" />
        </div>

        <div class="card p-5">
          <h3 class="font-display font-bold mb-1">Subject-wise Quiz Scores</h3>
          <p class="text-xs text-ink-soft dark:text-slate-400 mb-3">
            Latest quiz performance by subject
          </p>
          <BarChart :labels="subjectQuizScores.labels" :data="subjectQuizScores.data" />
        </div>
      </div>

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
            <p class="text-sm text-ink-soft dark:text-slate-400">
              No tasks scheduled for today.
            </p>
          </div>
        </div>
      </div>

      <div v-if="meetings.length" class="card p-5 mt-6">
        <h3 class="font-display font-bold mb-3">Upcoming Meetings</h3>
        <div v-for="m in meetings" :key="m.id" class="flex items-center justify-between gap-3 py-2 border-b last:border-0 border-slate-100 dark:border-slate-700">
          <div><p class="text-sm font-semibold">{{ m.tutor }}</p><p class="text-xs text-slate-500">{{ new Date(m.date).toLocaleString() }} · {{ m.reason || 'Meeting' }}</p></div>
          <span v-if="m.meeting_lifecycle === 'Awaiting Tutor Approval'" class="text-xs font-semibold text-indigo-600">Awaiting Tutor Approval</span><span v-else-if="m.meeting_lifecycle === 'Meeting Not Started'" class="text-xs font-semibold text-slate-400">Meeting Not Started</span><a v-else-if="m.can_join && m.link" :href="m.link" target="_blank" class="btn grad sm">Join</a><span v-else class="text-xs font-semibold text-slate-400">{{ m.meeting_lifecycle || 'Meeting Ended' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>