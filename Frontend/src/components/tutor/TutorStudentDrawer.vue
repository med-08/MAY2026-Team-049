<template>
  <div class="drawer" :class="{ on: Boolean(student) }" role="dialog" aria-modal="true" aria-label="Student profile">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px">
      <div class="eyebrow">Student profile</div>
      <button class="icbtn glass" type="button" aria-label="Close student profile" @click="$emit('close')">
        <svg viewBox="0 0 24 24" stroke-width="2"><path d="M6 6l12 12M18 6 6 18"/></svg>
      </button>
    </div>
    <template v-if="student">
      <div style="display:flex;gap:14px;align-items:center;margin-bottom:20px">
        <div class="av" :style="{ width:'56px', height:'56px', fontSize:'18px', background: student.gradient }">{{ student.initials }}</div>
        <div><h2 style="font-size:20px;font-weight:600">{{ student.name }}</h2><div class="s" style="font-size:12.5px;color:var(--muted)">{{ student.classLevel }} · {{ student.subjects }}</div></div>
      </div>
      <label class="lab">Topic completion</label>
      <div style="height:9px;border-radius:5px;background:var(--border);overflow:hidden;margin-bottom:18px"><div :style="{ width: `${student.progress.completedTopics}%`, height:'100%', background:'linear-gradient(90deg,var(--g1),var(--g2))' }"></div></div>
      <label class="lab">Learning pace</label>
      <TutorSegmentedControl v-model="pace" :options="['Fast', 'Average', 'Needs practice']" style="margin-bottom:18px" />
      <label class="lab" for="remarks">Tutor remarks</label>
      <textarea id="remarks" v-model="remarks" class="field" rows="3" style="margin-bottom:18px;resize:vertical"></textarea>
      <label class="lab">Parent details</label>
      <div style="margin-bottom:18px">
        <div class="row"><div class="g1"><div class="t" style="font-size:13px">{{ student.parent.name }}</div><div class="s">Preferred · {{ student.parent.preferredContact }}</div></div></div>
        <div class="row"><div class="g1"><div class="t" style="font-size:13px">{{ student.parent.phone }}</div><div class="s">{{ student.parent.email }}</div></div></div>
      </div>
      <label class="lab">Performance trend</label>
      <TutorLineTrend :scores="student.weeklyScores" style="margin-bottom:18px" />
      <label class="lab">Recent quiz scores</label>
      <div style="margin:8px 0 18px">
        <div v-for="quiz in scores" :key="quiz.quizId" class="row">
          <div class="g1"><div class="t" style="font-size:13px">{{ quiz.title }}</div></div><span class="badge" :class="quiz.badge">{{ quiz.score }}</span>
        </div>
      </div>
      <label class="lab">Recent sessions</label>
      <div style="margin:8px 0 18px">
        <div v-for="session in sessions" :key="session.sessionHistoryId" class="row">
          <div class="g1"><div class="t" style="font-size:13px">{{ session.date }} · {{ session.topic }}</div><div class="s">{{ session.status }} · {{ session.homework }}</div></div>
          <span class="badge" :class="session.badge">{{ session.status === 'Missed' ? '✗' : '✓' }}</span>
        </div>
      </div>
      <button class="btn magnetic" type="button" style="width:100%;justify-content:center;margin-bottom:10px" @click="printReport">Print student report</button>
      <button class="btn grad magnetic" type="button" style="width:100%;justify-content:center" @click="$emit('toast', 'Progress saved · student & parent notified')">Save &amp; update progress</button>
    </template>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import TutorLineTrend from './TutorLineTrend.vue'
import TutorSegmentedControl from './TutorSegmentedControl.vue'

const props = defineProps({
  student: { type: Object, default: null },
  scores: { type: Array, default: () => [] },
  sessions: { type: Array, default: () => [] }
})

defineEmits(['close', 'toast'])

const pace = ref('Fast')
const remarks = ref('')

function printReport() {
  window.print()
}

watch(() => props.student, (student) => {
  pace.value = student?.progress.learningPace || 'Fast'
  remarks.value = student?.progress.tutorRemarks || ''
}, { immediate: true })
</script>
