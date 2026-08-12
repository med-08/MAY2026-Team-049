<script setup>
import { computed, ref, onMounted } from "vue"
import PageHeader from "../../components/student/PageHeader.vue"
import { CalendarDaysIcon, TrophyIcon, SparklesIcon, AcademicCapIcon, BoltIcon } from "@heroicons/vue/24/outline"
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

const tutorQuizzes = computed(() => {
  return quizzes.value.filter(q => !q.title.toLowerCase().startsWith('ai quiz'))
})

const selfPracticeQuizzes = computed(() => {
  return quizzes.value.filter(q => q.title.toLowerCase().startsWith('ai quiz'))
})

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
      title="Quizzes & Self-Practice"
      subtitle="Attempt quizzes assigned by your tutor or generate instant custom AI practice quizzes."
    />

    <!-- Generate AI Quiz Section -->
    <div class="card p-5 mb-8 bg-gradient-to-r from-brand-purple/10 to-brand-blue/10 border border-brand-purple/20">
      <div class="flex items-center gap-2 mb-2">
        <SparklesIcon class="w-5 h-5 text-brand-purple" />
        <h3 class="text-base font-display font-bold">Generate Custom AI Self-Practice Quiz</h3>
      </div>
      <p class="text-xs text-ink-soft dark:text-slate-300 mb-3">
        Enter any subject topic to instantly create a new custom practice quiz using Gemini AI.
      </p>

      <form @submit.prevent="handleGenerateQuiz" class="flex flex-col sm:flex-row gap-3">
        <input
          v-model="topicInput"
          type="text"
          placeholder="e.g. Food Chain, Photosynthesis, Quadratic Equations..."
          class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-card-dark text-sm focus:outline-none focus:ring-2 focus:ring-brand-purple"
          :disabled="isGenerating"
        />
        <button
          type="submit"
          :disabled="isGenerating || !topicInput.trim()"
          class="px-5 py-2.5 rounded-xl font-bold text-sm bg-gradient-to-r from-brand-purple to-brand-blue text-white hover:opacity-90 disabled:opacity-50 transition flex items-center justify-center gap-2 cursor-pointer shadow-md"
        >
          <SparklesIcon v-if="!isGenerating" class="w-4 h-4" />
          <span>{{ isGenerating ? "Generating..." : "Generate AI Quiz" }}</span>
        </button>
      </form>

      <p v-if="message" class="text-xs font-semibold text-emerald-500 mt-2">
        ✓ {{ message }}
      </p>
      <p v-if="errorMessage" class="text-xs font-semibold text-rose-500 mt-2">
        {{ errorMessage }}
      </p>
    </div>

    <!-- SECTION 1: QUIZZES ASSIGNED BY TUTOR -->
    <div class="mb-10">
      <div class="flex items-center gap-2.5 mb-4 pb-2 border-b border-slate-200 dark:border-white/10">
        <div class="p-2 rounded-xl bg-brand-purple/10 text-brand-purple font-bold">
          <AcademicCapIcon class="w-5 h-5" />
        </div>
        <div>
          <h3 class="text-lg font-display font-bold">Quizzes Assigned by Tutor</h3>
          <p class="text-xs text-ink-soft dark:text-slate-400">Official course quizzes and homework assigned to your class</p>
        </div>
      </div>

      <div v-if="tutorQuizzes.length" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        <div
          v-for="q in tutorQuizzes"
          :key="q.quiz_id"
          class="card card-hover p-5 flex flex-col border border-brand-purple/20 bg-gradient-to-b from-brand-purple/5 to-transparent"
        >
          <div class="flex justify-between items-start mb-2">
            <p class="text-xs font-bold text-brand-purple uppercase tracking-wider">
              {{ q.subject }}
            </p>
            <span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-brand-purple/15 text-brand-purple">
              Assigned by Tutor
            </span>
          </div>

          <h3 class="text-base font-display font-bold mb-3 text-slate-800 dark:text-slate-100">
            {{ q.title }}
          </h3>

          <div class="flex items-center gap-2 text-xs text-ink-soft dark:text-slate-300 mb-3">
            <CalendarDaysIcon class="w-4 h-4 text-brand-blue" />
            <span>Time Limit: {{ q.timeLimit || 15 }} mins</span>
          </div>

          <div class="flex justify-between text-xs border-b border-slate-200 dark:border-white/10 pb-2.5 mb-2.5">
            <span class="text-ink-soft dark:text-slate-400">Last Attempt</span>
            <span class="font-medium">{{ q.lastAttempt || "Not Attempted" }}</span>
          </div>

          <div class="flex justify-between text-xs mb-4">
            <span class="text-ink-soft dark:text-slate-400">Previous Score</span>
            <span class="font-bold flex items-center gap-1">
              <TrophyIcon class="w-4 h-4 text-yellow-500" />
              {{ q.score !== null && q.score !== undefined ? q.score + "%" : "--" }}
            </span>
          </div>

          <RouterLink
            :to="`/student/quiz/${q.quiz_id || q.id || 1}`"
            style="background: linear-gradient(135deg, #7C3AED, #2563EB) !important; color: #FFFFFF !important;"
            class="mt-auto w-full py-3 px-4 rounded-xl font-bold text-sm text-center shadow-md hover:opacity-90 transition-all block cursor-pointer border-0"
          >
            {{ (q.score !== null && q.score !== undefined && q.score !== '') ? "Retake Quiz →" : "Take Quiz →" }}
          </RouterLink>
        </div>
      </div>

      <div v-else class="p-6 rounded-2xl bg-slate-50 dark:bg-white/5 text-center text-xs text-slate-400">
        No quizzes assigned by tutor yet.
      </div>
    </div>

    <!-- SECTION 2: AI SELF-PRACTICE & REMEDIAL QUIZZES -->
    <div>
      <div class="flex items-center gap-2.5 mb-4 pb-2 border-b border-slate-200 dark:border-white/10">
        <div class="p-2 rounded-xl bg-cyan-500/10 text-cyan-600 font-bold">
          <BoltIcon class="w-5 h-5" />
        </div>
        <div>
          <h3 class="text-lg font-display font-bold">AI Self-Practice & Remedial Quizzes</h3>
          <p class="text-xs text-ink-soft dark:text-slate-400">Custom quizzes generated by AI for continuous practice</p>
        </div>
      </div>

      <div v-if="selfPracticeQuizzes.length" class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        <div
          v-for="q in selfPracticeQuizzes"
          :key="q.quiz_id || q.id"
          class="card card-hover p-5 flex flex-col border border-cyan-500/20 bg-gradient-to-b from-cyan-500/5 to-transparent"
        >
          <div class="flex justify-between items-start mb-2">
            <p class="text-xs font-bold text-cyan-600 dark:text-cyan-400 uppercase tracking-wider">
              {{ q.subject }}
            </p>
            <span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-cyan-500/15 text-cyan-700 dark:text-cyan-300">
              ⚡ AI Practice
            </span>
          </div>

          <h3 class="text-base font-display font-bold mb-3 text-slate-800 dark:text-slate-100">
            {{ q.title }}
          </h3>

          <div class="flex items-center gap-2 text-xs text-ink-soft dark:text-slate-300 mb-3">
            <CalendarDaysIcon class="w-4 h-4 text-cyan-500" />
            <span>Time Limit: {{ q.timeLimit || 15 }} mins</span>
          </div>

          <div class="flex justify-between text-xs border-b border-slate-200 dark:border-white/10 pb-2.5 mb-2.5">
            <span class="text-ink-soft dark:text-slate-400">Last Attempt</span>
            <span class="font-medium">{{ q.lastAttempt || "Not Attempted" }}</span>
          </div>

          <div class="flex justify-between text-xs mb-4">
            <span class="text-ink-soft dark:text-slate-400">Previous Score</span>
            <span class="font-bold flex items-center gap-1">
              <TrophyIcon class="w-4 h-4 text-yellow-500" />
              {{ q.score !== null && q.score !== undefined ? q.score + "%" : "--" }}
            </span>
          </div>

          <RouterLink
            :to="`/student/quiz/${q.quiz_id || q.id || 1}`"
            style="background: linear-gradient(135deg, #0284C7, #0D9488) !important; color: #FFFFFF !important;"
            class="mt-auto w-full py-3 px-4 rounded-xl font-bold text-sm text-center shadow-md hover:opacity-90 transition-all block cursor-pointer border-0"
          >
            {{ (q.score !== null && q.score !== undefined && q.score !== '') ? "Retake Practice →" : "Start Practice →" }}
          </RouterLink>
        </div>
      </div>

      <div v-else class="p-6 rounded-2xl bg-slate-50 dark:bg-white/5 text-center text-xs text-slate-400">
        No self-practice quizzes generated yet. Use the box above to create one!
      </div>
    </div>
  </div>
</template>