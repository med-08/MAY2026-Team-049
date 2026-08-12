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

      <!-- Student Homework Submissions & Grading Card -->
      <div class="card glass" style="margin-top:16px;grid-column:1 / -1">
        <div class="ch">
          <h3>Student Homework Submissions (Manual Grading)</h3>
          <span class="eyebrow" style="color:var(--g1)">Review & enter grades</span>
        </div>
        <div v-if="loadingSubmissions" class="py-4 text-center text-slate-400">Loading submissions...</div>
        <TutorEmptyState v-else-if="!submissionsList.length" title="No student submissions pending" />
        <div v-else class="grid" style="grid-template-columns:repeat(auto-fill, minmax(280px, 1fr));gap:12px">
          <div v-for="sub in submissionsList" :key="sub.submission_id" class="p-3 rounded-xl bg-white/5 border border-white/10 flex flex-col justify-between gap-2">
            <div>
              <div class="flex justify-between items-start">
                <span class="font-bold text-sm text-purple-300">{{ sub.assignment_title }}</span>
                <span class="text-xs px-2 py-0.5 rounded-full" :class="sub.status === 'Completed' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-amber-500/20 text-amber-300'">{{ sub.status }}</span>
              </div>
              <p class="text-xs text-slate-300 mt-1">Student: <strong>{{ sub.student_name }}</strong></p>
              <p class="text-xs text-slate-400">Submitted: {{ sub.submission_date }}</p>
              <div v-if="sub.score" class="mt-2 text-xs text-emerald-400 font-semibold">Grade: {{ sub.score }}%</div>
              <p v-if="sub.tutor_feedback" class="text-xs text-slate-300 italic mt-1">"{{ sub.tutor_feedback }}"</p>
            </div>
            <button class="btn sm grad mt-2" type="button" @click="openGradeModal(sub)">
              {{ sub.status === 'Completed' ? 'Edit Grade' : 'Grade Submission' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Grade Submission Modal -->
      <div v-if="selectedSubmission" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="card glass max-w-md w-full p-6 rounded-2xl border border-white/20">
          <h3 class="text-lg font-bold text-white mb-2">Grade Homework Submission</h3>
          <p class="text-xs text-slate-300 mb-4">Student: <strong>{{ selectedSubmission.student_name }}</strong> ({{ selectedSubmission.assignment_title }})</p>
          <div class="space-y-4">
            <div>
              <label class="lab block mb-1">Score / Percentage (0 - 100)</label>
              <input v-model.number="gradeScoreInput" type="number" min="0" max="100" class="field w-full" placeholder="e.g. 85">
            </div>
            <div>
              <label class="lab block mb-1">Tutor Feedback / Comments</label>
              <textarea v-model="gradeFeedbackInput" rows="3" class="field w-full" placeholder="Write feedback for the student..."></textarea>
            </div>
          </div>

          <div class="flex justify-end gap-2 mt-6">
            <button class="btn sm" type="button" @click="closeGradeModal">Cancel</button>
            <button class="btn sm grad" type="button" :disabled="isGrading" @click="submitGrade">
              {{ isGrading ? 'Saving Grade...' : 'Save & Publish Grade' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Monthly Teaching Plans Card -->
      <div class="card glass" style="margin-top:16px;grid-column:1 / -1">
        <div class="ch">
          <div>
            <h3>Monthly Curriculum / Teaching Plans</h3>
            <span class="eyebrow" style="color:var(--g1)">Plan and publish upcoming topics</span>
          </div>
          <button class="btn sm grad" type="button" @click="showPlanModal = true">+ Create Plan</button>
        </div>
        <TutorEmptyState v-if="!teachingPlansList.length" title="No monthly teaching plans created" />
        <div v-else class="grid" style="grid-template-columns:repeat(auto-fill, minmax(280px, 1fr));gap:12px">
          <div v-for="plan in teachingPlansList" :key="plan.plan_id" class="p-3 rounded-xl bg-white/5 border border-white/10 flex flex-col justify-between">
            <div>
              <div class="flex justify-between items-center mb-1">
                <span class="font-bold text-sm text-purple-300">{{ plan.topic_name }}</span>
                <span class="text-xs px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300">{{ plan.month }}</span>
              </div>
              <p class="text-xs text-slate-300">Subject: {{ plan.subject_name }}</p>
              <p class="text-xs text-slate-400 mt-1">Planned Date: {{ plan.planned_date }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Create Teaching Plan Modal -->
      <div v-if="showPlanModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="card glass max-w-md w-full p-6 rounded-2xl border border-white/20">
          <h3 class="text-lg font-bold text-white mb-4">Create Monthly Teaching Plan</h3>
          <div class="space-y-4">
            <div>
              <label class="lab block mb-1">Topic Name / Chapter</label>
              <input v-model="planTopicInput" class="field w-full" placeholder="e.g. Quadratic Equations & Polynomials">
            </div>
            <div>
              <label class="lab block mb-1">Month / Target Period</label>
              <input v-model="planMonthInput" class="field w-full" placeholder="e.g. August 2026">
            </div>
            <div>
              <label class="lab block mb-1">Planned Date</label>
              <input v-model="planDateInput" type="date" class="field w-full">
            </div>
          </div>
          <div class="flex justify-end gap-2 mt-6">
            <button class="btn sm" type="button" @click="showPlanModal = false">Cancel</button>
            <button class="btn sm grad" type="button" :disabled="isSavingPlan" @click="submitTeachingPlan">
              {{ isSavingPlan ? 'Publishing Plan...' : 'Publish Plan' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Weekly Learning Summaries Card -->
      <div class="card glass" style="margin-top:16px;grid-column:1 / -1">
        <div class="ch">
          <div>
            <h3>Weekly Learning Summaries (For Parents)</h3>
            <span class="eyebrow" style="color:var(--g1)">Structured weekly progress reports</span>
          </div>
          <button class="btn sm grad" type="button" @click="showSummaryModal = true">+ Write Summary</button>
        </div>
        <TutorEmptyState v-if="!weeklySummariesList.length" title="No weekly summaries published yet" />
        <div v-else class="grid" style="grid-template-columns:repeat(auto-fill, minmax(300px, 1fr));gap:12px">
          <div v-for="sum in weeklySummariesList" :key="sum.summary_id" class="p-4 rounded-xl bg-white/5 border border-white/10 flex flex-col justify-between gap-2">
            <div>
              <div class="flex justify-between items-center mb-1">
                <span class="font-bold text-sm text-emerald-300">Student: {{ sum.student_name }}</span>
                <span class="text-xs text-slate-400">{{ sum.created_at }}</span>
              </div>
              <p class="text-xs text-slate-300"><strong>Topics:</strong> {{ sum.topics_taught }}</p>
              <p class="text-xs text-slate-300 mt-1"><strong>Homework:</strong> {{ sum.homework_summary }}</p>
              <p v-if="sum.areas_for_improvement" class="text-xs text-amber-300 mt-1"><strong>Improvement Areas:</strong> {{ sum.areas_for_improvement }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Create Weekly Summary Modal -->
      <div v-if="showSummaryModal" class="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
        <div class="card glass max-w-md w-full p-6 rounded-2xl border border-white/20">
          <h3 class="text-lg font-bold text-white mb-4">Write Weekly Learning Summary</h3>
          <div class="space-y-3">
            <div>
              <label class="lab block mb-1">Student ID</label>
              <input v-model.number="summaryStudentId" type="number" class="field w-full" placeholder="e.g. 1">
            </div>
            <div>
              <label class="lab block mb-1">Topics Taught This Week</label>
              <textarea v-model="summaryTopicsInput" rows="2" class="field w-full" placeholder="e.g. Algebra basics, quadratic formula"></textarea>
            </div>
            <div>
              <label class="lab block mb-1">Homework Summary</label>
              <textarea v-model="summaryHomeworkInput" rows="2" class="field w-full" placeholder="e.g. Completed worksheet 4.1"></textarea>
            </div>
            <div>
              <label class="lab block mb-1">Areas for Improvement</label>
              <textarea v-model="summaryImprovementInput" rows="2" class="field w-full" placeholder="e.g. Needs practice in speed factoring"></textarea>
            </div>
          </div>
          <div class="flex justify-end gap-2 mt-6">
            <button class="btn sm" type="button" @click="showSummaryModal = false">Cancel</button>
            <button class="btn sm grad" type="button" :disabled="isSavingSummary" @click="submitWeeklySummary">
              {{ isSavingSummary ? 'Publishing Summary...' : 'Publish Summary' }}
            </button>
          </div>
        </div>
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

// Submissions & Homework Grading
const submissionsList = ref([])
const loadingSubmissions = ref(false)
const selectedSubmission = ref(null)
const gradeScoreInput = ref(85)
const gradeFeedbackInput = ref('')
const isGrading = ref(false)

async function fetchSubmissions() {
  loadingSubmissions.value = true
  try {
    const res = await tutorApi.getSubmissions()
    if (res.success && res.data && Array.isArray(res.data.submissions)) {
      submissionsList.value = res.data.submissions
    }
  } catch (err) {
    console.error("Submissions fetch error:", err)
  } finally {
    loadingSubmissions.value = false
  }
}

function openGradeModal(sub) {
  selectedSubmission.value = sub
  gradeScoreInput.value = sub.score || 85
  gradeFeedbackInput.value = sub.tutor_feedback || ''
}

function closeGradeModal() {
  selectedSubmission.value = null
}

async function submitGrade() {
  if (!selectedSubmission.value) return
  isGrading.value = true
  try {
    const res = await tutorApi.gradeSubmission(selectedSubmission.value.submission_id, {
      score: gradeScoreInput.value,
      feedback: gradeFeedbackInput.value,
      status: 'Completed'
    })
    emit('toast', res.message || 'Submission graded successfully!')
    fetchSubmissions()
    closeGradeModal()
  } catch (err) {
    emit('toast', err.message || 'Failed to grade submission.')
  } finally {
    isGrading.value = false
  }
}

// Teaching Plans State & Methods
const teachingPlansList = ref([])
const showPlanModal = ref(false)
const planTopicInput = ref('')
const planMonthInput = ref('August 2026')
const planDateInput = ref(new Date().toISOString().split('T')[0])
const isSavingPlan = ref(false)

async function fetchTeachingPlans() {
  try {
    const res = await tutorApi.getTeachingPlans()
    if (res.success && res.data && Array.isArray(res.data.plans)) {
      teachingPlansList.value = res.data.plans
    }
  } catch (err) {
    console.error("Teaching plans fetch error:", err)
  }
}

async function submitTeachingPlan() {
  if (!planTopicInput.value.trim()) return
  isSavingPlan.value = true
  try {
    const res = await tutorApi.createTeachingPlan({
      topic_name: planTopicInput.value.trim(),
      month: planMonthInput.value,
      planned_date: planDateInput.value,
      subject_id: 1
    })
    emit('toast', res.message || 'Teaching plan created!')
    planTopicInput.value = ''
    showPlanModal.value = false
    fetchTeachingPlans()
  } catch (err) {
    emit('toast', err.message || 'Failed to create teaching plan.')
  } finally {
    isSavingPlan.value = false
  }
}

// Weekly Summaries State & Methods
const weeklySummariesList = ref([])
const showSummaryModal = ref(false)
const summaryStudentId = ref(1)
const summaryTopicsInput = ref('')
const summaryHomeworkInput = ref('')
const summaryImprovementInput = ref('')
const isSavingSummary = ref(false)

async function fetchWeeklySummaries() {
  try {
    const res = await tutorApi.getWeeklySummaries()
    if (res.success && res.data && Array.isArray(res.data.summaries)) {
      weeklySummariesList.value = res.data.summaries
    }
  } catch (err) {
    console.error("Weekly summaries fetch error:", err)
  }
}

async function submitWeeklySummary() {
  isSavingSummary.value = true
  try {
    const res = await tutorApi.createWeeklySummary({
      student_id: summaryStudentId.value,
      topics_taught: summaryTopicsInput.value,
      homework_summary: summaryHomeworkInput.value,
      areas_for_improvement: summaryImprovementInput.value
    })
    emit('toast', res.message || 'Weekly summary published for parents!')
    summaryTopicsInput.value = ''
    summaryHomeworkInput.value = ''
    summaryImprovementInput.value = ''
    showSummaryModal.value = false
    fetchWeeklySummaries()
  } catch (err) {
    emit('toast', err.message || 'Failed to publish weekly summary.')
  } finally {
    isSavingSummary.value = false
  }
}

import { onMounted } from 'vue'
onMounted(() => {
  fetchSubmissions()
  fetchTeachingPlans()
  fetchWeeklySummaries()
})
</script>


