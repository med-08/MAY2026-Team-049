<script setup>
import { ref, computed, onMounted } from 'vue'
import { Doughnut, Line, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Filler
} from 'chart.js'

import {
  UserGroupIcon,
  CheckBadgeIcon,
  ChartBarIcon,
  AcademicCapIcon,
  ArrowTrendingUpIcon
} from '@heroicons/vue/24/outline'

import { adminApi } from '../../services/adminApi'
import EmptyState from '../../components/ui/EmptyState.vue'

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Filler
)

const loading = ref(true)
const error = ref(null)

const subjectData = ref([])
const monthlyData = ref([])
const statusData = ref([])

async function loadAnalytics() {
  loading.value = true
  error.value = null

  try {
    const [
      subjectsRes,
      monthlyRes,
      statusRes
    ] = await Promise.all([
      adminApi.getStudentsPerSubject(),
      adminApi.getMonthlyRegistrations(7),
      adminApi.getStatusBreakdown()
    ])

    subjectData.value = subjectsRes.data
    monthlyData.value = monthlyRes.data
    statusData.value = statusRes.data
  } catch (e) {
    error.value = e.message || 'Failed to load analytics.'
  } finally {
    loading.value = false
  }
}

onMounted(loadAnalytics)

/* -----------------------------
   Insights
----------------------------- */

const approvalRateInsight = computed(() => {
  if (!statusData.value.length) return null

  const decided = statusData.value.reduce(
    (sum, s) => sum + s.active + s.blocked,
    0
  )

  const active = statusData.value.reduce(
    (sum, s) => sum + s.active,
    0
  )

  if (decided === 0) return null

  return Math.round((active / decided) * 100)
})

const totalSubjectStudents = computed(() => {
  return subjectData.value.reduce(
    (sum, item) => sum + item.count,
    0
  )
})

const topSubject = computed(() => {
  if (!subjectData.value.length) return null

  return [...subjectData.value].sort(
    (a, b) => b.count - a.count
  )[0]
})

/* -----------------------------
   Doughnut Chart
----------------------------- */

const doughnutData = () => ({
  labels: subjectData.value.map(
    (s) => s.subject
  ),

  datasets: [
    {
      data: subjectData.value.map(
        (s) => s.count
      ),

      backgroundColor: [
        '#60A5FA',
        '#34D399',
        '#8B5CF6',
        '#F59E0B',
        '#F87171',
        '#2DD4BF',
        '#A78BFA',
        '#38BDF8'
      ],

      borderWidth: 0,
      hoverOffset: 7
    }
  ]
})

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,

  cutout: '68%',

  plugins: {
    legend: {
      position: 'bottom',

      labels: {
        usePointStyle: true,
        pointStyle: 'circle',
        padding: 18,

        font: {
          family: 'Inter',
          size: 12
        }
      }
    },

    tooltip: {
      padding: 10,
      displayColors: true
    }
  }
}

/* -----------------------------
   Registration Line Chart
----------------------------- */

const lineData = () => {
  const grad = {
    top: 'rgba(16,185,129,0.25)',
    bottom: 'rgba(16,185,129,0)'
  }

  return {
    labels: monthlyData.value.map(
      (m) => m.month
    ),

    datasets: [
      {
        label: 'New Registrations',

        data: monthlyData.value.map(
          (m) => m.count
        ),

        borderColor: '#10b981',

        backgroundColor: (ctx) => {
          const chart = ctx.chart
          const { ctx: c, chartArea } = chart

          if (!chartArea) {
            return grad.bottom
          }

          const gradient = c.createLinearGradient(
            0,
            chartArea.top,
            0,
            chartArea.bottom
          )

          gradient.addColorStop(
            0,
            grad.top
          )

          gradient.addColorStop(
            1,
            grad.bottom
          )

          return gradient
        },

        tension: 0.4,
        fill: true,

        pointBackgroundColor: '#10b981',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6
      }
    ]
  }
}

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,

  interaction: {
    intersect: false,
    mode: 'index'
  },

  plugins: {
    legend: {
      display: false
    },

    tooltip: {
      padding: 10
    }
  },

  scales: {
    x: {
      grid: {
        display: false
      },

      ticks: {
        color: '#94a3b8',
        font: {
          size: 11
        }
      }
    },

    y: {
      beginAtZero: true,

      ticks: {
        precision: 0,
        color: '#94a3b8',
        font: {
          size: 11
        }
      },

      grid: {
        color: 'rgba(148,163,184,0.12)'
      }
    }
  }
}

