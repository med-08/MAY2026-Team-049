<template>
  <section class="view on">
    <div class="grid g2col reveal" style="grid-template-columns:1.4fr 1fr">
      <div class="card glass">
        <div class="ch"><h3>Shared Q&amp;A board</h3><span class="eyebrow">visible to all your students</span></div>
        <div>
          <div v-for="entry in entries" :key="entry.faqId" class="row"><div class="g1"><div class="t">{{ entry.question }}</div><div class="s">{{ entry.meta }}</div></div><span class="badge done">Live</span></div>
        </div>
      </div>
      <div class="card glass">
        <div class="ch"><h3>Post an answer</h3></div>
        <label class="lab" for="qa-question">Question</label><input id="qa-question" v-model="question" class="field" style="margin-bottom:12px" placeholder="Common question students ask…">
        <label class="lab" for="qa-answer">Answer</label><textarea id="qa-answer" v-model="answer" class="field" rows="4" style="margin-bottom:12px;resize:vertical" placeholder="Answer it once for everyone…"></textarea>
        <button class="btn grad magnetic" type="button" style="width:100%;justify-content:center" @click="publish">Publish to board</button>
        <div class="eyebrow" style="margin-top:12px">Resolves recurring doubts in one place</div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
const props = defineProps({ entries: { type: Array, required: true } })
const emit = defineEmits(['publish', 'toast'])
const question = ref('')
const answer = ref('')
function publish() {
  if (!question.value.trim()) return
  emit('publish', { question: question.value.trim(), answer: answer.value.trim() })
  question.value = ''
  answer.value = ''
}
</script>
