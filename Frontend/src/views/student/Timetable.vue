<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import StatusBadge from '../../components/student/StatusBadge.vue'
import { studentApi } from '../../services/studentApi'

const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
const MONTH_LABELS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

const today = new Date()

// The single source of truth for which month/year the calendar is showing.
// Everything else (grid, header label, API call) derives from this.
const viewYear = ref(today.getFullYear())
const viewMonth = ref(today.getMonth() + 1) // 1-12

const loading = ref(true)
const error = ref('')
const daysMap = ref({}) // { "YYYY-MM-DD": [session, ...] }

function isoOf(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const todayIso = isoOf(today)

const monthLabel = computed(() => `${MONTH_LABELS[viewMonth.value - 1]} ${viewYear.value}`)

// Builds a Monday-first calendar grid for the currently selected month/year,
// padded with the leading/trailing days from neighbouring months so every
// week row has exactly 7 cells - this is what makes it a real calendar
// instead of a fixed weekday table.
const weeks = computed(() => {
  const firstOfMonth = new Date(viewYear.value, viewMonth.value - 1, 1)
  const totalDaysInMonth = new Date(viewYear.value, viewMonth.value, 0).getDate()
  const leadingBlanks = (firstOfMonth.getDay() + 6) % 7 // convert Sun=0..Sat=6 -> Mon=0..Sun=6

  const cells = []
  for (let i = leadingBlanks; i > 0; i--) {
    cells.push(new Date(viewYear.value, viewMonth.value - 1, 1 - i))
  }
  for (let d = 1; d <= totalDaysInMonth; d++) {
    cells.push(new Date(viewYear.value, viewMonth.value - 1, d))
  }
  while (cells.length % 7 !== 0) {
    const next = new Date(cells[cells.length - 1])
    next.setDate(next.getDate() + 1)
    cells.push(next)
  }

  const result = []
  for (let i = 0; i < cells.length; i += 7) {
    result.push(
      cells.slice(i, i + 7).map((date) => ({
        date,
        iso: isoOf(date),
        inMonth: date.getMonth() === viewMonth.value - 1,
        isToday: isoOf(date) === todayIso,
      }))
    )
  }
  return result
})

function sessionsFor(iso) {
  const list = daysMap.value?.[iso]
  return Array.isArray(list) ? list : []
}

async function loadTimetable() {
  loading.value = true
  error.value = ''
  try {
    const r = await studentApi.getTimetable(viewYear.value, viewMonth.value)
    daysMap.value = r.data?.days || {}
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function goToPrevMonth() {
  if (viewMonth.value === 1) {
    viewMonth.value = 12
    viewYear.value -= 1
  } else {
    viewMonth.value -= 1
  }
}

function goToNextMonth() {
  if (viewMonth.value === 12) {
    viewMonth.value = 1
    viewYear.value += 1
  } else {
    viewMonth.value += 1
  }
}

function goToToday() {
  viewYear.value = today.getFullYear()
  viewMonth.value = today.getMonth() + 1
}

// Re-fetch whenever the selected month/year changes, so the calendar always
// reflects sessions for exactly the month/year currently in view.
watch([viewYear, viewMonth], loadTimetable)

onMounted(loadTimetable)
</script>

<template>
  <div>
    <PageHeader title="Timetable" subtitle="Your actual booked schedule, by date." />

    <!-- Month navigation -->
    <div class="flex items-center justify-between mb-4 gap-3 flex-wrap">
      <div class="flex items-center gap-2">
        <button
          type="button"
          @click="goToPrevMonth"
          class="w-9 h-9 flex items-center justify-center rounded-xl border border-slate-200 dark:border-border-dark hover:bg-slate-50 dark:hover:bg-white/5 transition"
          aria-label="Previous month"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
        </button>
        <h2 class="font-display font-bold text-lg min-w-[160px] text-center">{{ monthLabel }}</h2>
        <button
          type="button"
          @click="goToNextMonth"
          class="w-9 h-9 flex items-center justify-center rounded-xl border border-slate-200 dark:border-border-dark hover:bg-slate-50 dark:hover:bg-white/5 transition"
          aria-label="Next month"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18l6-6-6-6"/></svg>
        </button>
      </div>
      <button
        type="button"
        @click="goToToday"
        class="text-sm font-semibold px-3 py-1.5 rounded-xl border border-slate-200 dark:border-border-dark hover:bg-slate-50 dark:hover:bg-white/5 transition"
      >
        Today
      </button>
    </div>

    <p v-if="loading" class="text-slate-500">Loading timetable...</p>
    <p v-else-if="error" class="text-danger">{{ error }}</p>

    <template v-else>
      <!-- Full calendar grid (tablet & up) -->
      <div class="card p-0 overflow-hidden hidden sm:block">
        <div class="overflow-x-auto">
          <div class="min-w-[900px]">
            <div class="grid grid-cols-7 divide-x divide-slate-100 dark:divide-border-dark border-b border-slate-100 dark:border-border-dark">
              <div
                v-for="label in WEEKDAY_LABELS"
                :key="label"
                class="px-3 py-3 text-center font-display font-bold text-sm bg-slate-50 dark:bg-white/5"
              >
                {{ label }}
              </div>
            </div>

            <div
              v-for="(week, wIdx) in weeks"
              :key="wIdx"
              class="grid grid-cols-7 divide-x divide-slate-100 dark:divide-border-dark border-b last:border-b-0 border-slate-100 dark:border-border-dark"
            >
              <div
                v-for="cell in week"
                :key="cell.iso"
                class="min-h-[130px] p-2 flex flex-col gap-1.5"
                :class="!cell.inMonth ? 'bg-slate-50/60 dark:bg-white/[0.02]' : ''"
              >
                <div class="flex justify-end">
                  <span
                    class="text-xs font-semibold w-6 h-6 flex items-center justify-center rounded-full"
                    :class="[
                      cell.isToday ? 'bg-brand-blue text-white' : (cell.inMonth ? 'text-ink dark:text-slate-200' : 'text-slate-300 dark:text-slate-600')
                    ]"
                  >
                    {{ cell.date.getDate() }}
                  </span>
                </div>

                <div v-if="cell.inMonth" class="space-y-1 overflow-y-auto">
                  <div
                    v-for="c in sessionsFor(cell.iso).slice(0, 3)"
                    :key="c.session_id ?? `${cell.iso}-${c.time}-${c.subject}`"
                    class="rounded-lg bg-slate-50 dark:bg-white/5 p-1.5"
                    :title="`${c.subject || 'Subject'} · ${c.time || ''} · ${c.tutor || 'Tutor'}`"
                  >
                    <p class="font-semibold text-[11px] truncate">{{ c.subject || 'Subject' }}</p>
                    <p class="text-[10px] text-slate-500 truncate">{{ c.time || '--' }}</p>
                  </div>
                  <p v-if="sessionsFor(cell.iso).length > 3" class="text-[10px] text-slate-400 pl-1">
                    +{{ sessionsFor(cell.iso).length - 3 }} more
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Agenda list (small screens) -->
      <div class="sm:hidden space-y-4">
        <template v-for="week in weeks" :key="`m-${week[0].iso}`">
          <div
            v-for="cell in week.filter(c => c.inMonth)"
            :key="`m-${cell.iso}`"
            class="card p-4"
          >
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-display font-bold">
                {{ cell.date.toLocaleDateString(undefined, { weekday: 'long', day: 'numeric', month: 'short' }) }}
              </h3>
              <span v-if="cell.isToday" class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-brand-blue/10 text-brand-blue">Today</span>
            </div>
            <p v-if="!sessionsFor(cell.iso).length" class="text-sm text-slate-400">No session.</p>
            <div
              v-for="c in sessionsFor(cell.iso)"
              :key="c.session_id ?? `${cell.iso}-m-${c.time}`"
              class="rounded-xl bg-slate-50 dark:bg-white/5 p-3 mb-2"
            >
              <div class="flex items-center justify-between gap-2">
                <p class="font-semibold">{{ c.subject || 'Subject' }}</p>
                <StatusBadge v-if="c.status" :status="c.status" />
              </div>
              <p class="text-sm text-slate-500">{{ c.time || '--' }}</p>
              <p class="text-xs text-slate-500">{{ c.tutor || 'Tutor' }}</p>
            </div>
          </div>
        </template>
      </div>
    </template>
  </div>
</template>
