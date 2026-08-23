<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PageHeader from '../../components/student/PageHeader.vue'
import { studentApi } from '../../services/studentApi'

const route = useRoute()
const router = useRouter()
const quiz = ref(null)
const questions = ref([])
const answers = ref({})
const loading = ref(true)
const error = ref('')
const submitted = ref(false)
const result = ref(null)
const answered = computed(() => questions.value.filter(q => answers.value[q.id]).length)

onMounted(async () => {
  try {
    const r = await studentApi.getQuizDetails(Number(route.params.id))
    quiz.value = r.data?.quiz
    questions.value = r.data?.questions || []
    if (r.data?.attempt) {
      result.value = r.data.attempt
      submitted.value = true
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})

async function submit() {
  try {
    const r = await studentApi.submitQuiz(Number(route.params.id), answers.value)
    result.value = r.data
    submitted.value = true
  } catch (e) {
    alert(e.message)
  }
}
</script>

<template>
  <div>
    <PageHeader :title="quiz?.title || 'Quiz'" :subtitle="quiz ? `${quiz.subject} - ${quiz.topic} - ${quiz.difficulty}` : ''" />
    <p v-if="loading">Loading quiz...</p>
    <p v-else-if="error" class="text-red-500">{{ error }}</p>
    <div v-else-if="!questions.length" class="card p-8 text-slate-500">This quiz has no questions yet.</div>
    <div v-else-if="submitted" class="space-y-4">
      <div class="card p-8 text-center">
        <h2 class="font-display font-bold text-2xl">Quiz result</h2>
        <p class="mt-2">Score: {{ result.score }}% ({{ result.correctCount }}/{{ result.totalQuestions }})</p>
        <button class="btn grad mt-5" @click="router.push('/student/quiz')">Back to Quizzes</button>
      </div>
      <div v-for="(item, i) in result.review || []" :key="item.id" class="card p-5">
        <p class="font-semibold">{{ i + 1 }}. {{ item.question }}</p>
        <div class="grid gap-2 mt-4">
          <div
            v-for="letter in ['A','B','C','D']"
            :key="letter"
            class="p-3 rounded-xl border"
            :class="letter === item.correct_option ? 'border-emerald-300 bg-emerald-50 text-emerald-800' : letter === item.selected && !item.is_correct ? 'border-red-300 bg-red-50 text-red-700' : 'border-slate-200 dark:border-slate-700'"
          >
            {{ letter }}. {{ item.options?.[letter] }}
          </div>
        </div>
        <p class="mt-3 text-sm font-semibold" :class="item.is_correct ? 'text-emerald-600' : 'text-red-600'">
          {{ item.is_correct ? 'Correct' : 'Incorrect' }} - Your answer: {{ item.selected || 'Not answered' }}. Correct answer: {{ item.correct_option }}
        </p>
        <p v-if="item.explanation" class="mt-2 text-sm text-slate-500">{{ item.explanation }}</p>
      </div>
    </div>
    <div v-else class="space-y-4">
      <div v-for="(q, i) in questions" :key="q.id" class="card p-5">
        <p class="font-semibold">{{ i + 1 }}. {{ q.question }}</p>
        <div class="grid gap-2 mt-4">
          <label v-for="(o, j) in q.options" :key="j" class="p-3 rounded-xl border border-slate-200 dark:border-slate-700 cursor-pointer">
            <input v-model="answers[q.id]" type="radio" :name="`q-${q.id}`" :value="String.fromCharCode(65 + j)" class="mr-2">{{ String.fromCharCode(65 + j) }}. {{ o }}
          </label>
        </div>
      </div>
      <button class="btn grad" :disabled="answered !== questions.length" @click="submit">Submit Quiz</button>
    </div>
  </div>
</template>
