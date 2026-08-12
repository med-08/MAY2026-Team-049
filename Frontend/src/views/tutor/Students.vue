<template>
  <section class="view on">
    <div class="card glass reveal">
      <div class="ch"><h3>My students</h3><TutorSegmentedControl v-model="filter" :options="['All', 'Class 9', 'Class 10', 'Class 11']" /></div>
      <div class="filterbar">
        <input v-model="query" class="field" placeholder="Search students">
        <select v-model="classFilter" class="field"><option>All classes</option><option>Class 9</option><option>Class 10</option><option>Class 11</option></select>
        <select v-model="subjectFilter" class="field"><option>All subjects</option><option>Maths</option><option>Physics</option></select>
        <select v-model="performanceFilter" class="field"><option>All performance</option><option>Fast</option><option>Average</option><option>Needs practice</option></select>
      </div>
      <div class="eyebrow" style="margin-bottom:14px">Select a student to open their progress</div>
      <TutorEmptyState v-if="!filteredStudents.length" title="No students found" />
      <div v-else class="scards">
        <button v-for="student in pagedStudents" :key="student.studentId" class="scard" type="button" @click="$emit('select-student', student)">
          <div style="display:flex;gap:14px;align-items:center">
            <div class="ring2" :style="{ background: `conic-gradient(${student.accent} ${student.progress.completedTopics}%,var(--border) 0)` }"><i>{{ student.progress.completedTopics }}%</i></div>
            <div><div class="t" style="font-weight:600">{{ student.name }}</div><div class="s" style="font-size:12px;color:var(--muted)">{{ student.classLevel }} · {{ student.subjects }}</div><span class="badge" :class="{ done: student.progress.learningPace === 'Fast', warn: student.progress.learningPace === 'Needs practice' }" style="margin-top:7px;display:inline-block">{{ student.progress.learningPace }}</span></div>
          </div>
        </button>
      </div>
      <TutorPagination v-if="filteredStudents.length" v-model:page="page" :total-pages="totalPages" />
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import TutorEmptyState from '../../components/tutor/TutorEmptyState.vue'
import TutorPagination from '../../components/tutor/TutorPagination.vue'
import TutorSegmentedControl from '../../components/tutor/TutorSegmentedControl.vue'

const props = defineProps({ students: { type: Array, required: true } })
defineEmits(['select-student'])
const filter = ref('All')
const query = ref('')
const classFilter = ref('All classes')
const subjectFilter = ref('All subjects')
const performanceFilter = ref('All performance')
const page = ref(1)
const pageSize = 3
const filteredStudents = computed(() => props.students.filter((student) => {
  const selectedClass = filter.value !== 'All' ? filter.value : classFilter.value
  return (!query.value || student.name.toLowerCase().includes(query.value.toLowerCase()))
    && (selectedClass === 'All classes' || selectedClass === 'All' || student.classLevel === selectedClass)
    && (subjectFilter.value === 'All subjects' || student.subjects.includes(subjectFilter.value))
    && (performanceFilter.value === 'All performance' || student.progress.learningPace === performanceFilter.value)
}))
const totalPages = computed(() => Math.max(1, Math.ceil(filteredStudents.value.length / pageSize)))
const pagedStudents = computed(() => filteredStudents.value.slice((page.value - 1) * pageSize, page.value * pageSize))
watch([query, filter, classFilter, subjectFilter, performanceFilter], () => { page.value = 1 })
</script>
