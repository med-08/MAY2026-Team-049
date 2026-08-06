<script setup>
import { ref, onMounted } from "vue"
import PageHeader from "../../components/student/PageHeader.vue"
import { CalendarDaysIcon, TrophyIcon, SparklesIcon } from "@heroicons/vue/24/outline"
import { weeklyQuizzes as mockQuizzes } from "../../data/studentMockData"
import { apiRequest } from "../../services/apiClient"

const quizzes = ref([...mockQuizzes])
const topicInput = ref("")
const isGenerating = ref(false)
const message = ref("")
const errorMessage = ref("")

async function fetchQuizzes() {
  try {
    const res = await apiRequest("/student/quizzes")
    if (res.data && Array.isArray(res.data) && res.data.length > 0) {
      quizzes.value = res.data
    }
  } catch (err) {
    console.warn("Using mock quizzes fallback:", err.message)
  }
}

async function handleGenerateQuiz() {
  const topic = topicInput.value.trim()
  if (!topic) return

  isGenerating.value = true
  message.value = ""
  errorMessage.value = ""

  try {
    const res = await apiRequest("/student/quizzes/generate", {
      method: "POST",
      body: { topic, count: 5 }
    })
    message.value = res.message || "AI Quiz generated successfully!"
    topicInput.value = ""
    await fetchQuizzes()
  } catch (err) {
    errorMessage.value = err.message || "Failed to generate AI Quiz."
  } finally {
    isGenerating.value = false
  }
}

onMounted(() => {
  fetchQuizzes()
})
</script>

<template>
  <div>
    <PageHeader
      title="Weekly Quiz"
      subtitle="Attempt your weekly quizzes, track your performance, or generate custom AI quizzes."
    />

    <!-- Generate AI Quiz Section -->
    <div class="card p-5 mb-6 bg-gradient-to-r from-brand-green-500/10 to-brand-blue-500/10 border border-brand-green-500/20">
      <div class="flex items-center gap-2 mb-2">
        <SparklesIcon class="w-5 h-5 text-brand-green" />
        <h3 class="text-base font-display font-bold">Generate AI Quiz</h3>
      </div>
      <p class="text-xs text-ink-soft dark:text-slate-300 mb-3">
        Enter any subject topic to instantly create a new custom quiz using Gemini AI.
      </p>

      <form @submit.prevent="handleGenerateQuiz" class="flex flex-col sm:flex-row gap-3">
        <input
          v-model="topicInput"
          type="text"
          placeholder="e.g. Photosynthesis, Quadratic Equations, World War II..."
          class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-card-dark text-sm focus:outline-none focus:ring-2 focus:ring-brand-green"
          :disabled="isGenerating"
        />
        <button
          type="submit"
          :disabled="isGenerating || !topicInput.trim()"
          class="px-5 py-2.5 rounded-xl font-semibold text-sm bg-brand-green text-white hover:bg-brand-green-dark disabled:opacity-50 transition flex items-center justify-center gap-2"
        >
          <SparklesIcon v-if="!isGenerating" class="w-4 h-4" />
          <span>{{ isGenerating ? "Generating..." : "Generate Quiz" }}</span>
        </button>
      </form>

      <p v-if="message" class="text-xs font-semibold text-brand-green mt-2">
        {{ message }}
      </p>
      <p v-if="errorMessage" class="text-xs font-semibold text-danger mt-2">
        {{ errorMessage }}
      </p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
      <div
        v-for="q in quizzes"
        :key="q.quiz_id"
        class="card card-hover p-5 flex flex-col"
      >
        <!-- Subject -->
        <p class="text-sm font-semibold text-brand-blue mb-2">
          {{ q.subject }}
        </p>

        <!-- Quiz Title -->
        <h3 class="text-lg font-display font-bold mb-4">
          {{ q.title }}
        </h3>

        <!-- Week -->
        <div class="flex items-center gap-2 text-sm text-ink-soft dark:text-slate-300 mb-3">
          <CalendarDaysIcon class="w-5 h-5" />
          <span>Week {{ q.weekNumber }}</span>
        </div>

        <!-- Last Attempt -->
        <div class="flex justify-between text-sm border-b border-slate-200 dark:border-border-dark pb-3 mb-3">
          <span class="text-ink-soft dark:text-slate-400">Last Attempt</span>
          <span class="font-medium">{{ q.lastAttempt || "Not Attempted" }}</span>
        </div>

        <!-- Previous Score -->
        <div class="flex justify-between text-sm mb-5">
          <span class="text-ink-soft dark:text-slate-400">Previous Score</span>
          <span class="font-semibold flex items-center gap-1">
            <TrophyIcon class="w-4 h-4 text-yellow-500" />
            {{ q.score !== null && q.score !== undefined ? q.score + "%" : "--" }}
          </span>
        </div>

        <!-- Button -->
        <RouterLink
          :to="`/student/quiz/${q.quiz_id}`"
          class="mt-auto w-full py-2.5 rounded-xl font-semibold text-sm text-center bg-cyan-100 text-cyan-700 hover:bg-cyan-200 dark:bg-cyan-500/15 dark:text-cyan-300 dark:hover:bg-cyan-500/25 transition"
        >
          {{ q.score !== null && q.score !== undefined ? "Retake Quiz" : "Take Quiz" }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>