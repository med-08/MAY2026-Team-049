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
  CheckBadgeIcon
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
const subjectData = ref([]) // [{ subject, count }] -- student demand
const monthlyData = ref([]) // [{ month, year, count }]
const statusData = ref([]) // [{ type, active, blocked, pending }]

async function loadAnalytics() {
  loading.value = true
  error.value = null
  try {
    const [subjectsRes, monthlyRes, statusRes] = await Promise.all([
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

// ---- Insight: overall approval rate across Students/Tutors/Parents ----
const approvalRateInsight = computed(() => {
  if (!statusData.value.length) return null
  const decided = statusData.value.reduce((sum, s) => sum + s.active + s.blocked, 0)
  const active = statusData.value.reduce((sum, s) => sum + s.active, 0)
  if (decided === 0) return null
  return Math.round((active / decided) * 100)
})

const doughnutData = () => ({
  labels: subjectData.value.map((s) => s.subject),
  datasets: [
    {
      data: subjectData.value.map((s) => s.count),
      backgroundColor: [
        '#60A5FA',
        '#34D399',
        '#8b5cf6'
      ],
      borderWidth: 0,
      hoverOffset: 6
    }
  ]
})

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '65%',
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        padding: 18,
        font: {
          family: 'Inter',
          size: 12
        }
      }
    }
  }
}

const lineData = () => {
  const grad = {
    top: 'rgba(16,185,129,0.28)',
    bottom: 'rgba(16,185,129,0)'
  }

  return {
    labels: monthlyData.value.map((m) => m.month),
    datasets: [
      {
        label: 'New Registrations',
        data: monthlyData.value.map((m) => m.count),
        borderColor: '#10b981',

        backgroundColor: (ctx) => {
          const chart = ctx.chart
          const { ctx: c, chartArea } = chart

          if (!chartArea) return grad.bottom

          const gradient = c.createLinearGradient(
            0,
            chartArea.top,
            0,
            chartArea.bottom
          )

          gradient.addColorStop(0, grad.top)
          gradient.addColorStop(1, grad.bottom)

          return gradient
        },

        tension: 0.4,
        fill: true,
        pointBackgroundColor: '#10b981',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 4
      }
    ]
  }
}

const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    x: {
      grid: {
        display: false
      }
    },
    y: {
      beginAtZero: true,
      grid: {
        color: 'rgba(148,163,184,0.15)'
      }
    }
  }
}

// ---- Account Status Breakdown (stacked bar) ----
const statusBarData = () => ({
  labels: statusData.value.map((s) => s.type),
  datasets: [
    {
      label: 'Active',
      data: statusData.value.map((s) => s.active),
      backgroundColor: '#34D399',
      borderRadius: 4,
      maxBarThickness: 48
    },
    {
      label: 'Pending',
      data: statusData.value.map((s) => s.pending),
      backgroundColor: '#FBBF24',
      borderRadius: 4,
      maxBarThickness: 48
    },
    {
      label: 'Blocked',
      data: statusData.value.map((s) => s.blocked),
      backgroundColor: '#F87171',
      borderRadius: 4,
      maxBarThickness: 48
    }
  ]
})

const statusBarOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        padding: 18,
        font: { family: 'Inter', size: 12 }
      }
    }
  },
  scales: {
    x: { stacked: true, grid: { display: false } },
    y: {
      stacked: true,
      beginAtZero: true,
      ticks: { precision: 0 },
      grid: { color: 'rgba(148,163,184,0.15)' }
    }
  }
}
</script>
<template>
  <div>
    <div class="mb-5">
      <h2 class="text-xl font-display font-bold text-slate-800 dark:text-slate-100">
        Analytics
      </h2>

      <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
        A quick pulse on subject demand, enrollment trends, and account standing.
      </p>
    </div>

    <EmptyState
      v-if="error"
      title="Couldn't load analytics"
      :message="error"
    />

    <div v-else class="space-y-6">

      <!-- Insight Callouts -->
      <div
        v-if="!loading"
        class="grid grid-cols-1 gap-4 sm:grid-cols-2"
      >
        <div
          v-if="approvalRateInsight !== null"
          class="card p-5 flex items-start gap-4"
        >
          <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 dark:bg-emerald-500/20 dark:text-emerald-300">
            <CheckBadgeIcon class="h-5 w-5" />
          </div>
          <div>
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Account Standing
            </p>
            <p class="mt-1 text-sm text-slate-700 dark:text-slate-200">
              <span class="font-semibold">{{ approvalRateInsight }}%</span>
              of decided registrations (students, tutors & parents) are currently Active rather than Blocked.
            </p>
          </div>
        </div>

        <div
          v-if="approvalRateInsight === null"
          class="card p-5 flex items-start gap-4 sm:col-span-2"
        >
          <div class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-sky-100 text-sky-600 dark:bg-sky-500/20 dark:text-sky-300">
            <UserGroupIcon class="h-5 w-5" />
          </div>
          <p class="mt-1 text-sm text-slate-700 dark:text-slate-200">
            Not enough data yet to surface insights — check back once more students, tutors, and parents have registered.
          </p>
        </div>
      </div>

      <!-- Charts -->
      <div class="grid grid-cols-1 gap-6 xl:grid-cols-2">

        <!-- Doughnut Chart -->
        <div class="card p-5">
          <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">
            Students Per Subject
          </h3>
          <p class="text-xs text-slate-400 -mt-3 mb-4">Enrollment demand by subject.</p>

          <div class="h-72">
            <div
              v-if="loading"
              class="h-full w-full animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800"
            />
            <Doughnut
              v-else
              :data="doughnutData()"
              :options="doughnutOptions"
            />
          </div>
        </div>

        <!-- Line Chart -->
        <div class="card p-5">
          <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">
            Monthly Student Registration
          </h3>
          <p class="text-xs text-slate-400 -mt-3 mb-4">New registrations across the platform, last 7 months.</p>

          <div class="h-72">
            <div
              v-if="loading"
              class="h-full w-full animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800"
            />
            <Line
              v-else
              :data="lineData()"
              :options="lineOptions"
            />
          </div>
        </div>

        <!-- Status Breakdown Stacked Bar -->
        <div class="card p-5">
          <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">
            Account Status Breakdown
          </h3>
          <p class="text-xs text-slate-400 -mt-3 mb-4">Active vs. Pending vs. Blocked, by user type.</p>

          <div class="h-72">
            <div
              v-if="loading"
              class="h-full w-full animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800"
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