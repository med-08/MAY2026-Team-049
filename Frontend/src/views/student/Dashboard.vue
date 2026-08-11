<script setup>
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"
import PageHeader from "../../components/student/PageHeader.vue"
import StatCard from "../../components/student/StudentStatCard.vue"
import LineChart from "../../components/student/LineChart.vue"
import NextSessionCard from "../../components/student/NextSessionCard.vue"
import StatusBadge from "../../components/student/StatusBadge.vue"
import { CheckCircleIcon, ExclamationTriangleIcon } from "@heroicons/vue/24/outline"
import { studentApi } from "../../services/studentApi"

const router = useRouter()
const student = ref(null)
const summaryStats = ref([])
const weeklyQuizProgress = ref({ labels: [], data: [] })
const topicPerformance = ref({
  "Quadratic Equations": 85,
  "Factorisation": 58,
  "Trigonometry": 91,
  "Polynomials": 76
})
const weakTopicAlert = ref({
  topic: "Factorisation",
  score: 58,
  message: "Your performance in Factorisation is low (58%). Try the recommended 5-question practice quiz."
})
const nextSession = ref({})
const todaysTasks = ref([])

const loading = ref(true)
const error = ref("")

onMounted(async () => {
  try {
    const res = await studentApi.getDashboard()

    if (res.success && res.data) {
      const d = res.data
      student.value = d.student || null
      summaryStats.value = d.summaryStats || []
      weeklyQuizProgress.value = d.weeklyQuizProgress || { labels: ["W1", "W2", "W3", "W4", "W5", "W6"], data: [75, 80, 85, 78, 88, 82] }
      if (d.topicPerformance) topicPerformance.value = d.topicPerformance
      if (d.weakTopicAlert) weakTopicAlert.value = d.weakTopicAlert
      nextSession.value = d.nextSession || {}
      todaysTasks.value = d.todaysTasks || []
      error.value = ""
    } else {
      error.value = "Failed to load dashboard data"
    }
  } catch (err) {
    console.error("Dashboard fetch error:", err)
  } finally {
    loading.value = false
  }
})

function startPractice() {
  router.push({ name: 'student-quiz-attempt', params: { quizId: 1 } })
}
</script>

<template>
  <div>
    <PageHeader
      :title="`Welcome back, ${student?.name || 'Student'} 👋`"
      subtitle="Here's a quick look at your connected learning workflow and progress."
    />

    <div v-if="loading" class="flex justify-center items-center py-20">
      <p class="text-slate-500">Loading dashboard...</p>
    </div>

    <div v-else-if="error" class="text-center py-10 text-red-500">
      {{ error }}
    </div>

    <div v-else>
      <!-- Weak Topic Alert Banner -->
      <div v-if="weakTopicAlert" class="mb-6 p-4 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <div class="p-2.5 rounded-xl bg-amber-500/20 text-amber-500">
            <ExclamationTriangleIcon class="w-6 h-6" />
          </div>
          <div>
            <h4 class="font-bold text-sm text-amber-600 dark:text-amber-400">
              ⚠ Weak Area Detected: {{ weakTopicAlert.topic }} ({{ weakTopicAlert.score }}%)
            </h4>
            <p class="text-xs text-ink-soft dark:text-slate-300 mt-0.5">
              {{ weakTopicAlert.message }}
            </p>
          </div>
        </div>
        <button
          class="btn-primary text-xs px-4 py-2 bg-gradient-to-r from-brand-purple to-brand-blue text-white rounded-xl font-bold shadow-md hover:opacity-90 transition-all shrink-0"
          @click="startPractice"
        >
          ⚡ Start Recommended Practice
        </button>
      </div>

      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard v-for="s in summaryStats" :key="s.key" v-bind="s" />
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-6">
        <!-- Weekly Quiz Progress -->
        <div class="card p-5">
          <h3 class="font-display font-bold mb-1">Weekly Quiz Score Trend</h3>
          <p class="text-xs text-ink-soft dark:text-slate-400 mb-3">
            Your average score over the last 6 weeks
          </p>
          <LineChart :labels="weeklyQuizProgress.labels" :data="weeklyQuizProgress.data" />
        </div>

        <!-- Topic Performance Breakdown -->
        <div class="card p-5">
          <h3 class="font-display font-bold mb-1">Topic Performance Breakdown</h3>
          <p class="text-xs text-ink-soft dark:text-slate-400 mb-4">
            AI evaluated accuracy per chapter
          </p>
          <div class="space-y-3.5">
            <div v-for="(score, topic) in topicPerformance" :key="topic">
              <div class="flex justify-between text-xs font-semibold mb-1">
                <span class="flex items-center gap-1.5">
                  {{ topic }}
                  <span v-if="score < 65" class="text-xs text-amber-500 font-bold">⚠ Weak</span>
                </span>
                <span :class="score < 65 ? 'text-amber-500 font-bold' : 'text-emerald-500 font-bold'">{{ score }}%</span>
              </div>
              <div class="w-full bg-slate-100 dark:bg-white/10 h-2.5 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="score < 65 ? 'bg-amber-500' : score > 85 ? 'bg-emerald-500' : 'bg-brand-blue'"
                  :style="{ width: `${score}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-5 mt-6">
        <NextSessionCard :session="nextSession" />

        <div class="card p-5">
          <h3 class="font-display font-bold mb-4">Today's Learning Tasks</h3>

          <div v-if="todaysTasks.length" class="space-y-3">
            <div
              v-for="task in todaysTasks"
              :key="task.id"
              class="flex items-start justify-between gap-3 p-3.5 rounded-xl bg-slate-50 dark:bg-white/5 border border-slate-100 dark:border-white/5"
            >
              <div class="min-w-0">
                <p class="text-xs font-semibold text-brand-purple">{{ task.subject }}</p>
                <p class="text-sm font-semibold mt-0.5 truncate">{{ task.task }}</p>
                <p class="text-xs text-ink-soft dark:text-slate-400 mt-0.5">{{ task.time }}</p>
              </div>
              <button
                v-if="task.type === 'quiz'"
                class="px-3 py-1.5 text-xs font-bold text-white bg-brand-blue rounded-lg hover:opacity-90 transition-all"
                @click="startPractice"
              >
                Start Quiz
              </button>
              <StatusBadge v-else :status="task.status" />
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
    </div>
  </div>
</template>