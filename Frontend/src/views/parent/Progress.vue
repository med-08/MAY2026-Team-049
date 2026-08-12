<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { SparklesIcon, AcademicCapIcon } from '@heroicons/vue/24/outline'
import EmptyState from '../../components/ui/EmptyState.vue'
import { useToast } from '../../composables/useToast'
import { useParentPortal } from '../../composables/useParentPortal'

const { showToast } = useToast()
const { children, progressByChild, loadProfile, loadChildProgress, generateWeeklyReport } = useParentPortal()

const selectedChildId = ref(null)
const isGeneratingReport = ref(false)
const generatedReportText = ref('')
const reportError = ref('')

const selectedChild = computed(() =>
  children.value.find((c) => c.student_id === selectedChildId.value)
)

const progress = computed(() =>
  progressByChild.value[selectedChildId.value] || null
)

async function handleGenerateReport() {
  if (!selectedChildId.value) return
  isGeneratingReport.value = true
  reportError.value = ''

  try {
    const report = await generateWeeklyReport(selectedChildId.value)
    generatedReportText.value = report
    showToast('AI Weekly Progress Report generated!', 'success')
  } catch (err) {
    reportError.value = err.message || 'Failed to generate report.'
    showToast(reportError.value, 'error')
  } finally {
    isGeneratingReport.value = false
  }
}

async function init() {
  try {
    await loadProfile()
    if (children.value.length && !selectedChildId.value) {
      selectedChildId.value = children.value[0].student_id
    }
    if (selectedChildId.value) {
      await loadChildProgress(selectedChildId.value)
    }
  } catch (err) {
    showToast(err.message || 'Failed to load progress.', 'error')
  }
}

watch(selectedChildId, async (newId) => {
  if (!newId) return
  generatedReportText.value = ''
  reportError.value = ''
  try {
    await loadChildProgress(newId)
  } catch (err) {
    showToast(err.message || 'Failed to load progress.', 'error')
  }
})

onMounted(init)
</script>

