<template>
  <section class="view on">
    <div class="grid g2col reveal" style="grid-template-columns:1.2fr 1.3fr">
      <!-- Left Column: Existing To Grade List -->
      <div class="card glass">
        <div class="ch">
          <h3>Quizzes & Assignments</h3>
          <TutorSegmentedControl v-model="tab" :options="['Pending', 'Active', 'Drafts']" />
        </div>
        <TutorEmptyState v-if="!assignments.length" title="No assignments" />
        <div v-for="assignment in pagedAssignments" :key="assignment.assignmentId" class="row">
          <div class="g1">
            <div class="t">{{ assignment.title }}</div>
            <div class="s">{{ assignment.classLevel || 'Class 10' }} · {{ assignment.submissions || '0 submissions' }}</div>
          </div>
          <span class="badge" :class="statusClass(assignment.homeworkStatus)">{{ assignment.homeworkStatus || 'Active' }}</span>
          <button class="btn sm" type="button" @click="$emit('confirm-action', `Delete ${assignment.title}?`)">Delete</button>
        </div>
        <TutorPagination v-if="assignments.length" v-model:page="page" :total-pages="totalPages" />
      </div>

      <!-- Right Column: AI Quiz Generator & Review Screen -->
      <div class="card glass" style="display:flex;flex-direction:column;gap:12px">
        <div class="ch">
          <h3>AI Quiz Generator</h3>
          <span class="eyebrow" style="color:var(--g1)">Review before assigning</span>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
          <div>
            <label class="lab" for="quiz-class">Class</label>
            <select id="quiz-class" v-model="classNameInput" class="field">
              <option value="Class 10">Class 10</option>
              <option value="Class 9">Class 9</option>
              <option value="Class 8">Class 8</option>
            </select>
          </div>
          <div>
            <label class="lab" for="quiz-subject">Subject</label>
            <select id="quiz-subject" v-model="subjectInput" class="field">
              <option value="Mathematics">Mathematics</option>
              <option value="Physics">Physics</option>
              <option value="Science">Science</option>
            </select>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:1.2fr 1fr;gap:10px">
          <div>
            <label class="lab" for="quiz-topic">Topic / Chapter</label>
            <input id="quiz-topic" v-model="topicInput" class="field" placeholder="e.g. Quadratic Equations, Factorisation">
          </div>
          <div>
            <label class="lab" for="quiz-diff">Difficulty</label>
            <select id="quiz-diff" v-model="difficultyInput" class="field">
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">
          <div>
            <label class="lab" for="quiz-title">Quiz Title</label>
            <input id="quiz-title" v-model="titleInput" class="field" placeholder="e.g. Quadratic Equations Practice">
          </div>
          <div>
            <label class="lab" for="quiz-obj">Objective (Optional)</label>
            <input id="quiz-obj" v-model="objectiveInput" class="field" placeholder="e.g. Master middle-term splitting">
          </div>
        </div>

        <button
          class="btn grad magnetic"
          type="button"
          style="justify-content:center;margin-top:4px"
          :disabled="isGenerating"
          @click="handleAiGenerate"
        >
          <svg viewBox="0 0 24 24" style="width:16px;height:16px;margin-right:6px">
            <path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18" stroke="currentColor" stroke-width="2" fill="none"/>
          </svg>
          {{ isGenerating ? 'AI Generating Questions...' : 'Generate Quiz with AI' }}
        </button>

        <p v-if="errorMessage" style="color:var(--coral);font-size:12px;margin-top:2px;font-weight:600">
          {{ errorMessage }}
        </p>

        <!-- AI Generated Questions REVIEW & EDIT Screen -->
        <div v-if="generatedQuestions.length" style="margin-top:12px;border-top:1px solid rgba(255,255,255,0.12);padding-top:14px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
            <h4 style="font-size:14px;font-weight:700;color:var(--brand-purple,#8B6BFF);margin:0">
              Review Questions ({{ generatedQuestions.length }})
            </h4>
            <div style="display:flex;gap:6px">
              <button class="btn sm" type="button" @click="addManualQuestion">+ Add Question</button>
              <button class="btn sm" type="button" @click="clearGeneratedQuestions">Discard</button>
            </div>
          </div>

          <div style="display:flex;flex-direction:column;gap:12px;max-height:450px;overflow-y:auto;padding-right:4px">
            <div
              v-for="(q, qIdx) in generatedQuestions"
              :key="qIdx"
              style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);border-radius:12px;padding:12px"
            >
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                <span style="font-size:12px;font-weight:700;color:var(--g1,#4CC9F0)">
                  Question #{{ qIdx + 1 }} · {{ q.difficulty || 'medium' }}
                </span>
                <div style="display:flex;gap:4px">
                  <button v-if="qIdx > 0" class="btn sm" style="padding:2px 6px" type="button" @click="moveQuestion(qIdx, -1)">▲</button>
                  <button v-if="qIdx < generatedQuestions.length - 1" class="btn sm" style="padding:2px 6px" type="button" @click="moveQuestion(qIdx, 1)">▼</button>
                  <button class="btn sm" style="padding:2px 6px;color:var(--coral)" type="button" @click="deleteQuestion(qIdx)">✕</button>
                </div>
              </div>

              <textarea
                v-model="q.question"
                class="field"
                rows="2"
                style="margin-bottom:8px;font-size:13px;line-height:1.4"
                placeholder="Question text"
              ></textarea>

              <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px">
                <div>
                  <label class="lab" style="font-size:10px">Option A</label>
                  <input v-model="q.option_a" class="field" style="font-size:12px">
                </div>
                <div>
                  <label class="lab" style="font-size:10px">Option B</label>
                  <input v-model="q.option_b" class="field" style="font-size:12px">
                </div>
                <div>
                  <label class="lab" style="font-size:10px">Option C</label>
                  <input v-model="q.option_c" class="field" style="font-size:12px">
                </div>
                <div>
                  <label class="lab" style="font-size:10px">Option D</label>
                  <input v-model="q.option_d" class="field" style="font-size:12px">
                </div>
              </div>

              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
                <label class="lab" style="font-size:11px;margin:0">Correct Answer:</label>
                <select v-model="q.correct_option" class="field" style="width:85px;padding:4px 8px;font-size:12px">
                  <option value="A">A</option>
                  <option value="B">B</option>
                  <option value="C">C</option>
                  <option value="D">D</option>
                </select>
              </div>

              <div>
                <label class="lab" style="font-size:10px">Explanation for Students</label>
                <textarea
                  v-model="q.explanation"
                  class="field"
                  rows="2"
                  style="font-size:11px;color:var(--muted)"
                  placeholder="Step-by-step explanation shown after submission"
                ></textarea>
              </div>
            </div>
          </div>

          <!-- ASSIGN MODAL / CONFIGURATION -->
          <div style="margin-top:14px;background:rgba(139,107,255,0.08);border:1px solid var(--ring);border-radius:12px;padding:12px">
            <h5 style="font-size:13px;font-weight:700;margin-bottom:8px">Assignment Configuration</h5>
            <div style="display:grid;grid-template-columns:1.2fr 1fr 1fr;gap:8px;margin-bottom:10px">
              <div>
                <label class="lab" style="font-size:10px">Assign To</label>
                <select v-model="assignToInput" class="field" style="font-size:12px">
                  <option value="Entire Class">Entire Class (All Students)</option>
                  <option value="Rahul Sharma">Rahul Sharma</option>
                  <option value="Diya Rao">Diya Rao</option>
                  <option value="Kabir Joshi">Kabir Joshi</option>
                </select>
              </div>
              <div>
                <label class="lab" style="font-size:10px">Time Limit (Mins)</label>
                <input v-model.number="timeLimitInput" type="number" class="field" style="font-size:12px" min="5" max="60">
              </div>
              <div>
                <label class="lab" style="font-size:10px">Max Attempts</label>
                <input v-model.number="maxAttemptsInput" type="number" class="field" style="font-size:12px" min="1" max="5">
              </div>
            </div>

            <button
              class="btn grad magnetic"
              type="button"
              style="width:100%;justify-content:center"
              :disabled="isSaving"
              @click="handleCreateAndAssign"
            >
              {{ isSaving ? 'Assigning...' : `Assign Quiz (${generatedQuestions.length} Questions)` }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import TutorEmptyState from '../../components/tutor/TutorEmptyState.vue'
import TutorPagination from '../../components/tutor/TutorPagination.vue'
import TutorSegmentedControl from '../../components/tutor/TutorSegmentedControl.vue'
import { tutorApi } from '../../services/tutorApi'

const props = defineProps({ assignments: { type: Array, required: true } })
const emit = defineEmits(['toast', 'confirm-action'])

const tab = ref('Pending')
const page = ref(1)
const pageSize = 3

const classNameInput = ref('Class 10')
const subjectInput = ref('Mathematics')
const topicInput = ref('Quadratic Equations')
const difficultyInput = ref('medium')
const titleInput = ref('')
const objectiveInput = ref('')

const assignToInput = ref('Entire Class')
const timeLimitInput = ref(15)
const maxAttemptsInput = ref(1)

const isGenerating = ref(false)
const isSaving = ref(false)
const errorMessage = ref('')
const generatedQuestions = ref([])

const totalPages = computed(() => Math.max(1, Math.ceil(props.assignments.length / pageSize)))
const pagedAssignments = computed(() => props.assignments.slice((page.value - 1) * pageSize, page.value * pageSize))

function statusClass(status) {
  return { Submitted: 'done', Pending: '', Late: 'warn', Missing: 'warn' }[status] || ''
}

async function handleAiGenerate() {
  const topic = topicInput.value.trim() || 'Quadratic Equations'
  isGenerating.value = true
  errorMessage.value = ''

  try {
    const res = await tutorApi.aiGenerateQuizFull({
      topic,
      class_name: classNameInput.value,
      subject: subjectInput.value,
      difficulty: difficultyInput.value,
      question_count: 5,
      learning_objective: objectiveInput.value
    })

    if (res.questions && Array.isArray(res.questions) && res.questions.length > 0) {
      generatedQuestions.value = res.questions
      if (!titleInput.value) {
        titleInput.value = `${topic} Quiz`
      }
      emit('toast', `Generated ${res.questions.length} questions for "${topic}". Review and edit before assigning!`)
    } else {
      throw new Error(res.message || 'Did not receive valid questions from AI.')
    }
  } catch (err) {
    errorMessage.value = err.message || 'Failed to generate AI quiz questions.'
    emit('toast', errorMessage.value)
  } finally {
    isGenerating.value = false
  }
}

function addManualQuestion() {
  generatedQuestions.value.push({
    id: generatedQuestions.value.length + 1,
    question: "New Manual Question",
    option_a: "Option 1",
    option_b: "Option 2",
    option_c: "Option 3",
    option_d: "Option 4",
    correct_option: "A",
    explanation: "Explanation for manual question",
    difficulty: difficultyInput.value,
    topic: topicInput.value
  })
}

function deleteQuestion(index) {
  generatedQuestions.value.splice(index, 1)
}

function moveQuestion(index, delta) {
  const newIndex = index + delta
  if (newIndex < 0 || newIndex >= generatedQuestions.value.length) return
  const temp = generatedQuestions.value[index]
  generatedQuestions.value[index] = generatedQuestions.value[newIndex]
  generatedQuestions.value[newIndex] = temp
}

async function handleCreateAndAssign() {
  const title = titleInput.value.trim() || `${topicInput.value} Practice Quiz`
  if (!generatedQuestions.value.length) {
    emit('toast', 'Please generate or add questions first.')
    return
  }

  isSaving.value = true
  try {
    const payload = {
      title,
      subject: subjectInput.value,
      class_name: classNameInput.value,
      topic: topicInput.value,
      time_limit: timeLimitInput.value,
      max_attempts: maxAttemptsInput.value,
      assign_to: assignToInput.value,
      questions: generatedQuestions.value
    }
    const res = await tutorApi.createAndAssignQuiz(payload)
    
    // Add to list immediately so user sees it in left column
    if (props.assignments && Array.isArray(props.assignments)) {
      props.assignments.unshift({
        assignmentId: Date.now(),
        id: Date.now(),
        title: title,
        classLevel: `${classNameInput.value} · ${topicInput.value}`,
        submissions: '0 submissions',
        homeworkStatus: 'Active'
      })
    }

    emit('toast', res.message || `Quiz "${title}" assigned successfully!`)
    titleInput.value = ''
    generatedQuestions.value = []
  } catch (err) {
    emit('toast', err.message || `Quiz "${title}" created and assigned!`)
    generatedQuestions.value = []
  } finally {
    isSaving.value = false
  }
}

function clearGeneratedQuestions() {
  generatedQuestions.value = []
}
</script>


