<script setup>
import { ref, onMounted } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import { studentApi } from '../../services/studentApi'

const items = ref([])
const loading = ref(true)
const error = ref('')
const busy = ref(null)

// Exactly four states, each with its own color. No 100%-progress
// requirement anywhere - status comes straight from the backend.
const STATUS_STYLE = {
  Pending: 'bg-slate-100 text-slate-600 dark:bg-white/10 dark:text-slate-300',
  'Due Today': 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-400',
  'Due Passed': 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-400',
  Done: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400',
}

async function load() {
  try {
    const r = await studentApi.getAssignments()
    items.value = r.data?.assignments || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function markCompleted(a) {
  if (busy.value) return
  busy.value = a.id
  try {
    await studentApi.markHomeworkCompleted(a.id)
    await load()
  } catch (e) {
    error.value = e.message
  } finally {
    busy.value = null
  }
}
</script>

<template>
  <div>
    <PageHeader title="Homework" subtitle="Your assignment status, straight from the tutor's records." />
    <p v-if="loading" class="text-slate-500">Loading homework...</p>
    <p v-else-if="error" class="text-danger">{{ error }}</p>
    <div v-else-if="!items.length" class="card p-8 text-center text-slate-500">No homework assigned.</div>
    <div v-else class="space-y-3">
      <div v-for="a in items" :key="a.id" class="card p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div class="min-w-0">
          <p class="text-xs text-brand-blue">{{ a.subject }}</p>
          <h3 class="font-semibold truncate">{{ a.title }}</h3>
          <p class="text-sm text-slate-500">Due {{ a.dueDate || 'No due date' }}</p>
        </div>
        <div class="flex items-center gap-3 shrink-0">
          <span
            class="px-3 py-1 rounded-full text-xs font-semibold"
            :class="STATUS_STYLE[a.homeworkStatus] || STATUS_STYLE.Pending"
          >
            {{ a.homeworkStatus }}
          </span>
          <button
            v-if="a.canComplete"
            class="btn grad sm"
            :disabled="busy === a.id"
            @click="markCompleted(a)"
          >
            {{ busy === a.id ? 'Saving...' : 'Mark as Completed' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
