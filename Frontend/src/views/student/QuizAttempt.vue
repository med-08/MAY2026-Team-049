<script setup>
import { computed, ref, onMounted, watch } from "vue"
import { useRoute, useRouter, RouterLink } from "vue-router"
import PageHeader from "../../components/student/PageHeader.vue"
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  XCircleIcon,
  TrophyIcon,
  BoltIcon
} from "@heroicons/vue/24/outline"
import { weeklyQuizzes as mockWeeklyQuizzes, quizQuestions as mockQuizQuestions } from "../../data/studentMockData"
import { apiRequest } from "../../services/apiClient"

const route = useRoute()
const router = useRouter()

const quizId = computed(() => Number(route.params.id))
const quiz = ref(null)
const rawQuestions = ref([])

const currentIndex = ref(0)
const answers = ref({})
const submitted = ref(false)
const currentDifficulty = ref("medium")

// Sequence of question indices traversed during adaptive attempt
const traversalPath = ref([0])

async function fetchQuizData() {
  try {
    const res = await apiRequest(`/student/quizzes/${quizId.value}`)
    if (res.data) {
      quiz.value = res.data
      rawQuestions.value = res.data.questions || []
    }
  } catch (err) {
    console.warn("Using mock quiz data fallback:", err.message)
    quiz.value = mockWeeklyQuizzes.find((q) => q.quiz_id === quizId.value) || null
    rawQuestions.value = mockQuizQuestions[quizId.value] || []
  }
}

onMounted(() => {
  fetchQuizData()
})

const questions = computed(() => rawQuestions.value)
const currentQuestion = computed(() => questions.value[currentIndex.value] || null)

const isLastQuestion = computed(
  () => currentIndex.value === questions.value.length - 1
)

const hasAnsweredCurrent = computed(
  () => currentQuestion.value && answers.value[currentQuestion.value.id] !== undefined
)

function selectOption(optionIndex) {
  if (currentQuestion.value) {
    answers.value[currentQuestion.value.id] = optionIndex
  }
}

// Plain if/else rule-based difficulty adjustment
function getNextDifficulty(currentDiff, isCorrect) {
  if (isCorrect) {
    if (currentDiff === 'easy') return 'medium'
    if (currentDiff === 'medium') return 'hard'
    return 'hard'
  } else {
    if (currentDiff === 'hard') return 'medium'
    if (currentDiff === 'medium') return 'easy'
    return 'easy'
  }
}

async function goNext() {
  if (!currentQuestion.value) return

  // Determine correctness of current answer
  const isCorrect = answers.value[currentQuestion.value.id] === currentQuestion.value.correctIndex

  if (!isLastQuestion.value) {
    // Adaptive difficulty adjustment for next question
    currentDifficulty.value = getNextDifficulty(currentDifficulty.value, isCorrect)
    currentIndex.value++
    traversalPath.value.push(currentIndex.value)
  } else {
    submitted.value = true
    // Post attempt to backend if available
    try {
      await apiRequest(`/student/quizzes/${quizId.value}/attempt`, {
        method: "POST",
        body: { score: score.value }
      })
    } catch (err) {
      console.warn("Could not save quiz attempt:", err.message)
    }
  }
}

function goPrevious() {
  if (currentIndex.value > 0) {
    currentIndex.value--
  }
}

function retakeQuiz() {
  currentIndex.value = 0
  answers.value = {}
  submitted.value = false
  currentDifficulty.value = "medium"
  traversalPath.value = [0]
}

const score = computed(() => {
  if (questions.value.length === 0) return 0
  const correct = questions.value.filter(
    (q) => answers.value[q.id] === q.correctIndex
  ).length
  return Math.round((correct / questions.value.length) * 100)
})

const correctCount = computed(
  () => questions.value.filter((q) => answers.value[q.id] === q.correctIndex).length
)
</script>

