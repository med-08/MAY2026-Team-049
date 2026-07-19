<template>
  <div class="card glass reveal">
    <div class="ch"><h3>Monthly calendar</h3><span class="eyebrow">July 2026</span></div>
    <div class="cal-grid">
      <div v-for="day in dayNames" :key="day" class="hd">{{ day }}</div>
      <button
        v-for="day in days"
        :key="day.key"
        type="button"
        class="cal-day"
        :class="{ on: selectedDate === day.date, muted: !day.date }"
        @click="day.date && $emit('select-date', day.date)"
      >
        <span class="mono">{{ day.label }}</span>
        <span v-for="event in eventsFor(day.date)" :key="event.eventId" class="cal-badge" :class="eventClass(event.type)">{{ event.title }}</span>
      </button>
    </div>
    <div class="cal-legend">
      <span v-for="type in eventTypes" :key="type" class="badge" :class="eventClass(type)">{{ type }}</span>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  events: { type: Array, required: true },
  selectedDate: { type: String, required: true }
})
defineEmits(['select-date'])

const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const eventTypes = ['Class', 'Holiday', 'Exam', 'Cancelled Class', 'Meeting']
const days = [
  ...Array.from({ length: 3 }, (_, index) => ({ key: `blank-${index}`, label: '', date: '' })),
  ...Array.from({ length: 31 }, (_, index) => {
    const day = String(index + 1).padStart(2, '0')
    return { key: day, label: index + 1, date: `2026-07-${day}` }
  })
]
function eventsFor(date) {
  return props.events.filter((event) => event.date === date)
}
function eventClass(type) {
  return {
    Class: 'done',
    Holiday: '',
    Exam: 'live',
    'Cancelled Class': 'warn',
    Meeting: 'meeting'
  }[type] || ''
}
</script>