<template>
  <div v-if="selectedChild" class="space-y-6">
    <!-- Child Selection Tabs -->
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

    <!-- AI Weekly Progress Report Section -->
    <div class="card p-6 bg-gradient-to-r from-emerald-500/10 via-teal-500/5 to-cyan-500/10 border border-emerald-500/20 shadow-sm">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div class="flex items-center gap-2 mb-1">
            <SparklesIcon class="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            <h3 class="font-display font-bold text-base text-slate-800 dark:text-slate-100">
              Generate AI Weekly Progress Report
            </h3>
          </div>
          <p class="text-xs text-slate-600 dark:text-slate-400">
            Generate a simple AI progress report for <strong class="text-slate-800 dark:text-slate-200">{{ selectedChild?.student_name }}</strong> based on real attendance and quiz records.
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
            ✨ Parent AI Progress Report
          </span>
          <span class="text-xs text-slate-400">For {{ selectedChild?.student_name }}</span>
        </div>
        <p class="whitespace-pre-line text-xs sm:text-sm font-medium">{{ generatedReportText }}</p>
      </div>
    </div>

    <!-- Child Performance Overview -->
    <div class="card p-5">
      <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">
        Child Performance Overview
      </h3>

      <div v-if="progress" class="space-y-6">
        <!-- Summary Stats -->
        <div class="grid sm:grid-cols-2 gap-4">
          <div class="rounded-xl bg-slate-50 dark:bg-slate-800/60 p-4">
            <p class="text-xs uppercase tracking-wider text-slate-400 font-semibold">Student Name</p>
            <p class="mt-2 text-sm font-semibold text-slate-800 dark:text-slate-100">{{ progress.student_name }}</p>
          </div>

          <div class="rounded-xl bg-slate-50 dark:bg-slate-800/60 p-4">
            <p class="text-xs uppercase tracking-wider text-slate-400 font-semibold">Attendance Rate</p>
            <p class="mt-2 text-sm font-semibold text-slate-800 dark:text-slate-100">{{ progress.attendance_rate }}</p>
          </div>
        </div>

        <!-- Real-Time Session Learning Pace Logs -->
        <div class="card p-5 border border-slate-100 dark:border-slate-800">
          <div class="flex items-center justify-between mb-3">
            <h4 class="font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2">
              <AcademicCapIcon class="w-5 h-5 text-brand-green-500" />
              Per-Session Learning Pace & Status
            </h4>
          </div>
          <div v-if="progress.session_logs?.length" class="overflow-x-auto">
            <table class="w-full text-left">
              <thead>
                <tr class="border-b border-slate-100 dark:border-slate-800">
                  <th class="table-th">Date</th>
                  <th class="table-th">Status</th>
                  <th class="table-th">Learning Pace</th>
                  <th class="table-th">Tutor Observations</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
                <tr v-for="log in progress.session_logs" :key="log.session_id">
                  <td class="table-td text-xs font-medium">{{ log.date }}</td>
                  <td class="table-td">
                    <span 
                      class="px-2.5 py-1 rounded-full text-[11px] font-semibold"
                      :class="log.status === 'Completed' ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400' : 'bg-amber-500/10 text-amber-600 dark:text-amber-400'"
                    >
                      {{ log.status }}
                    </span>
                  </td>
                  <td class="table-td">
                    <span 
                      class="px-2.5 py-1 rounded-full text-[11px] font-semibold"
                      :class="log.learning_pace === 'Fast' ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400' : log.learning_pace === 'Needs Practice' ? 'bg-rose-500/10 text-rose-600 dark:text-rose-400' : 'bg-slate-500/10 text-slate-600 dark:text-slate-400'"
                    >
                      {{ log.learning_pace }}
                    </span>
                  </td>
                  <td class="table-td text-xs text-slate-600 dark:text-slate-300">{{ log.remarks }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <EmptyState v-else title="No session pace records yet" message="Session logs recorded by tutors will appear here." />
        </div>

        <!-- Recent Quiz Scores -->
        <div class="card p-5 border border-slate-100 dark:border-slate-800">
          <h4 class="font-semibold text-slate-800 dark:text-slate-100 mb-3">Recent Quiz Scores</h4>
          <div v-if="progress.recent_quiz_scores?.length" class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-slate-100 dark:border-slate-800">
                  <th class="table-th">Subject</th>
                  <th class="table-th">Topic</th>
                  <th class="table-th">Score</th>
                  <th class="table-th">Date</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
                <tr v-for="quiz in progress.recent_quiz_scores" :key="`${quiz.subject}-${quiz.date}-${quiz.score}`">
                  <td class="table-td">{{ quiz.subject }}</td>
                  <td class="table-td">{{ quiz.topic }}</td>
                  <td class="table-td font-bold text-brand-green-500">{{ quiz.score }}</td>
                  <td class="table-td">{{ quiz.date }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <EmptyState v-else title="No quizzes yet" message="Quiz performance will appear here." />
        </div>

        <!-- Tutor Remarks & Weekly Summaries -->
        <div class="card p-5 border border-slate-100 dark:border-slate-800">
          <h4 class="font-semibold text-slate-800 dark:text-slate-100 mb-3">Tutor Remarks & Weekly Reports</h4>
          <div v-if="progress.tutor_remarks?.length" class="space-y-3">
            <div
              v-for="remark in progress.tutor_remarks"
              :key="`${remark.date}-${remark.remark}`"
              class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-100 dark:border-slate-800"
            >
              <div class="flex items-center justify-between gap-3">
                <p class="text-sm font-semibold text-slate-800 dark:text-slate-100">{{ remark.subject }}</p>
                <span class="text-xs text-slate-400">{{ remark.date }}</span>
              </div>
              <p class="text-sm text-slate-600 dark:text-slate-300 mt-2">{{ remark.remark }}</p>
            </div>
          </div>
          <EmptyState v-else title="No remarks yet" message="Tutor comments will appear here." />
        </div>
      </div>

      <EmptyState v-else title="No progress data yet" message="Progress will appear after the tutor records activity." />
    </div>
  </div>

  <EmptyState v-else title="No linked child found" message="Please contact support if your children are not showing." />
</template>