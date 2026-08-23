<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '../../components/student/PageHeader.vue'
import { studentApi } from '../../services/studentApi'

const router = useRouter()
const quizzes = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const r = await studentApi.getQuizzes()
    quizzes.value = r.data?.quizzes || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <PageHeader title="Weekly Quiz" subtitle="Quizzes created by your tutor." />
    <p v-if="loading">Loading quizzes...</p>
    <p v-else-if="error" class="text-red-500">{{ error }}</p>
    <div v-else-if="!quizzes.length" class="card p-8 text-center text-slate-500">
      No quizzes are available yet. Your tutor can create one.
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
      <div v-for="q in quizzes" :key="q.quiz_id" class="card p-5">
        <p class="text-xs text-brand-blue font-semibold">{{ q.subject }}</p>
        <h3 class="font-display font-bold mt-1">{{ q.title }}</h3>
        <p class="text-sm text-slate-500 mt-2">Topic: {{ q.topic }}</p>
        <p class="text-sm text-slate-500 mt-1">Difficulty: {{ q.difficulty }}</p>
        <p class="text-sm text-slate-500 mt-1">Week {{ q.weekNumber || '-' }}</p>
        <p class="text-sm mt-2">{{ q.score === null ? 'Not attempted' : `Score: ${q.score}%` }}</p>
        <button class="btn grad sm mt-4" @click="router.push(`/student/quiz/${q.quiz_id}`)">
          {{ q.score === null ? 'Start Quiz' : 'View Quiz' }}
        </button>
      </div>
    </div>
  </div>
</template>
