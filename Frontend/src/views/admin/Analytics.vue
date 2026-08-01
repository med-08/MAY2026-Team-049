<script setup>
import { ref, onMounted } from 'vue'
import { Doughnut, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Filler
} from 'chart.js'

import { adminApi } from '../../services/adminApi'
import EmptyState from '../../components/ui/EmptyState.vue'

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Filler
)

const loading = ref(true)
const error = ref(null)
const subjectData = ref([]) // [{ subject, count }]
const monthlyData = ref([]) // [{ month, year, count }]

async function loadAnalytics() {
  loading.value = true
  error.value = null
  try {
    const [subjectsRes, monthlyRes] = await Promise.all([
      adminApi.getStudentsPerSubject(),
      adminApi.getMonthlyRegistrations(7)
    ])
    subjectData.value = subjectsRes.data
    monthlyData.value = monthlyRes.data
  } catch (e) {
    error.value = e.message || 'Failed to load analytics.'
  } finally {
    loading.value = false
  }
}

onMounted(loadAnalytics)

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
</script>
<template>
  <div>
    <div class="mb-5">
      <h2 class="text-xl font-display font-bold text-slate-800 dark:text-slate-100">
        Analytics
      </h2>

      <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
        A quick pulse on subject demand and enrollment trends.
      </p>
    </div>

    <EmptyState
      v-if="error"
      title="Couldn't load analytics"
      :message="error"
    />

    <!-- Charts One Below Another -->
    <div
      v-else
      class="space-y-6"
    >

      <!-- Doughnut Chart -->
      <div class="card p-5">
        <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">
          Students Per Subject
        </h3>

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

    </div>
  </div>
</template>