/* -----------------------------
   Account Status Breakdown
----------------------------- */

const statusBarData = () => ({
  labels: statusData.value.map(
    (s) => s.type
  ),

  datasets: [
    {
      label: 'Active',

      data: statusData.value.map(
        (s) => s.active
      ),

      backgroundColor: '#34D399',
      borderRadius: 5,
      maxBarThickness: 48
    },

    {
      label: 'Pending',

      data: statusData.value.map(
        (s) => s.pending
      ),

      backgroundColor: '#FBBF24',
      borderRadius: 5,
      maxBarThickness: 48
    },

    {
      label: 'Blocked',

      data: statusData.value.map(
        (s) => s.blocked
      ),

      backgroundColor: '#F87171',
      borderRadius: 5,
      maxBarThickness: 48
    }
  ]
})

const statusBarOptions = {
  responsive: true,
  maintainAspectRatio: false,

  interaction: {
    intersect: false,
    mode: 'index'
  },

  plugins: {
    legend: {
      position: 'bottom',

      labels: {
        usePointStyle: true,
        pointStyle: 'circle',
        padding: 18,

        font: {
          family: 'Inter',
          size: 12
        }
      }
    },

    tooltip: {
      padding: 10
    }
  },

  scales: {
    x: {
      stacked: true,

      grid: {
        display: false
      },

      ticks: {
        color: '#94a3b8',
        font: {
          size: 11
        }
      }
    },

    y: {
      stacked: true,
      beginAtZero: true,

      ticks: {
        precision: 0,
        color: '#94a3b8',
        font: {
          size: 11
        }
      },

      grid: {
        color: 'rgba(148,163,184,0.12)'
      }
    }
  }
}
</script>

