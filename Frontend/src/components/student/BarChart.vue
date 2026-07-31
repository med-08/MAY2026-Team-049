<script setup>
import { Bar } from "vue-chartjs"
import { Chart as ChartJS, BarElement, LinearScale, CategoryScale, Tooltip } from "chart.js"

ChartJS.register(BarElement, LinearScale, CategoryScale, Tooltip)

const props = defineProps({
  labels: Array,
  data: Array,
})

const chartData = {
  labels: props.labels,
  datasets: [
    {
      label: "Score (%)",
      data: props.data,
      backgroundColor: ["#2454ff", "#14b877", "#2454ff", "#14b877"],
      borderRadius: 8,
      maxBarThickness: 46,
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
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>
