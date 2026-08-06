<template>
  <div class="areachart">
    <svg viewBox="0 0 320 92" style="color:var(--lime)">
      <defs>
        <linearGradient :id="uid" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="currentColor" stop-opacity=".32" />
          <stop offset="1" stop-color="currentColor" stop-opacity="0" />
        </linearGradient>
      </defs>
      <path :d="areaPath" :fill="`url(#${uid})`" />
      <path ref="lineRef" class="cl" :d="linePath" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" />
      <circle v-for="point in points" :key="point.join('-')" :cx="point[0]" :cy="point[1]" r="2.6" fill="var(--solid)" stroke="currentColor" stroke-width="2" />
    </svg>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'

const props = defineProps({
  data: { type: Array, required: true },
  activeKey: { type: String, default: '' },
  reduceMotion: { type: Boolean, default: false }
})

const uid = `ac${Math.random().toString(36).slice(2, 7)}`
const lineRef = ref(null)
const points = computed(() => {
  const w = 320
  const h = 92
  const pad = 8
  const max = Math.max(...props.data)
  const min = Math.min(...props.data)
  return props.data.map((value, index) => [
    pad + index * ((w - 2 * pad) / (props.data.length - 1)),
    h - pad - ((value - min) / ((max - min) || 1)) * (h - 2 * pad - 6)
  ])
})
const linePath = computed(() => {
  const pts = points.value
  let d = `M${pts[0][0]} ${pts[0][1]}`
  for (let i = 1; i < pts.length; i++) {
    const xc = (pts[i - 1][0] + pts[i][0]) / 2
    const yc = (pts[i - 1][1] + pts[i][1]) / 2
    d += ` Q${pts[i - 1][0]} ${pts[i - 1][1]} ${xc} ${yc}`
  }
  d += ` T${pts[pts.length - 1][0]} ${pts[pts.length - 1][1]}`
  return d
})
const areaPath = computed(() => {
  const pts = points.value
  return `${linePath.value} L${pts[pts.length - 1][0]} 92 L${pts[0][0]} 92 Z`
})

function animateLine() {
  const line = lineRef.value
  if (!line || props.reduceMotion || !line.getTotalLength) return
  const length = line.getTotalLength()
  line.style.strokeDasharray = length
  line.style.strokeDashoffset = length
  line.getBoundingClientRect()
  line.style.transition = 'stroke-dashoffset 1.1s cubic-bezier(.4,0,.2,1)'
  line.style.strokeDashoffset = 0
}

onMounted(animateLine)
watch(() => props.activeKey, animateLine)
</script>
