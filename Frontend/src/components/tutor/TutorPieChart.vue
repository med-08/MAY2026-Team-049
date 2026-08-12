<template>
  <div class="pie-wrap">
    <svg viewBox="0 0 86 86" class="pie">
      <circle cx="43" cy="43" r="30" fill="none" stroke="var(--border)" stroke-width="12" />
      <circle
        v-for="slice in slices"
        :key="slice.label"
        cx="43"
        cy="43"
        r="30"
        fill="none"
        :stroke="slice.color"
        stroke-width="12"
        stroke-linecap="round"
        :stroke-dasharray="`${slice.value} ${100 - slice.value}`"
        :stroke-dashoffset="slice.offset"
        transform="rotate(-90 43 43)"
      />
      <text x="43" y="40" text-anchor="middle" class="pie-main">{{ overall }}%</text>
      <text x="43" y="54" text-anchor="middle" class="pie-sub">Overall</text>
    </svg>
    <div>
      <div v-for="item in data" :key="item.label" class="row" style="padding:7px 0">
        <span class="nd" :style="{ background: item.color }"></span><div class="g1"><div class="t" style="font-size:12.5px">{{ item.label }}</div></div><span class="mono" style="font-size:12px">{{ item.value }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ data: { type: Array, required: true } })
const overall = computed(() => props.data.find((item) => item.label === 'Present')?.value || 0)
const slices = computed(() => {
  let offset = 0
  return props.data.map((item) => {
    const slice = { ...item, offset: -offset }
    offset += item.value
    return slice
  })
})
</script>
