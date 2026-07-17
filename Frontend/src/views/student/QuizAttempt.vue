<script setup>
import { computed, ref } from "vue"
import { useRoute, useRouter, RouterLink } from "vue-router"
import PageHeader from "../../components/student/PageHeader.vue"
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  XCircleIcon,
  TrophyIcon,
} from "@heroicons/vue/24/outline"
import { weeklyQuizzes, quizQuestions } from "../../data/studentMockData"

const route = useRoute()
const router = useRouter()

const quizId = computed(() => Number(route.params.id))
const quiz = computed(() => weeklyQuizzes.find((q) => q.quiz_id === quizId.value))
const questions = computed(() => quizQuestions[quizId.value] || [])

// current question index while attempting the quiz
const currentIndex = ref(0)
// selected option index per question id
const answers = ref({})
// whether the quiz has been submitted (shows results screen)
const submitted = ref(false)

const currentQuestion = computed(() => questions.value[currentIndex.value])
const isLastQuestion = computed(
  () => currentIndex.value === questions.value.length - 1
)
const hasAnsweredCurrent = computed(
  () => answers.value[currentQuestion.value?.id] !== undefined
)

function selectOption(optionIndex) {
  answers.value[currentQuestion.value.id] = optionIndex
}

function goNext() {
  if (!isLastQuestion.value) {
    currentIndex.value++
  } else {
    submitted.value = true
  }
}

function goPrevious() {
  if (currentIndex.value > 0) currentIndex.value--
}

function retakeQuiz() {
  currentIndex.value = 0
  answers.value = {}
  submitted.value = false
}

const score = computed(() => {
  if (questions.value.length === 0) return 0
  const correct = questions.value.filter(
    (q) => answers.value[q.id] === q.correctIndex
  ).length
  return Math.round((correct / questions.value.length) * 100)
})

const correctCount = computed(
  () =>
    questions.value.filter((q) => answers.value[q.id] === q.correctIndex)
      .length
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
      <PageHeader :title="quiz.title" :subtitle="`${quiz.subject} · Week ${quiz.weekNumber}`" />

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
                Correct answer: {{ q.options[q.correctIndex] }}
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
      <div v-else-if="questions.length > 0" class="card p-6 md:p-8 max-w-2xl mx-auto">
        <!-- Progress -->
        <div class="flex items-center justify-between mb-5">
          <span class="text-xs font-semibold text-ink-soft dark:text-slate-400">
            Question {{ currentIndex + 1 }} of {{ questions.length }}
          </span>
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
