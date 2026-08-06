<template>
  <section class="view on">
    <div class="card glass reveal">
      <div class="ch"><h3>Student doubts</h3><span class="eyebrow">reply within 24h · student is notified</span></div>
      <div>
        <div v-for="doubt in doubts" :key="doubt.doubtId" class="row">
          <div class="av" :style="{ background: studentById(doubt.studentId).gradient }">{{ studentById(doubt.studentId).initials }}</div>
          <div class="g1">
            <div class="t">{{ doubt.question }}</div>
            <div class="s">{{ studentById(doubt.studentId).name }} · {{ doubt.subject }} · {{ doubt.askedAt }}</div>
            <div class="reply-open" style="margin-top:10px">
              <template v-if="doubt.status === 'Open'">
                <input v-model="replies[doubt.doubtId]" class="field dreply" :placeholder="`Type your reply to ${studentById(doubt.studentId).name.split(' ')[0]}…`">
                <button class="btn grad sm magnetic dsend" type="button" style="margin-top:8px" @click="reply(doubt)">Send reply</button>
              </template>
              <div v-else class="s" style="color:var(--lime)">Replied · {{ studentById(doubt.studentId).name }} notified</div>
            </div>
          </div>
          <span class="badge" :class="doubt.status === 'Open' ? 'warn' : 'done'">{{ doubt.status === 'Open' ? 'Open' : 'Answered' }}</span>
        </div>
      </div>
      <div class="eyebrow" style="margin-top:14px">Recurring question? Answer it once on the <button class="lnk" type="button" @click="$emit('navigate', 'qa')">Q&amp;A board →</button></div>
    </div>
  </section>
</template>

<script setup>
import { reactive } from 'vue'
const props = defineProps({
  doubts: { type: Array, required: true },
  students: { type: Array, required: true }
})
const emit = defineEmits(['reply', 'navigate'])
const replies = reactive({})
function studentById(id) {
  return props.students.find((student) => student.studentId === id) || props.students[0]
}
function reply(doubt) {
  const value = replies[doubt.doubtId]?.trim()
  if (!value) return
  emit('reply', doubt.doubtId, value)
  replies[doubt.doubtId] = ''
}
</script>