<template>
  <div>
    <button
      @click="router.push('/student/quiz')"
      class="flex items-center gap-1.5 text-sm font-medium text-ink-soft dark:text-slate-400 hover:text-brand-blue dark:hover:text-brand-blue mb-4 transition"
    >
      <ArrowLeftIcon class="w-4 h-4" />
      Back to Weekly Quiz
    </button>

    <div v-if="!quiz">
      <PageHeader title="Quiz Not Found" subtitle="We couldn't find this quiz." />
      <RouterLink to="/student/quiz" class="text-brand-blue font-medium text-sm">
        Go back to Weekly Quiz
      </RouterLink>
    </div>

    <div v-else>
      <PageHeader :title="quiz.title" :subtitle="`${quiz.subject} · Week ${quiz.weekNumber || 1}`" />

      <!-- Results screen -->
      <div v-if="submitted" class="card p-8 max-w-xl mx-auto text-center">
        <TrophyIcon class="w-12 h-12 text-yellow-500 mx-auto mb-3" />
        <h2 class="text-xl font-display font-bold mb-1">Quiz Completed!</h2>
        <p class="text-sm text-ink-soft dark:text-slate-400 mb-6">
          You scored {{ correctCount }} out of {{ questions.length }} questions correctly.
        </p>

        <div class="text-4xl font-display font-bold text-brand-blue mb-6">
          {{ score }}%
        </div>

        <div class="text-left space-y-3 mb-6">
          <div
            v-for="(q, idx) in questions"
            :key="q.id"
            class="flex items-start gap-2 text-sm border-b border-slate-200 dark:border-border-dark pb-3"
          >
            <CheckCircleIcon
              v-if="answers[q.id] === q.correctIndex"
              class="w-5 h-5 text-brand-green shrink-0 mt-0.5"
            />
            <XCircleIcon v-else class="w-5 h-5 text-danger shrink-0 mt-0.5" />
            <div>
              <p class="font-medium">{{ idx + 1 }}. {{ q.question }}</p>
              <p class="text-ink-soft dark:text-slate-400 mt-0.5">
                Correct answer: {{ q.options ? q.options[q.correctIndex] : q.correctIndex }}
              </p>
            </div>
          </div>
        </div>

        <div class="flex gap-3 justify-center">
          <button
            @click="retakeQuiz"
            class="px-5 py-2.5 rounded-xl font-semibold text-sm bg-cyan-100 text-cyan-700 hover:bg-cyan-200 dark:bg-cyan-500/15 dark:text-cyan-300 dark:hover:bg-cyan-500/25 transition"
          >
            Retake Quiz
          </button>
          <RouterLink
            to="/student/quiz"
            class="px-5 py-2.5 rounded-xl font-semibold text-sm bg-slate-100 text-ink hover:bg-slate-200 dark:bg-white/5 dark:text-slate-200 dark:hover:bg-white/10 transition"
          >
            Back to Quizzes
          </RouterLink>
        </div>
      </div>

      <!-- Quiz taking screen -->
      <div v-else-if="questions.length > 0 && currentQuestion" class="card p-6 md:p-8 max-w-2xl mx-auto">
        <!-- Progress + Adaptive Difficulty Badge -->
        <div class="flex items-center justify-between mb-5">
          <div class="flex items-center gap-2">
            <span class="text-xs font-semibold text-ink-soft dark:text-slate-400">
              Question {{ currentIndex + 1 }} of {{ questions.length }}
            </span>
            <span
              class="px-2 py-0.5 rounded-md text-[11px] font-bold uppercase tracking-wider flex items-center gap-1"
              :class="{
                'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300': (currentQuestion.difficulty || currentDifficulty) === 'easy',
                'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-300': (currentQuestion.difficulty || currentDifficulty) === 'medium',
                'bg-rose-100 text-rose-700 dark:bg-rose-500/20 dark:text-rose-300': (currentQuestion.difficulty || currentDifficulty) === 'hard'
              }"
            >
              <BoltIcon class="w-3 h-3" />
              {{ currentQuestion.difficulty || currentDifficulty }}
            </span>
          </div>

          <div class="flex gap-1.5">
            <span
              v-for="(q, idx) in questions"
              :key="q.id"
              class="w-6 h-1.5 rounded-full"
              :class="idx <= currentIndex ? 'bg-brand-blue' : 'bg-slate-200 dark:bg-white/10'"
            />
          </div>
        </div>

        <h3 class="text-lg font-display font-semibold mb-5">
          {{ currentQuestion.question }}
        </h3>

        <div class="space-y-3 mb-6">
          <button
            v-for="(option, idx) in currentQuestion.options"
            :key="idx"
            @click="selectOption(idx)"
            class="w-full text-left px-4 py-3 rounded-xl border text-sm font-medium transition"
            :class="answers[currentQuestion.id] === idx
              ? 'border-brand-blue bg-brand-blue/10 text-brand-blue dark:bg-brand-blue/15'
              : 'border-slate-200 dark:border-border-dark hover:bg-slate-50 dark:hover:bg-white/5'"
          >
            {{ option }}
          </button>
        </div>

        <div class="flex items-center justify-between">
          <button
            @click="goPrevious"
            :disabled="currentIndex === 0"
            class="px-4 py-2 rounded-xl font-semibold text-sm text-ink-soft dark:text-slate-400 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 dark:hover:bg-white/5 transition"
          >
            Previous
          </button>

          <button
            @click="goNext"
            :disabled="!hasAnsweredCurrent"
            class="px-5 py-2.5 rounded-xl font-semibold text-sm bg-brand-blue text-white hover:bg-brand-blue-dark disabled:opacity-40 disabled:cursor-not-allowed transition"
          >
            {{ isLastQuestion ? "Submit Quiz" : "Next Question" }}
          </button>
        </div>
      </div>

      <!-- No questions available -->
      <div v-else class="card p-8 max-w-xl mx-auto text-center">
        <p class="text-sm text-ink-soft dark:text-slate-400">
          No questions are available for this quiz yet.
        </p>
      </div>
    </div>
  </div>
</template>