<template>
  <div class="space-y-7">

    <!-- Header -->
    <div
      class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between"
    >
      <div>
        <div class="flex items-center gap-3">

          <div
            class="flex h-11 w-11 items-center justify-center rounded-xl bg-sky-100 text-sky-600 shadow-sm dark:bg-sky-500/10 dark:text-sky-400"
          >
            <ChartBarIcon class="h-6 w-6" />
          </div>

          <div>
            <p
              class="text-[11px] font-bold uppercase tracking-[0.16em] text-sky-600 dark:text-sky-400"
            >
              Platform Insights
            </p>

            <h2
              class="text-2xl font-display font-bold tracking-tight text-slate-800 dark:text-slate-100 sm:text-3xl"
            >
              Analytics
            </h2>
          </div>

        </div>

        <p
          class="mt-2 max-w-2xl text-sm leading-6 text-slate-500 dark:text-slate-400"
        >
          A quick pulse on subject demand, enrollment
          trends, and account standing across LearnAtHome.
        </p>
      </div>

      <!-- Data indicator -->
      <div
        v-if="!loading"
        class="inline-flex w-fit items-center gap-2 rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-xs font-medium text-slate-500 shadow-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400"
      >
        <span
          class="h-2 w-2 rounded-full bg-emerald-500"
        />

        Live platform data
      </div>
    </div>

    <!-- Error -->
    <EmptyState
      v-if="error"
      title="Couldn't load analytics"
      :message="error"
    />

    <div
      v-else
      class="space-y-6"
    >

      <!-- Insight Cards -->
      <div
        v-if="loading"
        class="grid grid-cols-1 gap-4 md:grid-cols-2"
      >
        <div
          v-for="n in 2"
          :key="n"
          class="h-28 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800"
        />
      </div>

      <div
        v-else
        class="grid grid-cols-1 gap-4 md:grid-cols-2"
      >

        <!-- Account Standing -->
        <div
          class="group relative overflow-hidden rounded-2xl border border-emerald-100 bg-gradient-to-br from-emerald-50 to-white p-5 shadow-sm transition-shadow hover:shadow-md dark:border-emerald-500/10 dark:from-emerald-500/10 dark:to-slate-800"
        >
          <div
            class="absolute -right-8 -top-8 h-28 w-28 rounded-full bg-emerald-200/30 blur-2xl dark:bg-emerald-500/10"
          />

          <div
            v-if="approvalRateInsight !== null"
            class="relative flex items-center gap-4"
          >
            <div
              class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-300"
            >
              <CheckBadgeIcon class="h-6 w-6" />
            </div>

            <div class="min-w-0">
              <p
                class="text-[11px] font-bold uppercase tracking-wider text-emerald-600 dark:text-emerald-400"
              >
                Account Standing
              </p>

              <p
                class="mt-1 text-sm leading-5 text-slate-700 dark:text-slate-200"
              >
                <span
                  class="text-2xl font-bold text-emerald-600 dark:text-emerald-400"
                >
                  {{ approvalRateInsight }}%
                </span>

                of decided registrations are currently active.
              </p>
            </div>
          </div>

          <div
            v-else
            class="relative flex items-center gap-4"
          >
            <div
              class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-sky-100 text-sky-600 dark:bg-sky-500/20 dark:text-sky-300"
            >
              <UserGroupIcon class="h-6 w-6" />
            </div>

            <p
              class="text-sm leading-5 text-slate-700 dark:text-slate-200"
            >
              Not enough account data yet to surface
              an account-standing insight.
            </p>
          </div>
        </div>

        <!-- Subject Demand -->
        <div
          class="group relative overflow-hidden rounded-2xl border border-sky-100 bg-gradient-to-br from-sky-50 to-white p-5 shadow-sm transition-shadow hover:shadow-md dark:border-sky-500/10 dark:from-sky-500/10 dark:to-slate-800"
        >
          <div
            class="absolute -right-8 -top-8 h-28 w-28 rounded-full bg-sky-200/30 blur-2xl dark:bg-sky-500/10"
          />

          <div
            v-if="topSubject"
            class="relative flex items-center gap-4"
          >
            <div
              class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-sky-100 text-sky-600 dark:bg-sky-500/20 dark:text-sky-300"
            >
              <AcademicCapIcon class="h-6 w-6" />
            </div>

            <div class="min-w-0">
              <p
                class="text-[11px] font-bold uppercase tracking-wider text-sky-600 dark:text-sky-400"
              >
                Leading Subject
              </p>

              <p
                class="mt-1 truncate text-lg font-bold text-slate-800 dark:text-slate-100"
              >
                {{ topSubject.subject }}
              </p>

              <p
                class="mt-0.5 text-xs text-slate-500 dark:text-slate-400"
              >
                {{ topSubject.count }} students across
                {{ subjectData.length }} subjects
              </p>
            </div>
          </div>

          <div
            v-else
            class="relative flex items-center gap-4"
          >
            <div
              class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-sky-100 text-sky-600 dark:bg-sky-500/20 dark:text-sky-300"
            >
              <AcademicCapIcon class="h-6 w-6" />
            </div>

            <p
              class="text-sm leading-5 text-slate-700 dark:text-slate-200"
            >
              Subject demand data will appear here
              once enrollment data is available.
            </p>
          </div>
        </div>
      </div>

      <!-- Charts -->
      <div
        class="grid grid-cols-1 gap-6 xl:grid-cols-2"
      >

        <!-- Students Per Subject -->
        <div
          class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-shadow hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
        >
          <div
            class="flex items-start justify-between border-b border-slate-100 px-5 py-4 dark:border-slate-700"
          >
            <div>
              <div class="flex items-center gap-2.5">

                <div
                  class="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-100 text-violet-600 dark:bg-violet-500/10 dark:text-violet-400"
                >
                  <UserGroupIcon class="h-4 w-4" />
                </div>

                <h3
                  class="font-display text-base font-semibold text-slate-800 dark:text-slate-100"
                >
                  Students Per Subject
                </h3>
              </div>

              <p
                class="mt-1 pl-10 text-xs text-slate-400"
              >
                Enrollment demand by subject.
              </p>
            </div>

            <span
              v-if="!loading && totalSubjectStudents"
              class="rounded-lg bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-500 dark:bg-slate-700/60 dark:text-slate-300"
            >
              {{ totalSubjectStudents }} total
            </span>
          </div>

          <div class="h-80 p-5">

            <div
              v-if="loading"
              class="h-full w-full animate-pulse rounded-xl bg-slate-100 dark:bg-slate-700/60"
            />

            <EmptyState
              v-else-if="!subjectData.length"
              title="No subject data"
              message="There is no subject enrollment data available yet."
            />

            <Doughnut
              v-else
              :data="doughnutData()"
              :options="doughnutOptions"
            />

          </div>
        </div>

        <!-- Monthly Registration -->
        <div
          class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-shadow hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
        >
          <div
            class="flex items-start justify-between border-b border-slate-100 px-5 py-4 dark:border-slate-700"
          >
            <div>
              <div class="flex items-center gap-2.5">

                <div
                  class="flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400"
                >
                  <ArrowTrendingUpIcon class="h-4 w-4" />
                </div>

                <h3
                  class="font-display text-base font-semibold text-slate-800 dark:text-slate-100"
                >
                  Monthly Registrations
                </h3>
              </div>

              <p
                class="mt-1 pl-10 text-xs text-slate-400"
              >
                New registrations across the last 7 months.
              </p>
            </div>

            <span
              class="hidden rounded-lg bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400 sm:inline-flex"
            >
              7 months
            </span>
          </div>

          <div class="h-80 p-5">

            <div
              v-if="loading"
              class="h-full w-full animate-pulse rounded-xl bg-slate-100 dark:bg-slate-700/60"
            />

            <EmptyState
              v-else-if="!monthlyData.length"
              title="No registration data"
              message="There is no monthly registration data available yet."
            />

            <Line
              v-else
              :data="lineData()"
              :options="lineOptions"
            />

          </div>
        </div>

        <!-- Status Breakdown -->
        <div
          class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-shadow hover:shadow-md dark:border-slate-700 dark:bg-slate-800 xl:col-span-2"
        >
          <div
            class="flex items-start justify-between border-b border-slate-100 px-5 py-4 dark:border-slate-700"
          >
            <div>
              <div class="flex items-center gap-2.5">

                <div
                  class="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100 text-amber-600 dark:bg-amber-500/10 dark:text-amber-400"
                >
                  <ChartBarIcon class="h-4 w-4" />
                </div>

                <h3
                  class="font-display text-base font-semibold text-slate-800 dark:text-slate-100"
                >
                  Account Status Breakdown
                </h3>
              </div>

              <p
                class="mt-1 pl-10 text-xs text-slate-400"
              >
                Active, pending, and blocked accounts by user type.
              </p>
            </div>
          </div>

          <div class="h-80 p-5">

            <div
              v-if="loading"
              class="h-full w-full animate-pulse rounded-xl bg-slate-100 dark:bg-slate-700/60"
            />

            <EmptyState
              v-else-if="!statusData.length"
              title="No account status data"
              message="There is no account status information available yet."
            />

            <Bar
              v-else
              :data="statusBarData()"
              :options="statusBarOptions"
            />

          </div>
        </div>

      </div>
    </div>
  </div>
</template>