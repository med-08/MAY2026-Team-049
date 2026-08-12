<script setup>
import { ref, computed, onMounted } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import { studentApi } from '../../services/studentApi'

const days = ref([])
const classesByDay = ref({})
const loading = ref(true)
const error = ref('')

// Always show Mon-Sat in the same fixed, straight horizontal order,
// regardless of what order/shape the backend happens to return.
const WEEK_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

const orderedDays = computed(() => WEEK_ORDER)

function classesFor(day) {
  const list = classesByDay.value?.[day]
  return Array.isArray(list) ? list : []
}

onMounted(async () => {
  try {
    const r = await studentApi.getTimetable()
    days.value = r.data?.days || []
    classesByDay.value = r.data?.classes || {}
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <PageHeader title="Timetable" subtitle="Your actual booked schedule, Monday through Saturday." />

    <p v-if="loading" class="text-slate-500">Loading timetable...</p>
    <p v-else-if="error" class="text-danger">{{ error }}</p>

    <div v-else class="card p-0 overflow-hidden hidden sm:block">
      <div class="overflow-x-auto">
        <div class="min-w-[900px] grid grid-cols-6 divide-x divide-slate-100 dark:divide-border-dark">
          <div
            v-for="day in orderedDays"
            :key="day"
            class="flex flex-col"
          >
            <div class="px-3 py-3 text-center font-display font-bold text-sm bg-slate-50 dark:bg-white/5 border-b border-slate-100 dark:border-border-dark truncate">
              {{ day }}
            </div>

            <div class="flex-1 p-2.5 space-y-2 min-h-[140px]">
              <p v-if="!classesFor(day).length" class="text-xs text-slate-400 text-center pt-4">
                No session
              </p>

              <div
                v-for="c in classesFor(day)"
                :key="c.session_id ?? `${day}-${c.time}-${c.subject}`"
                class="rounded-xl bg-slate-50 dark:bg-white/5 p-2.5"
              >
                <p class="font-semibold text-sm truncate" :title="c.subject || 'Subject'">
                  {{ c.subject || 'Subject' }}
                </p>
                <p class="text-xs text-slate-500 mt-0.5 truncate">{{ c.time || '--' }}</p>
                <p class="text-xs text-slate-500 truncate" :title="c.tutor || 'Tutor'">
                  {{ c.tutor || 'Tutor' }} &middot; {{ c.status || 'Scheduled' }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Compact stacked view for very small screens -->
    <div v-if="!loading && !error" class="sm:hidden space-y-4">
      <div v-for="day in orderedDays" :key="`m-${day}`" class="card p-4">
        <h3 class="font-display font-bold mb-2">{{ day }}</h3>
        <p v-if="!classesFor(day).length" class="text-sm text-slate-400">No session.</p>
        <div v-for="c in classesFor(day)" :key="c.session_id ?? `${day}-m-${c.time}`" class="rounded-xl bg-slate-50 dark:bg-white/5 p-3 mb-2">
          <p class="font-semibold">{{ c.subject || 'Subject' }}</p>
          <p class="text-sm text-slate-500">{{ c.time || '--' }}</p>
          <p class="text-xs text-slate-500">{{ c.tutor || 'Tutor' }} &middot; {{ c.status || 'Scheduled' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
