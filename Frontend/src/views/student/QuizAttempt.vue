<script setup>
import { computed, ref, onMounted, onUnmounted } from "vue"
import { useRoute, useRouter, RouterLink } from "vue-router"
import PageHeader from "../../components/student/PageHeader.vue"
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  XCircleIcon,
  TrophyIcon,
  ClockIcon
} from "@heroicons/vue/24/outline"
import { studentApi } from "../../services/studentApi"

const route = useRoute()
const router = useRouter()

const quizId = computed(() => Number(route.params.id))
const quiz = ref(null)
const rawQuestions = ref([])

const currentIndex = ref(0)
const answers = ref({})  // { question_id: option_letter }
const submitted = ref(false)
const isSubmitting = ref(false)

const startTime = ref(Date.now())
const elapsedTime = ref(0)
let timerInterval = null

const submissionResult = ref(null)

function getQuestionKey(q, idx) {
  if (!q) return idx
  return q.id ?? q.question_id ?? q.questionId ?? idx
}

async function fetchQuizData() {
  try {
    const res = await studentApi.getQuizDetails(quizId.value)
    if (res.data) {
      quiz.value = res.data
      rawQuestions.value = res.data.questions || []
    }
  } catch (err) {
    console.warn("Quiz fetch error:", err.message)
  }
}

onMounted(() => {
  fetchQuizData()
  startTime.value = Date.now()
  timerInterval = setInterval(() => {
    elapsedTime.value = Math.floor((Date.now() - startTime.value) / 1000)
  }, 1000)
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})

const timerDisplay = computed(() => {
  const mins = Math.floor(elapsedTime.value / 60)
  const secs = elapsedTime.value % 60
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
})

const questions = computed(() => rawQuestions.value)
const currentQuestion = computed(() => questions.value[currentIndex.value] || null)

const isLastQuestion = computed(
  () => currentIndex.value === questions.value.length - 1
)

function selectOption(optionLetter) {
  if (currentQuestion.value) {
    const key = getQuestionKey(currentQuestion.value, currentIndex.value)
    answers.value[key] = optionLetter
  }
}

async function goNext() {
  if (!isLastQuestion.value) {
    currentIndex.value++
  } else {
    await submitQuiz()
  }
}

async function submitQuiz() {
  if (isSubmitting.value) return
  isSubmitting.value = true
  if (timerInterval) clearInterval(timerInterval)

  try {
    const res = await studentApi.submitQuiz(quizId.value, answers.value)
    if (res.data) {
      submissionResult.value = res.data
    }
  } catch (err) {
    console.error("Quiz submission error:", err)
  } finally {
    submitted.value = true
    isSubmitting.value = false
  }
}

function goPrevious() {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}
</script>

