<script setup>
import { ref, onMounted, computed } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import { studentApi } from '../../services/studentApi'

const tips = ref([])
const insights = ref('')
const performance = ref(null)
const insightError = ref('')
const insightLoading = ref(false)
const chatMessage = ref('')
const chatLoading = ref(false)
const chatError = ref('')
const chatMessages = ref([])
const loading = ref(true)
const error = ref('')

const STATUS_STYLES = {
  'Strong': { dot: 'bg-emerald-500', text: 'text-emerald-700', bg: 'bg-emerald-50 border-emerald-200' },
  'Needs Practice': { dot: 'bg-amber-500', text: 'text-amber-700', bg: 'bg-amber-50 border-amber-200' },
  'Needs Improvement': { dot: 'bg-red-500', text: 'text-red-700', bg: 'bg-red-50 border-red-200' },
}
function statusStyle(status) {
  return STATUS_STYLES[status] || { dot: 'bg-slate-400', text: 'text-slate-600', bg: 'bg-slate-50 border-slate-200' }
}
function scoreRingClass(score) {
  if (score === null || score === undefined) return 'border-slate-200'
  if (score >= 80) return 'border-emerald-400'
  if (score >= 55) return 'border-amber-400'
  return 'border-red-400'
}

async function loadPerformanceInsights() {
  insightLoading.value = true
  insightError.value = ''
  try {
    const r = await studentApi.getPerformanceInsights()
    insights.value = r.data?.insights || ''
    performance.value = r.data?.performance || null
  } catch (e) {
    insightError.value = e.message || 'Failed to generate performance insights.'
  } finally {
    insightLoading.value = false
  }
}

async function sendChat() {
  const message = chatMessage.value.trim()
  if (!message) return
  chatMessages.value.push({ who: 'student', text: message })
  chatMessage.value = ''
  chatLoading.value = true
  chatError.value = ''
  try {
    const r = await studentApi.performanceChat(message)
    chatMessages.value.push({ who: 'ai', text: r.data?.reply || 'I need more quiz data before I can answer that.' })
  } catch (e) {
    chatError.value = e.message || 'Chat is unavailable right now.'
  } finally {
    chatLoading.value = false
  }
}

