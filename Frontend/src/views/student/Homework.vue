<script setup>
import { ref, computed, onMounted } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import { studentApi } from '../../services/studentApi'

const items = ref([])
const loading = ref(true)
const error = ref('')
const busy = ref(null)

const STATUS_STYLE = {
  Pending: 'bg-slate-100 text-slate-600 dark:bg-white/10 dark:text-slate-300',
  'Due Today': 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-400',
  'Due Passed': 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-400',
  Done: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400',
}

const statusIcon = {
  Pending: '○',
  'Due Today': '◷',
  'Due Passed': '!',
  Done: '✓',
}

const total = computed(() => items.value.length)
const completed = computed(
  () => items.value.filter(a => a.homeworkStatus === 'Done').length
)
const remaining = computed(() => total.value - completed.value)

function subjectInitial(subject) {
  return subject?.trim()?.charAt(0)?.toUpperCase() || '?'
}

function subjectStyle(subject) {
  const styles = {
    English: 'bg-blue-500',
    Mathematics: 'bg-violet-500',
    Physics: 'bg-cyan-500',
    Chemistry: 'bg-emerald-500',
    Biology: 'bg-green-500',
    Science: 'bg-orange-500',
  }

  return styles[subject] || 'bg-teal-500'
}

async function load() {
  loading.value = true
  error.value = ''

  try {
    const r = await studentApi.getAssignments()
    items.value = r.data?.assignments || []
  } catch (e) {
    error.value = e?.message || 'Unable to load homework.'
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
    error.value = e?.message || 'Unable to update homework.'
  } finally {
    busy.value = null
  }
}
</script>

<template>
  <div>

    <!-- Header -->
    <PageHeader
      title="Homework"
      subtitle="Stay on top of your assignments and deadlines."
    />

    <!-- Small summary -->
    <div
      v-if="!loading && !error && items.length"
      class="mb-5 flex flex-wrap items-center gap-2 text-xs"
    >
      <span class="rounded-full bg-blue-50 px-3 py-1.5 font-semibold text-blue-600">
        {{ total }} Total
      </span>

      <span class="rounded-full bg-amber-50 px-3 py-1.5 font-semibold text-amber-600">
        {{ remaining }} Remaining
      </span>

      <span class="rounded-full bg-emerald-50 px-3 py-1.5 font-semibold text-emerald-600">
        {{ completed }} Completed
      </span>
    </div>

    <!-- Loading -->
    <div
      v-if="loading"
      class="py-10 text-center"
    >
      <div
        class="mx-auto mb-3 h-7 w-7 animate-spin rounded-full border-2 border-slate-200 border-t-teal-500"
      ></div>

      <p class="text-sm text-slate-500">
        Loading homework...
      </p>
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-600"
    >
      {{ error }}

      <button
        class="ml-2 font-semibold underline"
        @click="load"
      >
        Retry
      </button>
    </div>

    <!-- Empty -->
    <div
      v-else-if="!items.length"
      class="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-6 py-10 text-center dark:border-slate-700 dark:bg-white/5"
    >
      <div class="text-3xl">
        📚
      </div>

      <p class="mt-2 font-semibold text-slate-700 dark:text-slate-200">
        No homework yet
      </p>

      <p class="mt-1 text-xs text-slate-500">
        Assignments from your tutors will appear here.
      </p>
    </div>

    <!-- Homework list -->
    <div
      v-else
      class="space-y-2.5"
    >

      <div
        v-for="a in items"
        :key="a.id"
        class="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md dark:border-slate-700 dark:bg-slate-900"
      >

        <!-- Subject colour strip -->
        <div
          class="absolute inset-y-0 left-0 w-1"
          :class="subjectStyle(a.subject)"
        ></div>

        <div
          class="flex flex-col gap-3 py-3.5 pl-4 pr-3 sm:flex-row sm:items-center"
        >

          <!-- Subject -->
          <div class="flex items-center gap-3 sm:w-[230px]">

            <div
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-sm font-bold text-white shadow-sm"
              :class="subjectStyle(a.subject)"
            >
              {{ subjectInitial(a.subject) }}
            </div>

            <div class="min-w-0">
              <p
                class="text-[11px] font-bold uppercase tracking-wide text-slate-400"
              >
                {{ a.subject }}
              </p>

              <h3
                class="truncate text-sm font-bold text-slate-800 dark:text-white"
                :title="a.title"
              >
                {{ a.title }}
              </h3>
            </div>

          </div>

          <!-- Due -->
          <div class="flex items-center gap-2 sm:w-[170px]">

            <div
              class="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 text-sm dark:bg-slate-800"
            >
              📅
            </div>

            <div>
              <p class="text-[10px] uppercase tracking-wide text-slate-400">
                Due date
              </p>

              <p class="text-xs font-semibold text-slate-700 dark:text-slate-300">
                {{ a.dueDate || 'No due date' }}
              </p>
            </div>

          </div>

          <!-- Status -->
          <div class="flex-1">

            <span
              class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-bold"
              :class="
                STATUS_STYLE[a.homeworkStatus] ||
                STATUS_STYLE.Pending
              "
            >
              <span>
                {{ statusIcon[a.homeworkStatus] || '○' }}
              </span>

              {{ a.homeworkStatus || 'Pending' }}
            </span>

          </div>

          <!-- Action -->
          <div class="sm:w-[145px] sm:text-right">

            <button
              v-if="a.canComplete"
              class="w-full rounded-lg bg-gradient-to-r from-teal-500 to-blue-500 px-3 py-2 text-xs font-bold text-white shadow-sm transition hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
              :disabled="busy === a.id"
              @click="markCompleted(a)"
            >
              {{ busy === a.id ? 'Saving...' : '✓ Mark Complete' }}
            </button>

            <span
              v-else-if="a.homeworkStatus === 'Done'"
              class="text-xs font-bold text-emerald-600"
            >
              ✓ Completed
            </span>

          </div>

        </div>

      </div>

    </div>

  </div>
</template>