<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import { useToast } from '../../composables/useToast'
import { useParentPortal } from '../../composables/useParentPortal'

const { showToast } = useToast()
const { children, progressByChild, loadProfile, loadChildProgress } = useParentPortal()

const selectedChildId = ref(null)

const selectedChild = computed(() =>
  children.value.find((c) => c.student_id === selectedChildId.value)
)

const progress = computed(() =>
  progressByChild.value[selectedChildId.value] || null
)

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

    <div class="card p-5">
      <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">
        Child Performance Overview
      </h3>

      <div v-if="progress" class="space-y-6">
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
                  <td class="table-td">{{ quiz.score }}</td>
                  <td class="table-td">{{ quiz.date }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <EmptyState v-else title="No quizzes yet" message="Quiz performance will appear here." />
        </div>

        <div class="card p-5 border border-slate-100 dark:border-slate-800">
          <h4 class="font-semibold text-slate-800 dark:text-slate-100 mb-3">Tutor Remarks</h4>
          <div v-if="progress.tutor_remarks?.length" class="space-y-3">
            <div
              v-for="remark in progress.tutor_remarks"
              :key="`${remark.date}-${remark.remark}`"
              class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60"
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