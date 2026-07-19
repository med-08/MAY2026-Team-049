<template>
  <section class="view on">
    <div class="grid g2col reveal" style="grid-template-columns:1fr 1fr">
      <div class="card glass">
        <div class="ch"><h3>Attendance</h3><span class="badge live">Maths · 4:00 PM</span></div>
        <div v-for="record in records" :key="record.attendanceId" class="row">
          <div class="av" :style="{ background: studentById(record.studentId).gradient }">{{ studentById(record.studentId).initials }}</div>
          <div class="g1"><div class="t">{{ studentById(record.studentId).name }}</div></div>
          <TutorAttendanceToggle v-model="record.status" :name="studentById(record.studentId).name" />
        </div>
        <div class="eyebrow" style="margin-top:14px">Parents are notified automatically</div>
        <div style="display:flex;gap:8px;margin-top:14px"><button class="btn sm" type="button" @click="$emit('toast', 'Attendance CSV exported')">Export CSV</button><button class="btn sm" type="button" @click="$emit('toast', 'Attendance PDF exported')">Export PDF</button></div>
      </div>
      <div class="card glass">
        <div class="ch"><h3>Attendance analytics</h3><span class="eyebrow">this month</span></div>
        <TutorPieChart :data="analytics" />
      </div>
      <div class="card glass">
        <div class="ch"><h3>Session update</h3></div>
        <label class="lab" for="topics">Topics covered</label><input id="topics" class="field" style="margin-bottom:12px" placeholder="Quadratic equations — factorisation">
        <label class="lab" for="homework">Homework</label><input id="homework" class="field" style="margin-bottom:12px" placeholder="Exercise 4.2 · Q1–Q10">
        <label class="lab" for="next-session">Next session</label><input id="next-session" class="field" style="margin-bottom:16px" placeholder="Wed, 4:00 PM">
        <button class="btn grad magnetic" type="button" style="width:100%;justify-content:center" @click="$emit('toast', 'Update sent · parents & students notified')">Send update to parents &amp; students</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import TutorAttendanceToggle from '../../components/tutor/TutorAttendanceToggle.vue'
import TutorPieChart from '../../components/tutor/TutorPieChart.vue'

const props = defineProps({
  records: { type: Array, required: true },
  students: { type: Array, required: true },
  analytics: { type: Array, required: true }
})
defineEmits(['toast'])
function studentById(id) {
  return props.students.find((student) => student.studentId === id) || props.students[0]
}
</script>
