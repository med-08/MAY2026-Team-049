<script setup>
import { Line } from "vue-chartjs"
import { Chart as ChartJS, LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Filler } from "chart.js"

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Filler)

const props = defineProps({
  labels: Array,
  data: Array,
})

const chartData = {
  labels: props.labels,
  datasets: [
    {
      label: "Quiz Average (%)",
      data: props.data,
      borderColor: "#2454ff",
      backgroundColor: "rgba(36,84,255,0.12)",
      pointBackgroundColor: "#14b877",
      pointBorderColor: "#ffffff",
      pointRadius: 5,
      pointHoverRadius: 6,
      borderWidth: 3,
      fill: true,
      tension: 0.35,
    },
  ],
}

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { beginAtZero: true, max: 100, grid: { color: "rgba(148,163,184,0.15)" }, ticks: { color: "#94a3b8" } },
    x: { grid: { display: false }, ticks: { color: "#94a3b8" } },
  },
}
</script>

<template>
  <div class="h-64">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>
