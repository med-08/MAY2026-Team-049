<script setup>
import { computed, ref } from 'vue'
import {
  ClipboardDocumentCheckIcon
} from '@heroicons/vue/24/outline'
import EmptyState from '../../components/ui/EmptyState.vue'
import { useParentPortal } from '../../composables/useParentPortal'

const { children, completedSessions, assignmentsFor, quizHistory } = useParentPortal(1)

const selectedChildId = ref(children.value[0]?.student_id)
const selectedChild = computed(() => children.value.find((c) => c.student_id === selectedChildId.value))

const sessionHistory = computed(() => completedSessions(selectedChildId.value))
const assignmentList = computed(() => assignmentsFor(selectedChildId.value))
const quizzes = computed(() => quizHistory(selectedChildId.value))

function formatDate(dateStr, short = false) {
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', short
    ? { month: 'short', day: 'numeric' }
    : { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })
}
function formatDateTime(dateStr) {
  if (!dateStr) return '\u2014'
  return new Date(dateStr).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
}

function statusStyle(status) {
  if (status === 'Completed') return 'bg-brand-blue-100 text-brand-blue-700 dark:bg-brand-blue-500/15 dark:text-brand-blue-400'
  if (status === 'Partially Completed') return 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-400'
  return 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-400'
}
function paceStyle(pace) {
  if (pace === 'Fast') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400'
  if (pace === 'Average') return 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-400'
  return 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-400'
}
function submissionStyle(status) {
  if (status === 'Submitted') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400'
  if (status === 'Late') return 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-400'
  return 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-400'
}
</script>

<template>
  <div v-if="selectedChild" class="space-y-6">
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

    <!-- Learning progress -->
    <div class="card p-5">
      <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">
        Learning Progress by Session
      </h3>
      <div v-if="sessionHistory.length" class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-100 dark:border-slate-800">
              <th class="table-th">Subject</th>
              <th class="table-th">Date</th>
              <th class="table-th">Tutor</th>
              <th class="table-th">Status</th>
              <th class="table-th">Pace</th>
              <th class="table-th">Tutor Remarks</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
            <tr v-for="s in sessionHistory" :key="s.session_id">
              <td class="table-td font-medium text-slate-800 dark:text-slate-100">{{ s.subjectName }}</td>
              <td class="table-td text-slate-500 dark:text-slate-400">{{ formatDate(s.session_date, true) }}</td>
              <td class="table-td text-slate-500 dark:text-slate-400">{{ s.tutorName }}</td>
              <td class="table-td">
                <span v-if="s.progress" class="px-2.5 py-1 rounded-full text-xs font-semibold" :class="statusStyle(s.progress.session_completion_status)">
                  {{ s.progress.session_completion_status }}
                </span>
                <span v-else class="text-xs text-slate-400">Not yet recorded</span>
              </td>
              <td class="table-td">
                <span v-if="s.progress" class="px-2.5 py-1 rounded-full text-xs font-semibold" :class="paceStyle(s.progress.learning_pace)">
                  {{ s.progress.learning_pace }}
                </span>
                <span v-else>—</span>
              </td>
              <td class="table-td max-w-xs whitespace-normal text-slate-500 dark:text-slate-400">
                {{ s.progress?.tutor_remarks || '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <EmptyState v-else title="No sessions yet" message="Progress will appear after the first completed session." />
    </div>

    <!-- Quiz history -->
    <div class="card p-5">
      <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">Weekly Quiz History</h3>
      <div v-if="quizzes.length" class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-slate-100 dark:border-slate-800">
              <th class="table-th">Quiz</th>
              <th class="table-th">Subject</th>
              <th class="table-th">Week</th>
              <th class="table-th">Score</th>
              <th class="table-th">Attempted</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
            <tr v-for="q in quizzes" :key="q.attempt_id">
              <td class="table-td font-medium text-slate-800 dark:text-slate-100">{{ q.title }}</td>
              <td class="table-td text-slate-500 dark:text-slate-400">{{ q.subjectName }}</td>
              <td class="table-td text-slate-500 dark:text-slate-400">Week {{ q.week_number }}</td>
              <td class="table-td">
                <span
                  class="px-2.5 py-1 rounded-full text-xs font-semibold"
                  :class="q.score >= 75 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400' : q.score >= 50 ? 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-400' : 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-400'"
                >
                  {{ q.score }}%
                </span>
              </td>
              <td class="table-td text-slate-500 dark:text-slate-400">{{ formatDateTime(q.attempted_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <EmptyState v-else title="No quiz attempts yet" message="Weekly quiz results will appear here." />
    </div>

    <!-- Assignments -->
    <div class="card p-5">
      <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4 flex items-center gap-2">
        <ClipboardDocumentCheckIcon class="w-5 h-5 text-brand-blue-500" />
        Assignments
      </h3>
      <div v-if="assignmentList.length" class="space-y-3">
        <div v-for="a in assignmentList" :key="a.assignment_id" class="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60">
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-sm font-semibold text-slate-800 dark:text-slate-100">{{ a.title }}</p>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{{ a.sessionSubject }} · Due {{ formatDate(a.due_date, true) }}</p>
            </div>
            <span class="px-2.5 py-1 rounded-full text-xs font-semibold shrink-0" :class="submissionStyle(a.submission?.status || 'Pending')">
              {{ a.submission?.status || 'Pending' }}
            </span>
          </div>
          <p v-if="a.submission?.tutor_feedback" class="text-xs text-slate-500 dark:text-slate-400 mt-2">
            <span class="font-semibold text-slate-600 dark:text-slate-300">Tutor feedback:</span> {{ a.submission.tutor_feedback }}
          </p>
        </div>
      </div>
      <EmptyState v-else title="No assignments yet" message="Assignments will appear here after a session." />
    </div>
  </div>
</template>