onMounted(async () => {
  try {
    const r = await studentApi.getStudyTips()
    tips.value = r.data?.studyTips || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
  await loadPerformanceInsights()
})
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <PageHeader
      title="Performance Insights"
      subtitle="AI insights from your real progress data, plus tips recorded by your tutor."
    />

    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

      <!-- Loading State -->
      <div
        v-if="loading"
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"
      >
        <div
          v-for="n in 6"
          :key="n"
          class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm animate-pulse"
        >
          <div class="h-5 w-24 bg-slate-200 rounded-full mb-5"></div>
          <div class="h-4 bg-slate-200 rounded w-full mb-3"></div>
          <div class="h-4 bg-slate-200 rounded w-5/6 mb-3"></div>
          <div class="h-4 bg-slate-200 rounded w-2/3"></div>
        </div>
      </div>

      <template v-else>
      <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 mb-6">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 class="text-lg font-semibold text-slate-800">Performance Insights</h3>
            <p class="text-sm text-slate-500 mt-1">Generated from your attendance, progress, quizzes, and assignment records.</p>
          </div>
          <button
            type="button"
            class="px-4 py-2 rounded-xl bg-brand-blue text-white text-sm font-semibold disabled:opacity-50"
            :disabled="insightLoading"
            @click="loadPerformanceInsights"
          >
            {{ insightLoading ? 'Generating...' : 'Refresh Insights' }}
          </button>
        </div>
        <div v-if="insightError" class="mt-4 bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-700">
          {{ insightError }}
        </div>

        <template v-else-if="performance?.hasEnoughData">
          <div class="mt-5 flex flex-col sm:flex-row items-center sm:items-stretch gap-5">
            <div
              class="shrink-0 mx-auto sm:mx-0 w-28 h-28 rounded-full flex flex-col items-center justify-center border-4"
              :class="scoreRingClass(performance.overall.averageScore)"
            >
              <span class="text-2xl font-bold text-slate-800">{{ Math.round(performance.overall.averageScore || 0) }}%</span>
              <span class="text-[11px] text-slate-500">avg score</span>
            </div>
            <div class="flex-1 text-center sm:text-left">
              <p class="text-sm leading-6 text-slate-700">{{ performance.overall.summary }}</p>
              <p class="text-xs text-slate-400 mt-2">
                {{ performance.overall.completedQuizzes }} quiz{{ performance.overall.completedQuizzes === 1 ? '' : 'zes' }} completed
              </p>
            </div>
          </div>

          <div v-if="performance.topicPerformance?.length" class="mt-6">
            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Topic Breakdown</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div
                v-for="topic in performance.topicPerformance"
                :key="topic.subject + topic.topic"
                class="rounded-xl border p-3 flex items-center justify-between gap-3"
                :class="statusStyle(topic.status).bg"
              >
                <div class="min-w-0">
                  <p class="text-sm font-medium text-slate-800 truncate">{{ topic.subject }} - {{ topic.topic }}</p>
                  <p class="text-xs mt-0.5" :class="statusStyle(topic.status).text">{{ topic.status }}</p>
                </div>
                <span class="text-sm font-semibold shrink-0" :class="statusStyle(topic.status).text">{{ Math.round(topic.averageScore) }}%</span>
              </div>
            </div>
          </div>

          <div v-if="performance.missedQuestions?.length" class="mt-6">
            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">What You Got Wrong</p>
            <ul class="space-y-2">
              <li
                v-for="(item, i) in performance.missedQuestions.slice(0, 4)"
                :key="i"
                class="text-sm rounded-xl bg-red-50 border border-red-100 p-3"
              >
                <span class="font-medium text-slate-700">{{ item.topic }}:</span>
                <span class="text-slate-600"> {{ item.question }}</span>
                <span class="block text-xs text-emerald-700 mt-1">Correct answer: {{ item.correctAnswer }}</span>
              </li>
            </ul>
          </div>

          <div v-if="performance.recommendations?.length" class="mt-6 rounded-xl bg-blue-50 border border-blue-100 p-4">
            <p class="text-xs font-semibold text-brand-blue uppercase tracking-wide mb-1">Suggested Next Step</p>
            <p class="text-sm text-slate-700">{{ performance.recommendations[0].nextStep }}</p>
          </div>
        </template>

        <p v-else-if="insights" class="mt-4 whitespace-pre-line text-sm leading-6 text-slate-700">{{ insights }}</p>
        <p v-else class="mt-4 text-sm text-slate-500">Insights will appear here once generated.</p>
      </div>

      <div class="grid grid-cols-1 gap-6 mb-6">
        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 class="text-lg font-semibold text-slate-800">Ask About Your Performance</h3>
          <div class="mt-4 space-y-3 max-h-64 overflow-auto">
            <div
              v-for="(message, index) in chatMessages"
              :key="index"
              class="rounded-2xl p-3 text-sm"
              :class="message.who === 'student' ? 'bg-blue-50 text-slate-700' : 'bg-slate-50 text-slate-700'"
            >
              {{ message.text }}
            </div>
            <p v-if="!chatMessages.length" class="text-sm text-slate-500">Ask what you got wrong, what to revise, or what topic to practice next.</p>
          </div>
          <div v-if="chatError" class="mt-3 bg-red-50 border border-red-200 rounded-xl p-3 text-sm text-red-700">{{ chatError }}</div>
          <div class="flex gap-2 mt-4">
            <input
              v-model="chatMessage"
              class="flex-1 rounded-xl border border-slate-200 px-3 py-2 text-sm"
              placeholder="What did I miss?"
              @keyup.enter="sendChat"
            >
            <button class="px-4 py-2 rounded-xl bg-brand-blue text-white text-sm font-semibold disabled:opacity-50" :disabled="chatLoading" @click="sendChat">
              {{ chatLoading ? 'Sending...' : 'Ask' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div
        v-if="error"
        class="bg-red-50 border border-red-200 rounded-2xl p-6 flex items-start gap-4"
      >
        <div
          class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center shrink-0"
        >
          <span class="text-red-600 text-lg">!</span>
        </div>

        <div>
          <h3 class="font-semibold text-red-800">
            Unable to load study tips
          </h3>
          <p class="text-sm text-red-600 mt-1">
            {{ error }}
          </p>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!tips.length"
        class="bg-white rounded-2xl border border-slate-200 shadow-sm p-10 text-center"
      >
        <div
          class="mx-auto w-16 h-16 rounded-full bg-blue-50 flex items-center justify-center mb-5"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-8 h-8 text-brand-blue"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="1.8"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5S19.832 5.477 21 6.253v13C19.832 18.477 18.246 18 16.5 18s-3.332.477-4.5 1.253"
            />
          </svg>
        </div>

        <h3 class="text-lg font-semibold text-slate-800">
          No study tips yet
        </h3>

        <p class="text-sm text-slate-500 mt-2 max-w-md mx-auto">
          Your tutor hasn't added any study tips yet. Check back later for
          helpful advice and guidance.
        </p>
      </div>

      <!-- Tutor Tips -->
      <div
        v-else
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"
      >
        <div
          v-for="t in tips"
          :key="t.id"
          class="group bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-200"
        >
          <!-- Top Section -->
          <div class="flex items-center justify-between gap-3 mb-5">
            <span
              class="inline-flex items-center px-3 py-1.5 rounded-full bg-blue-50 text-brand-blue text-xs font-semibold"
            >
              {{ t.subject }}
            </span>

            <div
              class="w-9 h-9 rounded-full bg-slate-50 group-hover:bg-blue-50 flex items-center justify-center transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-5 h-5 text-slate-400 group-hover:text-brand-blue transition-colors"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.8"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M12 18.5a6.5 6.5 0 100-13 6.5 6.5 0 000 13z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M12 8.5v4l2.5 1.5"
                />
              </svg>
            </div>
          </div>

          <!-- Tip -->
          <p class="text-slate-700 text-sm leading-6">
            {{ t.tip }}
          </p>

          <!-- Bottom Accent -->
          <div
            class="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2"
          >
            <div class="w-1.5 h-1.5 rounded-full bg-brand-blue"></div>
            <span class="text-xs text-slate-400">
              Tutor's study tip
            </span>
          </div>
        </div>
      </div>
      </template>

    </div>
  </div>
</template>
