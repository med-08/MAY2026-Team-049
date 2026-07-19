<template>
  <aside ref="railRef" class="rail glass" :class="{ open: mobileOpen }">
    <div class="brand">
      <span class="mk"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9.5 12 4l9 5.5-9 5.5-9-5.5Z"/><path d="M6.5 11.5V16c0 1 2.5 2.5 5.5 2.5s5.5-1.5 5.5-2.5v-4.5"/></svg></span>
      <span class="nm">Learn<b>AtHome</b></span>
    </div>
    <div ref="navWrapRef" class="navwrap">
      <div class="nav-pill" :style="pillStyle"></div>
      <template v-for="group in groups" :key="group.label">
        <div class="navlbl">{{ group.label }}</div>
        <button
          v-for="item in group.items"
          :key="item.id"
          :ref="(el) => setNavRef(item.id, el)"
          class="nav"
          :class="{ on: activeView === item.id }"
          type="button"
          @click="$emit('navigate', item.id)"
        >
          <TutorIconSvg :path="item.icon" />
          {{ item.label }}
          <span v-if="badgeCount(item)" class="cnt">{{ badgeCount(item) }}</span>
        </button>
      </template>
    </div>
    <div class="rail-foot">
      <button class="nav" type="button" @click="$emit('toggle-theme')">
        <svg viewBox="0 0 24 24" v-html="themeIcon"></svg><span>{{ themeLabel }}</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, reactive, watch } from 'vue'
import TutorIconSvg from './TutorIconSvg.vue'

const props = defineProps({
  groups: { type: Array, required: true },
  activeView: { type: String, required: true },
  mobileOpen: { type: Boolean, required: true },
  dark: { type: Boolean, required: true },
  counts: { type: Object, default: () => ({}) }
})

defineEmits(['navigate', 'toggle-theme'])

const navRefs = new Map()
const pill = reactive({ top: 0, height: 42 })
const themeIcon = computed(() => props.dark
  ? '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 19 19M19 5l-1.5 1.5M6.5 17.5 5 19"/>'
  : '<path d="M20 14.5A8 8 0 0 1 9.5 4 7 7 0 1 0 20 14.5Z"/>')
const themeLabel = computed(() => props.dark ? 'Light mode' : 'Dark mode')
const pillStyle = computed(() => ({ transform: `translateY(${pill.top}px)`, height: `${pill.height}px` }))

function setNavRef(id, el) {
  if (el) navRefs.set(id, el)
}

function badgeCount(item) {
  if (item.countKey) return props.counts[item.countKey]
  return item.count
}

function movePill() {
  nextTick(() => {
    const el = navRefs.get(props.activeView)
    if (!el) return
    pill.top = el.offsetTop
    pill.height = el.offsetHeight
  })
}

watch(() => props.activeView, movePill)
onMounted(() => {
  movePill()
  window.addEventListener('resize', movePill)
})
onUnmounted(() => window.removeEventListener('resize', movePill))
</script>
