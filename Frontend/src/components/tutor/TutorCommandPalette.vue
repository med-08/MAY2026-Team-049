<template>
  <div ref="scrimRef" class="cmd-scrim" :class="{ on: open }" @click="onScrimClick">
    <div class="cmd glass">
      <div class="cmd-in">
        <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <input ref="inputRef" v-model="query" placeholder="Search or jump to..." autocomplete="off" @keydown="onKeydown">
        <span class="kbd">esc</span>
      </div>
      <div class="cmd-list">
        <button
          v-for="(item, index) in filtered"
          :key="item.l"
          class="cmd-item"
          :class="{ sel: index === selectedIndex }"
          type="button"
          @mousemove="selectedIndex = index"
          @click="run(item)"
        >
          <svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
          <span>{{ item.l }}</span><span class="rk">{{ item.a ? 'action' : 'jump' }}</span>
        </button>
        <div v-if="!filtered.length" class="cmd-empty">No matches</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, required: true },
  items: { type: Array, required: true }
})

const emit = defineEmits(['close', 'run'])
const inputRef = ref(null)
const scrimRef = ref(null)
const query = ref('')
const selectedIndex = ref(0)
const filtered = computed(() => props.items.filter((item) => item.l.toLowerCase().includes(query.value.toLowerCase())))

function run(item) {
  if (item) emit('run', item)
}

function onScrimClick(event) {
  if (event.target === scrimRef.value) emit('close')
}

function onKeydown(event) {
  if (event.key === 'Escape') emit('close')
  if (event.key === 'ArrowDown') {
    event.preventDefault()
    selectedIndex.value = Math.min(selectedIndex.value + 1, filtered.value.length - 1)
  }
  if (event.key === 'ArrowUp') {
    event.preventDefault()
    selectedIndex.value = Math.max(selectedIndex.value - 1, 0)
  }
  if (event.key === 'Enter') run(filtered.value[selectedIndex.value])
}

function onGlobalKeydown(event) {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
    event.preventDefault()
    props.open ? emit('close') : emit('run', { a: 'open-command' })
  }
}

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    query.value = ''
    selectedIndex.value = 0
    nextTick(() => setTimeout(() => inputRef.value?.focus(), 60))
  }
})

watch(query, () => { selectedIndex.value = 0 })
onMounted(() => document.addEventListener('keydown', onGlobalKeydown))
onUnmounted(() => document.removeEventListener('keydown', onGlobalKeydown))
</script>
