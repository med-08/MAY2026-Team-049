<template>
  <section class="view on">
    <TutorMonthlyCalendar :events="events" :selected-date="selectedDate" @select-date="selectedDate = $event" />
    <div class="card glass reveal">
      <div class="ch"><h3>Weekly schedule</h3><div style="display:flex;gap:8px"><button class="btn sm" type="button" @click="$emit('toast', 'Pick a slot to reschedule')">Reschedule</button><button class="btn grad sm magnetic" type="button" @click="$emit('toast', 'New class added to schedule')">+ Add class</button></div></div>
      <div class="eyebrow" style="margin-bottom:14px">Selected date · {{ selectedDate }} · tuition hours · 4:00–7:00 PM · reminders auto-sent 1h before</div>
      <div class="tt">
        <div class="hd"></div><div v-for="day in days" :key="day" class="hd">{{ day }}</div>
        <template v-for="row in rows" :key="row.time">
          <div class="tm">{{ row.time }}</div>
          <button v-for="(cell, index) in row.days" :key="`${row.time}-${index}`" class="cell" :class="cell ? 'on' : 'free'" type="button" @click="!cell && $emit('toast', 'New class added to schedule')">
            <template v-if="cell"><div class="t">{{ cell.t }}</div><div class="s">{{ cell.s }}</div></template>
            <template v-else>+</template>
          </button>
        </template>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import TutorMonthlyCalendar from '../../components/tutor/TutorMonthlyCalendar.vue'

defineProps({
  rows: { type: Array, required: true },
  events: { type: Array, required: true }
})
defineEmits(['toast'])
const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const selectedDate = ref('2026-07-10')
</script>
