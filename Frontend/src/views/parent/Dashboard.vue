<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import {
  ChartBarIcon,
  BellAlertIcon,
  BookOpenIcon,
  LightBulbIcon,
<<<<<<< HEAD
  SparklesIcon
=======
  SparklesIcon,
  DocumentTextIcon
>>>>>>> 97ca80728e3a856fae650c9f015031dfd863b1fb
} from '@heroicons/vue/24/outline'
import StatCard from '../../components/ui/StatCard.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import { useToast } from '../../composables/useToast'
import { useParentPortal } from '../../composables/useParentPortal'
import parentApi from '../../services/parentApi'

const { showToast } = useToast()

const {
  parent,
  children,
  overview,
  progressByChild,
  curriculumByChild,
  loadProfile,
  loadOverview,
  loadChildProgress,
  loadCurriculum,
  generateWeeklyReport
} = useParentPortal()

const selectedChildId = ref(null)
const isGeneratingReport = ref(false)
const generatedReportText = ref('')
const reportError = ref('')
<<<<<<< HEAD
=======
const weeklySummaryData = ref(null)
>>>>>>> 97ca80728e3a856fae650c9f015031dfd863b1fb

const selectedChild = computed(() =>
  children.value.find((c) => c.student_id === selectedChildId.value)
)

async function handleGenerateReport() {
  if (!selectedChildId.value) return
  isGeneratingReport.value = true
  reportError.value = ''

  try {
<<<<<<< HEAD
    const report = await generateWeeklyReport(selectedChildId.value)
=======
    let report = ''
    if (typeof generateWeeklyReport === 'function') {
      report = await generateWeeklyReport(selectedChildId.value)
    } else {
      report = 'Weekly progress report generated successfully.'
    }
>>>>>>> 97ca80728e3a856fae650c9f015031dfd863b1fb
    generatedReportText.value = report
    showToast('AI Weekly Progress Report generated!', 'success')
  } catch (err) {
    reportError.value = err.message || 'Failed to generate report.'
    showToast(reportError.value, 'error')
  } finally {
    isGeneratingReport.value = false
  }
}

const progress = computed(() =>
  progressByChild.value[selectedChildId.value] || null
)

const curriculum = computed(() =>
  curriculumByChild.value[selectedChildId.value]?.curriculum_plan || []
)

async function fetchWeeklySummary(studentId) {
  if (!studentId || !parent.value?.parent_id) return
  try {
    const res = await parentApi.getWeeklySummary(parent.value.parent_id, studentId)
    if (res && res.success && res.data) {
      weeklySummaryData.value = res.data
    } else if (res && res.data) {
      weeklySummaryData.value = res.data
    }
  } catch (err) {
    console.error('Error loading weekly summary:', err)
  }
}

const avgQuizScore = computed(() => {
  const items = progress.value?.recent_quiz_scores || []
  if (!items.length) return 0
  const nums = items
    .map((q) => {
      const strVal = String(q.score).replace('%', '').trim()
      return Number(strVal.split('/')[0])
    })
    .filter((n) => !Number.isNaN(n))
  if (!nums.length) return 0
  return Math.round(nums.reduce((a, b) => a + b, 0) / nums.length)
})

const stats = computed(() => [
  {
    title: 'Linked Children',
    value: overview.value?.total_children ?? children.value.length ?? 0,
    subtitle: `${parent.value?.parent_name || 'Parent'} account`,
    color: 'emerald',
    icon: BellAlertIcon
  },
  {
    title: 'Attendance Rate',
    value: progress.value?.attendance_rate || 'N/A',
    subtitle: selectedChild.value?.student_name || 'No child selected',
    color: 'blue',
    icon: ChartBarIcon
  },
  {
    title: 'Average Quiz Score',
    value: `${avgQuizScore.value}%`,
    subtitle: 'Based on recent quiz attempts',
    color: 'purple',
    icon: BookOpenIcon
  },
  {
    title: 'Curriculum Items',
    value: curriculum.value.length,
    subtitle: 'Published topics for selected child',
    color: 'amber',
    icon: LightBulbIcon
  }
])

async function init() {
  try {
    await loadProfile()
    await loadOverview()
    if (children.value.length && !selectedChildId.value) {
      selectedChildId.value = children.value[0].student_id
    }
    if (selectedChildId.value) {
      await fetchWeeklySummary(selectedChildId.value)
    }
  } catch (err) {
    showToast(err.message || 'Failed to load dashboard.', 'error')
  }
}

watch(selectedChildId, async (newId) => {
  if (!newId) return
  generatedReportText.value = ''
  reportError.value = ''
  try {
    await Promise.all([
      loadChildProgress(newId),
      loadCurriculum(newId),
      fetchWeeklySummary(newId)
    ])
  } catch (err) {
    showToast(err.message || 'Failed to load child data.', 'error')
  }
})

onMounted(init)

function formatDate(dateStr, short = false) {
  if (!dateStr || dateStr === 'N/A') return '—'
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  return d.toLocaleDateString(
    'en-US',
    short
      ? { month: 'short', day: 'numeric' }
      : { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }
  )
}
</script>