<template>
  <div>
    <button
      @click="router.push('/student/quiz')"
      class="flex items-center gap-1.5 text-sm font-medium text-ink-soft dark:text-slate-400 hover:text-brand-blue dark:hover:text-brand-blue mb-4 transition cursor-pointer"
    >
      <ArrowLeftIcon class="w-4 h-4" />
      Back to Quizzes
    </button>

    <div v-if="!quiz">
      <PageHeader title="Loading Quiz..." subtitle="Please wait while we prepare your quiz." />
    </div>

    <div v-else>
      <PageHeader :title="quiz.title" :subtitle="`${quiz.subject || 'Subject'} · ${quiz.className || 'Class 8/10'} · ${quiz.topicName || 'Practice'}`" />

      <!-- Results screen -->
      <div v-if="submitted" class="card p-6 md:p-8 max-w-2xl mx-auto text-center">
        <TrophyIcon class="w-14 h-14 text-yellow-500 mx-auto mb-3" />
        <h2 class="text-2xl font-display font-bold mb-1">Quiz Completed!</h2>
        <p class="text-xs text-ink-soft dark:text-slate-400 mb-6">
          Your answers have been evaluated and topic performance updated.
        </p>

        <div class="flex justify-center items-center gap-6 mb-6">
          <div class="p-4 rounded-2xl bg-brand-blue/10 border border-brand-blue/20">
            <p class="text-3xl font-display font-bold text-brand-blue">
              {{ submissionResult?.score ?? 0 }}%
            </p>
            <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-0.5">Overall Score</p>
          </div>
          <div class="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
            <p class="text-3xl font-display font-bold text-emerald-500">
              {{ submissionResult?.correctCount ?? 0 }} / {{ submissionResult?.totalQuestions ?? questions.length }}
            </p>
            <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-0.5">Correct Answers</p>
          </div>
          <div class="p-4 rounded-2xl bg-slate-500/10 border border-slate-500/20">
            <p class="text-3xl font-display font-bold text-slate-400">
              {{ submissionResult?.timeTaken || '5m 12s' }}
            </p>
            <p class="text-xs font-semibold text-slate-500 dark:text-slate-400 mt-0.5">Time Taken</p>
          </div>
        </div>

        <!-- Topic Performance Breakdown -->
        <div v-if="submissionResult?.topicPerformance" class="mb-6 p-4 rounded-2xl bg-slate-50 dark:bg-white/5 text-left border border-slate-100 dark:border-white/5">
          <h4 class="font-bold text-xs text-slate-500 uppercase tracking-wider mb-3">Topic Performance Analysis</h4>
          <div class="space-y-2">
            <div v-for="(score, top) in submissionResult.topicPerformance" :key="top" class="flex justify-between items-center text-xs font-semibold">
              <span>{{ top }}</span>
              <span :class="score < 65 ? 'text-amber-500 font-bold' : 'text-emerald-500 font-bold'">{{ score }}%</span>
            </div>
          </div>
        </div>

        <!-- Question Explanations Review -->
        <div class="text-left space-y-4 mb-6">
          <h4 class="font-bold text-sm mb-2">Question Breakdown & Explanations</h4>
          <div
            v-for="(q, idx) in (submissionResult?.questionBreakdown || questions)"
            :key="idx"
            class="p-4 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50/50 dark:bg-white/5"
          >
            <div class="flex items-start gap-2.5">
              <CheckCircleIcon
                v-if="q.isCorrect || q.userAnswer === q.correctOption"
                class="w-5 h-5 text-emerald-500 shrink-0 mt-0.5"
              />
              <XCircleIcon v-else class="w-5 h-5 text-rose-500 shrink-0 mt-0.5" />
              <div class="min-w-0 flex-1">
                <p class="font-semibold text-sm">{{ idx + 1 }}. {{ q.question }}</p>
                <div class="mt-2 text-xs space-y-1">
                  <p :class="q.isCorrect ? 'text-emerald-600 dark:text-emerald-400 font-semibold' : 'text-rose-600 dark:text-rose-400 font-semibold'">
                    Your Answer: {{ q.userAnswer || 'Skipped' }}
                  </p>
                  <p class="text-slate-600 dark:text-slate-300 font-semibold">
                    Correct Option: {{ q.correctOption }}
                  </p>
                  <div v-if="q.explanation" class="mt-2 p-2.5 rounded-lg bg-blue-500/10 text-blue-700 dark:text-blue-300 text-xs">
                    💡 <strong>Explanation:</strong> {{ q.explanation }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex gap-3 justify-center">
          <RouterLink
            to="/student/dashboard"
            class="px-6 py-3 rounded-xl font-bold text-sm bg-gradient-to-r from-brand-purple to-brand-blue text-white shadow-md hover:opacity-90 transition-all"
          >
            Back to Student Dashboard
          </RouterLink>
        </div>
      </div>

      <!-- Quiz taking screen -->
      <div v-else-if="questions.length > 0 && currentQuestion" class="card p-6 md:p-8 max-w-2xl mx-auto">
        <!-- Timer + Progress Header -->
        <div class="flex items-center justify-between mb-5 pb-3 border-b border-slate-100 dark:border-white/10">
          <div class="flex items-center gap-2">
            <span class="text-xs font-bold text-brand-purple">
              Question {{ currentIndex + 1 }} of {{ questions.length }}
            </span>
          </div>

          <div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 dark:bg-white/10 text-xs font-mono font-bold text-slate-700 dark:text-slate-200">
            <ClockIcon class="w-4 h-4 text-brand-blue" />
            {{ timerDisplay }}
          </div>
        </div>

        <h3 class="text-lg font-display font-semibold mb-6">
          {{ currentQuestion.question }}
        </h3>

        <!-- Options -->
        <div class="space-y-3 mb-6">
          <button
            v-for="(optText, optKey) in { 'A': currentQuestion.option_a || currentQuestion.options?.[0], 'B': currentQuestion.option_b || currentQuestion.options?.[1], 'C': currentQuestion.option_c || currentQuestion.options?.[2], 'D': currentQuestion.option_d || currentQuestion.options?.[3] }"
            :key="optKey"
            type="button"
            @click="selectOption(optKey)"
            class="w-full text-left px-4 py-3.5 rounded-xl border text-sm font-medium transition-all flex items-center justify-between cursor-pointer"
            :class="answers[getQuestionKey(currentQuestion, currentIndex)] === optKey
              ? 'border-brand-purple bg-brand-purple/15 text-brand-purple font-bold dark:bg-brand-purple/25 ring-2 ring-brand-purple/30'
              : 'border-slate-200 dark:border-white/10 hover:bg-slate-50 dark:hover:bg-white/5'"
          >
            <span><strong class="mr-2">{{ optKey }}.</strong> {{ optText }}</span>
            <span v-if="answers[getQuestionKey(currentQuestion, currentIndex)] === optKey" class="w-3.5 h-3.5 rounded-full bg-brand-purple flex items-center justify-center text-white text-[9px] font-bold">✓</span>
          </button>
        </div>

        <!-- Navigation Buttons -->
        <div class="flex items-center justify-between">
          <button
            type="button"
            @click="goPrevious"
            :disabled="currentIndex === 0"
            style="background: rgba(100, 116, 139, 0.12) !important; color: #475569 !important;"
            class="px-5 py-2.5 rounded-xl font-bold text-sm disabled:opacity-40 disabled:cursor-not-allowed hover:opacity-80 transition cursor-pointer border-0"
          >
            ← Previous
          </button>

          <button
            type="button"
            @click="goNext"
            :disabled="isSubmitting"
            style="background: linear-gradient(135deg, #7C3AED, #2563EB) !important; color: #FFFFFF !important;"
            class="px-6 py-2.5 rounded-xl font-bold text-sm shadow-md hover:opacity-90 disabled:opacity-50 transition-all cursor-pointer border-0"
          >
            {{ isLastQuestion ? (isSubmitting ? "Evaluating..." : "Submit Quiz ✓") : "Next Question →" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

