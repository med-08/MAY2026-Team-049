<template>
  <section class="view on">
    <div class="grid g2col reveal" style="grid-template-columns:1.4fr 1fr">
      <div class="card glass">
        <div class="ch"><h3>To grade</h3><TutorSegmentedControl v-model="tab" :options="['Pending', 'Active', 'Drafts']" /></div>
        <TutorEmptyState v-if="!assignments.length" title="No assignments" />
        <div v-for="assignment in pagedAssignments" :key="assignment.assignmentId" class="row">
          <div class="g1"><div class="t">{{ assignment.title }}</div><div class="s">{{ assignment.classLevel }} · {{ assignment.submissions }}</div></div>
          <span class="badge" :class="statusClass(assignment.homeworkStatus)">{{ assignment.homeworkStatus }}</span>
          <button class="btn grad sm magnetic" type="button" @click="$emit('toast', 'Opening grader…')">Grade</button>
          <button class="btn sm" type="button" @click="$emit('confirm-action', `Delete ${assignment.title}?`)">Delete</button>
        </div>
        <TutorPagination v-if="assignments.length" v-model:page="page" :total-pages="totalPages" />
      </div>
      <div class="card glass">
        <div class="ch"><h3>Create new</h3></div>
        <TutorSegmentedControl v-model="createType" :options="['Quiz', 'Assignment', 'Puzzle']" style="margin-bottom:14px" />
        <label class="lab" for="assignment-title">Title</label><input id="assignment-title" class="field" style="margin-bottom:12px" placeholder="Weekly quiz — Trigonometry">
        <label class="lab" for="assign-to">Assign to</label><input id="assign-to" class="field" style="margin-bottom:16px" placeholder="Class 10 · Maths">
        <div style="display:flex;gap:9px"><button class="btn grad magnetic" type="button" @click="$emit('toast', 'Quiz created · assigned to Class 10')">Create</button><button class="btn magnetic" type="button" @click="$emit('toast', 'Generating questions with AI…')"><svg viewBox="0 0 24 24"><path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/></svg> AI generate</button></div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import TutorEmptyState from '../../components/tutor/TutorEmptyState.vue'
import TutorPagination from '../../components/tutor/TutorPagination.vue'
import TutorSegmentedControl from '../../components/tutor/TutorSegmentedControl.vue'
const props = defineProps({ assignments: { type: Array, required: true } })
defineEmits(['toast', 'confirm-action'])
const tab = ref('Pending')
const createType = ref('Quiz')
const page = ref(1)
const pageSize = 3
const totalPages = computed(() => Math.max(1, Math.ceil(props.assignments.length / pageSize)))
const pagedAssignments = computed(() => props.assignments.slice((page.value - 1) * pageSize, page.value * pageSize))
function statusClass(status) {
  return { Submitted: 'done', Pending: '', Late: 'warn', Missing: 'warn' }[status] || ''
}
</script>
