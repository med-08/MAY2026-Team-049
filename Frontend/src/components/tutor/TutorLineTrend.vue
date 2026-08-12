<template>
  <div class="mini-chart">
    <svg viewBox="0 0 220 82" aria-label="Performance trend">
      <defs>
        <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="var(--g2)" stop-opacity=".22" />
          <stop offset="1" stop-color="var(--g2)" stop-opacity="0" />
        </linearGradient>
      </defs>
      <path :d="areaPath" fill="url(#trendFill)" />
      <path :d="linePath" fill="none" stroke="var(--g2)" stroke-width="2.4" stroke-linecap="round" />
      <circle v-for="point in points" :key="point.join('-')" :cx="point[0]" :cy="point[1]" r="3" fill="var(--solid)" stroke="var(--g2)" stroke-width="2" />
    </svg>
    <div class="trend-labels"><span v-for="(score, index) in scores" :key="index">Week {{ index + 1 }}</span></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ scores: { type: Array, required: true } })

const points = computed(() => {
  const max = Math.max(...props.scores)
  const min = Math.min(...props.scores)
  return props.scores.map((score, index) => [
    10 + index * (200 / Math.max(props.scores.length - 1, 1)),
    70 - ((score - min) / ((max - min) || 1)) * 52
  ])
})

const linePath = computed(() => points.value.map((point, index) => `${index ? 'L' : 'M'}${point[0]} ${point[1]}`).join(' '))
const areaPath = computed(() => `${linePath.value} L${points.value.at(-1)[0]} 78 L${points.value[0][0]} 78 Z`)
</script>
