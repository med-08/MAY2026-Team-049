<template>
  <div ref="tileRef" class="tile glass reveal" data-tilt>
    <div class="ti"><TutorIconSvg :path="icon" /></div>
    <div v-if="spark?.length" class="spark">
      <i v-for="height in spark" :key="height" :style="{ height: `${height}%` }"></i>
    </div>
    <div class="val">
      <slot name="prefix"></slot><span>{{ displayValue }}</span><slot name="suffix"></slot>
    </div>
    <div class="cap">{{ label }}</div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import TutorIconSvg from './TutorIconSvg.vue'

const props = defineProps({
  value: { type: Number, required: true },
  label: { type: String, required: true },
  icon: { type: String, required: true },
  spark: { type: Array, default: () => [] },
  activeKey: { type: String, default: '' },
  reduceMotion: { type: Boolean, default: false }
})

const displayValue = ref(0)
const tileRef = ref(null)
let frame = 0

function animate() {
  cancelAnimationFrame(frame)
  if (props.reduceMotion) {
    displayValue.value = props.value
    return
  }
  let start = null
  const duration = 900
  const step = (timestamp) => {
    start ||= timestamp
    const progress = Math.min((timestamp - start) / duration, 1)
    displayValue.value = Math.round(props.value * (1 - Math.pow(1 - progress, 3)))
    if (progress < 1) frame = requestAnimationFrame(step)
  }
  frame = requestAnimationFrame(step)
}

function onMouseMove(event) {
  if (props.reduceMotion || !tileRef.value) return
  const rect = tileRef.value.getBoundingClientRect()
  const px = (event.clientX - rect.left) / rect.width - 0.5
  const py = (event.clientY - rect.top) / rect.height - 0.5
  tileRef.value.style.transform = `perspective(720px) rotateX(${-py * 5}deg) rotateY(${px * 6}deg) translateY(-3px)`
}

function onMouseLeave() {
  if (tileRef.value) tileRef.value.style.transform = ''
}

onMounted(() => {
  animate()
  tileRef.value?.addEventListener('mousemove', onMouseMove)
  tileRef.value?.addEventListener('mouseleave', onMouseLeave)
})

watch(() => props.activeKey, animate)

onUnmounted(() => {
  cancelAnimationFrame(frame)
  tileRef.value?.removeEventListener('mousemove', onMouseMove)
  tileRef.value?.removeEventListener('mouseleave', onMouseLeave)
})
</script>