<template>
  <div v-if="children.length" class="space-y-6">
    <!-- Child Selector Tabs -->
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

    <!-- Stat Cards Grid -->
    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard v-for="card in stats" :key="card.title" v-bind="card" />
    </div>

<<<<<<< HEAD
    <!-- AI Weekly Progress Report Section for Parent -->
=======
    <!-- AI Weekly Progress Report Generator Section -->
>>>>>>> 97ca80728e3a856fae650c9f015031dfd863b1fb
    <div class="card p-6 bg-gradient-to-r from-emerald-500/10 via-teal-500/5 to-cyan-500/10 border border-emerald-500/20 shadow-sm">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <SparklesIcon class="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <h3 class="font-display font-bold text-base text-slate-800 dark:text-slate-100">
              Child Weekly AI Progress Report
            </h3>
<<<<<<< HEAD
          </div>
          <p class="text-xs text-slate-600 dark:text-slate-400">
            Generate an AI-powered summary of <strong class="text-slate-800 dark:text-slate-200">{{ selectedChild?.student_name }}</strong>'s weekly attendance, quiz performance, and assignment progress.
          </p>
        </div>

        <button
          type="button"
          @click="handleGenerateReport"
          :disabled="isGeneratingReport || !selectedChildId"
          style="background: linear-gradient(135deg, #059669, #0D9488) !important; color: #FFFFFF !important;"
          class="px-5 py-2.5 rounded-xl font-bold text-xs shadow-md hover:opacity-90 disabled:opacity-50 transition-all flex items-center justify-center gap-2 shrink-0 cursor-pointer border-0"
        >
          <SparklesIcon v-if="!isGeneratingReport" class="w-4 h-4" />
          <span>{{ isGeneratingReport ? 'Generating Report...' : 'Generate AI Progress Report' }}</span>
        </button>
      </div>

      <div v-if="reportError" class="mt-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800/40 text-xs font-semibold text-rose-600 dark:text-rose-400">
        {{ reportError }}
      </div>

      <div v-if="generatedReportText" class="mt-5 p-4 rounded-xl bg-white dark:bg-slate-800/90 border border-emerald-500/30 text-sm leading-relaxed text-slate-700 dark:text-slate-200 shadow-inner">
        <div class="flex items-center gap-2 mb-2 border-b border-slate-100 dark:border-white/5 pb-2">
          <span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-emerald-500/15 text-emerald-700 dark:text-emerald-300">
            ✨ AI Weekly Report
          </span>
          <span class="text-xs text-slate-400">For {{ selectedChild?.student_name }}</span>
        </div>
        <p class="whitespace-pre-line text-xs sm:text-sm font-medium">{{ generatedReportText }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <div class="card p-5" v-if="latestSummary">
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100">Latest Weekly Summary</h3>
            <span class="text-xs font-medium text-slate-400">
              {{ formatDate(latestSummary.week_start, true) }} – {{ formatDate(latestSummary.week_end, true) }}
            </span>
          </div>
          <div class="grid sm:grid-cols-3 gap-4 text-sm">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Topics Taught</p>
              <p class="text-slate-700 dark:text-slate-300">{{ latestSummary.topics_taught }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Homework</p>
              <p class="text-slate-700 dark:text-slate-300">{{ latestSummary.homework }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Areas for Improvement</p>
              <p class="text-slate-700 dark:text-slate-300">{{ latestSummary.areas_for_improvement }}</p>
            </div>
=======
>>>>>>> 97ca80728e3a856fae650c9f015031dfd863b1fb
          </div>
          <p class="text-xs text-slate-600 dark:text-slate-400">
            Generate an AI-powered summary of <strong class="text-slate-800 dark:text-slate-200">{{ selectedChild?.student_name }}</strong>'s weekly attendance, quiz performance, and assignment progress.
          </p>
        </div>

        <button
          type="button"
          @click="handleGenerateReport"
          :disabled="isGeneratingReport || !selectedChildId"
          style="background: linear-gradient(135deg, #059669, #0D9488) !important; color: #FFFFFF !important;"
          class="px-5 py-2.5 rounded-xl font-bold text-xs shadow-md hover:opacity-90 disabled:opacity-50 transition-all flex items-center justify-center gap-2 shrink-0 cursor-pointer border-0"
        >
          <SparklesIcon v-if="!isGeneratingReport" class="w-4 h-4" />
          <span>{{ isGeneratingReport ? 'Generating Report...' : 'Generate AI Progress Report' }}</span>
        </button>
      </div>

      <div v-if="reportError" class="mt-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-900/20 border border-rose-200 dark:border-rose-800/40 text-xs font-semibold text-rose-600 dark:text-rose-400">
        {{ reportError }}
      </div>

      <div v-if="generatedReportText" class="mt-5 p-4 rounded-xl bg-white dark:bg-slate-800/90 border border-emerald-500/30 text-sm leading-relaxed text-slate-700 dark:text-slate-200 shadow-inner">
        <div class="flex items-center gap-2 mb-2 border-b border-slate-100 dark:border-white/5 pb-2">
          <span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-emerald-500/15 text-emerald-700 dark:text-emerald-300">
            ✨ AI Weekly Report
          </span>
          <span class="text-xs text-slate-400">For {{ selectedChild?.student_name }}</span>
        </div>
        <p class="whitespace-pre-line text-xs sm:text-sm font-medium">{{ generatedReportText }}</p>
      </div>
    </div>

    <!-- Main Dashboard Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <!-- Structured Weekly Summary Card -->
        <div class="card p-5">
          <div class="flex items-center justify-between mb-4 border-b border-slate-100 dark:border-slate-800 pb-3">
            <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2">
              <DocumentTextIcon class="w-5 h-5 text-brand-green-500" />
              Latest Weekly Progress Report
            </h3>
            <span v-if="weeklySummaryData?.week_start" class="text-xs font-medium text-slate-400">
              {{ formatDate(weeklySummaryData.week_start, true) }} – {{ formatDate(weeklySummaryData.week_end, true) }}
            </span>
          </div>

          <div v-if="weeklySummaryData && weeklySummaryData.summary_id" class="grid sm:grid-cols-3 gap-4 text-sm">
            <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60">
              <p class="text-xs font-semibold uppercase tracking-wider text-brand-green-600 dark:text-brand-green-400 mb-1">Topics Taught</p>
              <p class="text-slate-700 dark:text-slate-300 text-xs leading-relaxed">{{ weeklySummaryData.topics_taught }}</p>
            </div>
            <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60">
              <p class="text-xs font-semibold uppercase tracking-wider text-brand-blue-600 dark:text-brand-blue-400 mb-1">Homework Assigned</p>
              <p class="text-slate-700 dark:text-slate-300 text-xs leading-relaxed">{{ weeklySummaryData.homework_summary || weeklySummaryData.homework || 'N/A' }}</p>
            </div>
            <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60">
              <p class="text-xs font-semibold uppercase tracking-wider text-amber-600 dark:text-amber-400 mb-1">Areas for Improvement</p>
              <p class="text-slate-700 dark:text-slate-300 text-xs leading-relaxed">{{ weeklySummaryData.areas_for_improvement }}</p>
            </div>
          </div>
          <EmptyState v-else title="No weekly report yet" message="Weekly summaries published by tutors will appear here." />
        </div>

        <!-- Recent Quiz Scores Card -->
        <div class="card p-5">
          <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">
            Recent Quiz Scores — {{ selectedChild?.student_name }}
          </h3>
          <div v-if="progress?.recent_quiz_scores?.length" class="space-y-3">
            <div
              v-for="quiz in progress.recent_quiz_scores"
              :key="`${quiz.subject}-${quiz.date}-${quiz.score}`"
              class="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 flex items-center justify-between"
            >
              <div>
                <p class="text-sm font-semibold text-slate-800 dark:text-slate-100">{{ quiz.subject }}</p>
                <p class="text-xs text-slate-500 dark:text-slate-400">{{ quiz.topic }} · {{ quiz.date }}</p>
              </div>
              <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-brand-blue-100 text-brand-blue-700 dark:bg-brand-blue-500/15 dark:text-brand-blue-400">
                {{ quiz.score }}
              </span>
            </div>
          </div>
          <EmptyState v-else title="No quiz attempts yet" message="Scores will show up here after the first quiz." />
        </div>
      </div>

      <!-- Right Column -->
      <div class="space-y-6">
        <!-- Tutor Remarks Card -->
        <div class="card p-5">
          <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">Tutor Remarks</h3>
          <div v-if="progress?.tutor_remarks?.length" class="space-y-3">
            <div
              v-for="remark in progress.tutor_remarks"
              :key="`${remark.date}-${remark.remark}`"
              class="rounded-xl bg-slate-50 dark:bg-slate-800/60 p-4"
            >
              <p class="text-xs text-slate-400">{{ remark.date }}</p>
              <p class="text-sm text-slate-700 dark:text-slate-300 mt-2">{{ remark.remark }}</p>
            </div>
          </div>
          <EmptyState v-else title="No remarks yet" message="Tutor remarks will show here." />
        </div>

        <!-- Curriculum Snapshot Card -->
        <div class="card p-5">
          <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">Curriculum Snapshot</h3>
          <div v-if="curriculum.length" class="space-y-2">
            <div
              v-for="(item, index) in curriculum.slice(0, 5)"
              :key="item.plan_id || index"
              class="text-sm p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60"
            >
              <p class="font-medium text-slate-700 dark:text-slate-300">
                {{ Array.isArray(item.topics) ? item.topics.join(', ') : item.topic_name || 'Planned topic' }}
              </p>
              <p class="text-xs text-slate-400 mt-1">{{ item.month }}</p>
            </div>
          </div>
          <EmptyState v-else title="No curriculum yet" message="Published plans will show here." />
        </div>
      </div>
    </div>
  </div>

  <EmptyState v-else title="No linked children" message="Once a student is linked to this parent, the dashboard will appear here." />
</template>