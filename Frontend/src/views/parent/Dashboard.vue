<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import {
  ChartBarIcon,
  BellAlertIcon,
  BookOpenIcon,
  LightBulbIcon
} from '@heroicons/vue/24/outline'
import StatCard from '../../components/ui/StatCard.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import { useToast } from '../../composables/useToast'
import { useParentPortal } from '../../composables/useParentPortal'

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
  loadCurriculum
} = useParentPortal()

const selectedChildId = ref(null)

const selectedChild = computed(() =>
  children.value.find((c) => c.student_id === selectedChildId.value)
)

const progress = computed(() =>
  progressByChild.value[selectedChildId.value] || null
)

const curriculum = computed(() =>
  curriculumByChild.value[selectedChildId.value]?.curriculum_plan || []
)

const latestSummary = computed(() => overview.value?.latest_summary || null)

const avgQuizScore = computed(() => {
  const items = progress.value?.recent_quiz_scores || []
  if (!items.length) return 0
  const nums = items
    .map((q) => Number(String(q.score).split('/')[0]))
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
  } catch (err) {
    showToast(err.message || 'Failed to load dashboard.', 'error')
  }
}

watch(selectedChildId, async (newId) => {
  if (!newId) return
  try {
    await Promise.all([
      loadChildProgress(newId),
      loadCurriculum(newId)
    ])
  } catch (err) {
    showToast(err.message || 'Failed to load child data.', 'error')
  }
})

onMounted(init)

function formatDate(dateStr, short = false) {
  if (!dateStr) return '—'
  const d = new Date(dateStr)
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

    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-4">
      <StatCard v-for="card in stats" :key="card.title" v-bind="card" />
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
          </div>
        </div>

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

      <div class="space-y-6">
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