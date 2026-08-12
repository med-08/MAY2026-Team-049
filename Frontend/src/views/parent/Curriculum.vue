<script setup>
import { computed, ref, onMounted, watch } from 'vue'
import { BookOpenIcon } from '@heroicons/vue/24/outline'
import EmptyState from '../../components/ui/EmptyState.vue'
import { useToast } from '../../composables/useToast'
import { useParentPortal } from '../../composables/useParentPortal'

const { showToast } = useToast()
const { children, curriculumByChild, loadProfile, loadCurriculum } = useParentPortal()

const selectedChildId = ref(null)

const selectedChild = computed(() =>
  children.value.find((c) => c.student_id === selectedChildId.value)
)

const plan = computed(() =>
  curriculumByChild.value[selectedChildId.value]?.curriculum_plan || []
)

const groupedByMonth = computed(() => {
  const groups = {}
  plan.value.forEach((item, index) => {
    const month = item.month || 'Untitled Month'
    if (!groups[month]) groups[month] = []
    groups[month].push({
      ...item,
      _key: item.plan_id || `${month}-${index}`
    })
  })
  return groups
})

function formatDate(dateStr) {
  if (!dateStr) return 'No date'
  return new Date(dateStr).toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  })
}

async function init() {
  try {
    await loadProfile()
    if (children.value.length && !selectedChildId.value) {
      selectedChildId.value = children.value[0].student_id
    }
    if (selectedChildId.value) {
      await loadCurriculum(selectedChildId.value)
    }
  } catch (err) {
    showToast(err.message || 'Failed to load curriculum.', 'error')
  }
}

watch(selectedChildId, async (newId) => {
  if (!newId) return
  try {
    await loadCurriculum(newId)
  } catch (err) {
    showToast(err.message || 'Failed to load curriculum.', 'error')
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

    <p class="text-sm text-slate-500 dark:text-slate-400">
      The tutor's planned topics for {{ selectedChild.student_name }}, so you can confirm tuition stays aligned with school learning.
    </p>

    <div v-if="Object.keys(groupedByMonth).length" class="space-y-6">
      <div v-for="(items, month) in groupedByMonth" :key="month" class="card p-5">
        <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4 flex items-center gap-2">
          <BookOpenIcon class="w-5 h-5 text-brand-blue-500" />
          {{ month }}
        </h3>
        <div class="space-y-3">
          <div
            v-for="item in items"
            :key="item._key"
            class="flex items-center justify-between gap-3 p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60"
          >
            <div>
              <p class="text-sm font-semibold text-slate-800 dark:text-slate-100">
                {{ Array.isArray(item.topics) ? item.topics.join(', ') : item.topic_name || 'No topic' }}
              </p>
              <p class="text-xs text-slate-500 dark:text-slate-400">{{ item.subject || 'Subject' }}</p>
            </div>
            <span class="text-xs font-semibold px-2.5 py-1 rounded-full bg-brand-blue-100 text-brand-blue-700 dark:bg-brand-blue-500/15 dark:text-brand-blue-400 shrink-0">
              {{ formatDate(item.planned_date) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <EmptyState v-else title="No plan published yet" message="The tutor hasn't shared a curriculum plan for this child." />
  </div>

  <EmptyState v-else title="No linked child found" message="Please contact support if your children are not showing." />
</template>