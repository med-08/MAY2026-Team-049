<template>
  <section class="view on">
    <div class="grid g2col reveal" style="grid-template-columns:1.4fr 1fr">
      <div class="card glass">
        <div class="ch"><h3>Assignments</h3></div>
        <TutorEmptyState v-if="!assignments.length" title="No assignments" />
        <div v-for="a in assignments" :key="a.assignmentId" class="row">
          <div class="g1">
            <div class="t">{{ a.title }}</div>
            <div class="s">{{ a.classLevel }} - {{ a.submissions }}</div>
          </div>
          <span class="badge" :class="statusClass(a.homeworkStatus)">{{ a.homeworkStatus }}</span>
          <button class="btn sm" @click="remove(a.assignmentId)">Delete</button>
        </div>
      </div>

      <div class="card glass">
        <div class="ch"><h3>Create assignment / quiz</h3></div>
        <label class="lab">Type</label>
        <select v-model="type" class="field" style="margin-bottom:12px"><option>Assignment</option><option>Quiz</option></select>
        <label class="lab">Title</label>
        <input v-model="title" class="field" style="margin-bottom:12px">
        <template v-if="type === 'Assignment'">
          <label class="lab">Session</label>
          <select v-model="sessionId" class="field" style="margin-bottom:12px">
            <option value="">Choose session</option>
            <option v-for="s in sessions" :key="s.id" :value="s.id">{{ s.subject }} - {{ s.date }} - {{ s.time }}</option>
          </select>
          <label class="lab">Description</label>
          <textarea v-model="description" class="field" rows="3" style="margin-bottom:12px"></textarea>
          <label class="lab">Due date</label>
          <input v-model="dueDate" type="date" class="field" style="margin-bottom:12px">
        </template>
        <template v-else>
          <label class="lab">Subject</label>
          <select v-model="subjectId" class="field" style="margin-bottom:12px">
            <option value="">Choose subject</option>
            <option v-for="s in uniqueSubjects" :key="s.subjectId" :value="s.subjectId">{{ s.subject }}</option>
          </select>
          <label class="lab">Assign to student</label>
          <select v-model="assignedStudentId" class="field" style="margin-bottom:12px">
            <option value="">Choose assigned student</option>
            <option v-for="student in studentsForSubject" :key="student.studentId" :value="student.studentId">{{ student.name }}</option>
          </select>
          <label class="lab">Topic / concept</label>
          <input v-model="topic" class="field" placeholder="Exact topic, e.g. Vowels" style="margin-bottom:12px">
          <label class="lab">Difficulty</label>
          <select v-model="difficulty" class="field" style="margin-bottom:12px">
            <option>Easy</option><option>Medium</option><option>Hard</option>
          </select>
          <label class="lab">Week</label>
          <input v-model.number="week" type="number" min="1" class="field" style="margin-bottom:12px">
        </template>
        <button class="btn grad" @click="create">Create</button>
        <p v-if="message" class="eyebrow" style="margin-top:10px">{{ message }}</p>
      </div>
    </div>

    <div class="card glass reveal" style="margin-top:18px">
      <div class="ch"><h3>Quiz questions</h3></div>
      <p v-if="!quizzes.length" class="eyebrow">Create a quiz first.</p>
      <template v-else>
        <select v-model="question.quizId" class="field" style="margin-bottom:12px">
          <option value="">Choose quiz</option>
          <option v-for="q in quizzes" :key="q.quiz_id" :value="q.quiz_id">{{ q.title }} - {{ q.subject }}</option>
        </select>
        <input v-model="question.text" class="field" placeholder="Question" style="margin-bottom:8px">
        <div class="grid" style="grid-template-columns:1fr 1fr;gap:8px">
          <input v-model="question.a" class="field" placeholder="Option A">
          <input v-model="question.b" class="field" placeholder="Option B">
          <input v-model="question.c" class="field" placeholder="Option C">
          <input v-model="question.d" class="field" placeholder="Option D">
        </div>
        <select v-model="question.correct" class="field" style="margin:10px 0">
          <option value="">Correct option</option>
          <option>A</option><option>B</option><option>C</option><option>D</option>
        </select>
        <textarea v-model="question.explanation" class="field" rows="2" placeholder="Explanation" style="margin-bottom:10px"></textarea>
        <button class="btn grad" @click="addQuestion">Add question</button>
      </template>

      <div style="border-top:1px solid var(--border);margin-top:16px;padding-top:16px">
        <div class="ch"><h3>AI generate questions</h3><span class="eyebrow">real tutor data</span></div>
        <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px">
          <select v-model="aiSubject" class="field">
            <option value="">Choose subject</option>
            <option v-for="subject in aiSubjects" :key="subject" :value="subject">{{ subject }}</option>
          </select>
          <input v-model="aiTopic" class="field" placeholder="Topic">
          <select v-model="aiDifficulty" class="field"><option>Easy</option><option>Medium</option><option>Hard</option></select>
          <input v-model.number="aiCount" type="number" min="1" max="10" class="field">
        </div>
        <button class="btn grad" style="margin-top:10px" :disabled="aiLoading" @click="generateAiQuestions">{{ aiLoading ? 'Generating...' : 'AI generate' }}</button>

        <div v-if="aiQuestions.length" class="quiz-preview">
          <div class="ch"><h3>{{ aiQuizTitle }}</h3><span class="eyebrow">{{ aiSubjectLabel }} - {{ aiDifficulty }} - {{ aiQuestions.length }} questions</span></div>
          <div v-for="(q, i) in aiQuestions" :key="i" class="quiz-question">
            <p class="t">{{ i + 1 }}. {{ q.question }}</p>
            <label v-for="letter in optionLetters" :key="letter" class="quiz-option">
              <input type="radio" :name="`preview-${i}`" disabled>
              <span>{{ letter }}. {{ q[`option_${letter.toLowerCase()}`] }}</span>
            </label>
            <p class="s">Answer: {{ q.correct_option }}<span v-if="q.explanation"> - {{ q.explanation }}</span></p>
          </div>
          <div class="flex flex-wrap items-center gap-2" style="margin-top:12px">
            <select v-model="saveQuizId" class="field" style="max-width:280px">
              <option value="">Choose quiz to save into</option>
              <option v-for="q in quizzes" :key="q.quiz_id" :value="q.quiz_id">{{ q.title }} - {{ q.subject }}</option>
            </select>
            <button class="btn grad" :disabled="savingAi" @click="saveAiQuestions">{{ savingAi ? 'Saving...' : 'Save Questions to Quiz' }}</button>
          </div>
        </div>
      </div>

      <div v-if="selectedQuiz" class="quiz-preview" style="border-top:1px solid var(--border);margin-top:16px;padding-top:16px">
          <div class="ch"><h3>{{ selectedQuiz.title }}</h3><span class="eyebrow">{{ selectedQuiz.subject }} - {{ selectedQuiz.topic || 'Topic not set' }} - {{ selectedQuiz.difficulty || 'Difficulty not set' }} - {{ selectedQuiz.questionCount || 0 }} questions</span></div>
        <p v-if="!selectedQuiz.questions?.length" class="eyebrow">No questions saved yet.</p>
        <div v-for="(q, i) in selectedQuiz.questions" :key="q.id" class="quiz-question">
          <p class="t">{{ i + 1 }}. {{ q.question }}</p>
          <p class="s">A. {{ q.option_a }}</p>
          <p class="s">B. {{ q.option_b }}</p>
          <p class="s">C. {{ q.option_c }}</p>
          <p class="s">D. {{ q.option_d }}</p>
        </div>
      </div>
    </div>

    <div class="card glass reveal" style="margin-top:18px">
      <div class="ch"><h3>Flashcards</h3><span class="eyebrow">AI generated from topic + class level + context</span></div>
      <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px">
        <select v-model="aiFcSubjectId" class="field">
          <option value="">Choose subject</option>
          <option v-for="s in uniqueSubjects" :key="s.subjectId" :value="s.subjectId">{{ s.subject }}</option>
        </select>
        <select v-model="aiFcAssignedStudentId" class="field">
          <option value="">All students (subject-wide)</option>
          <option v-for="student in fcStudentsForSubject" :key="student.studentId" :value="student.studentId">{{ student.name }}</option>
        </select>
        <input v-model="aiFcTopic" class="field" placeholder="Exact topic, e.g. Vowels">
        <input v-model="aiFcClassLevel" class="field" placeholder="Class level, e.g. Grade 5">
        <input v-model.number="aiFcCount" type="number" min="1" max="20" class="field" placeholder="Card count">
      </div>
      <textarea v-model="aiFcContext" class="field" rows="2" style="margin-top:8px" placeholder="Context / description for the AI (optional)"></textarea>
      <button class="btn grad" style="margin-top:10px" :disabled="aiFcLoading" @click="generateAiFlashcards">{{ aiFcLoading ? 'Generating...' : 'AI Generate Flashcards' }}</button>

      <div v-if="aiFlashcards.length" class="quiz-preview">
        <div class="ch"><h3>{{ aiFcSetTitle }}</h3><span class="eyebrow">{{ aiFcClassLevel || 'Class level not set' }} - {{ aiFlashcards.length }} cards</span></div>
        <div v-for="(c, i) in aiFlashcards" :key="i" class="quiz-question">
          <p class="t">{{ i + 1 }}. {{ c.front }}</p>
          <p class="s">Answer: {{ c.back }}</p>
          <p v-if="c.explanation" class="s">{{ c.explanation }}</p>
        </div>
        <button class="btn grad" style="margin-top:10px" :disabled="savingFcAi" @click="saveAiFlashcards">{{ savingFcAi ? 'Saving...' : 'Save Flashcards for Students' }}</button>
      </div>

      <div v-if="flashcardSets.length" style="border-top:1px solid var(--border);margin-top:16px;padding-top:16px">
        <div class="ch"><h3>Saved Flashcard Sets</h3></div>
        <select v-model="saveFlashcardSetId" class="field" style="margin-bottom:12px">
          <option value="">Choose a set to preview</option>
          <option v-for="s in flashcardSets" :key="s.set_id" :value="s.set_id">{{ s.title }} - {{ s.subject }} ({{ s.cardCount }} cards){{ s.assignedStudent ? ' - ' + s.assignedStudent : '' }}</option>
        </select>
        <div v-if="selectedFlashcardSet">
          <p v-if="!selectedFlashcardSet.cards?.length" class="eyebrow">No cards saved yet.</p>
          <div v-for="(c, i) in selectedFlashcardSet.cards" :key="c.id" class="quiz-question">
            <p class="t">{{ i + 1 }}. {{ c.front }}</p>
            <p class="s">Answer: {{ c.back }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import TutorEmptyState from '../../components/tutor/TutorEmptyState.vue'
import { tutorApi } from '../../services/tutorApi'

const props = defineProps({ assignments: { type: Array, required: true }, sessions: { type: Array, default: () => [] }, subjects: { type: Array, default: () => [] } })
const emit = defineEmits(['toast'])
const type = ref('Assignment')
const title = ref('')
const sessionId = ref('')
const subjectId = ref('')
const assignedStudentId = ref('')
const topic = ref('')
const difficulty = ref('Medium')
const description = ref('')
const dueDate = ref('')
const week = ref(1)
const classLevel = ref('')
const context = ref('')
const message = ref('')
const quizzes = ref([])
const aiSubject = ref('')
const aiTopic = ref('')
const aiDifficulty = ref('Medium')
const aiCount = ref(5)
const aiQuestions = ref([])
const aiLoading = ref(false)
const saveQuizId = ref('')
const savingAi = ref(false)
const question = ref({ quizId: '', text: '', a: '', b: '', c: '', d: '', correct: '', explanation: '' })

const flashcardSets = ref([])
const aiFcSubjectId = ref('')
const aiFcAssignedStudentId = ref('')
const aiFcTopic = ref('')
const aiFcClassLevel = ref('')
const aiFcContext = ref('')
const aiFcCount = ref(10)
const aiFlashcards = ref([])
const aiFcLoading = ref(false)
const saveFlashcardSetId = ref('')
const savingFcAi = ref(false)
const assignments = computed(() => props.assignments)
const uniqueSubjects = computed(() => {
  const m = new Map()
  props.sessions.forEach(s => m.set(s.subjectId, { subjectId: s.subjectId, subject: s.subject }))
  return [...m.values()]
})
const studentsForSubject = computed(() => {
  const m = new Map()
  props.sessions
    .filter(s => !subjectId.value || String(s.subjectId) === String(subjectId.value))
    .forEach(s => (s.students || []).forEach(st => {
      const id = st.studentId || st.student_id || st.id
      if (id) m.set(id, { studentId: id, name: st.name || st.student_name || `Student #${id}` })
    }))
  return [...m.values()]
})
const aiSubjects = computed(() => props.subjects.length ? props.subjects : uniqueSubjects.value.map(s => s.subject))
const optionLetters = ['A', 'B', 'C', 'D']
const aiSubjectLabel = computed(() => aiSubject.value || uniqueSubjects.value.find(s => String(s.subjectId) === String(subjectId.value))?.subject || 'Subject')
const aiQuizTitle = computed(() => `${aiSubjectLabel.value}: ${aiTopic.value || title.value || 'Generated Quiz'}`)
const selectedQuiz = computed(() => quizzes.value.find(q => String(q.quiz_id) === String(question.value.quizId || saveQuizId.value)))

const aiFcSubjectLabel = computed(() => uniqueSubjects.value.find(s => String(s.subjectId) === String(aiFcSubjectId.value))?.subject || 'Subject')
const aiFcSetTitle = computed(() => `${aiFcSubjectLabel.value}: ${aiFcTopic.value || 'Flashcards'}`)
const fcStudentsForSubject = computed(() => {
  const m = new Map()
  props.sessions
    .filter(s => !aiFcSubjectId.value || String(s.subjectId) === String(aiFcSubjectId.value))
    .forEach(s => (s.students || []).forEach(st => {
      const id = st.studentId || st.student_id || st.id
      if (id) m.set(id, { studentId: id, name: st.name || st.student_name || `Student #${id}` })
    }))
  return [...m.values()]
})
const selectedFlashcardSet = computed(() => flashcardSets.value.find(s => String(s.set_id) === String(saveFlashcardSetId.value)))

function statusClass(s) { return { Submitted: 'done', Late: 'warn', Missing: 'warn' }[s] || '' }
async function loadQuizzes() { try { quizzes.value = (await tutorApi.getQuizzes()).quizzes || [] } catch { quizzes.value = [] } }
async function loadFlashcardSets() { try { flashcardSets.value = (await tutorApi.getFlashcardSets()).sets || [] } catch { flashcardSets.value = [] } }
onMounted(loadQuizzes)
onMounted(loadFlashcardSets)

async function create() {
  try {
    if (!title.value) throw new Error('Enter a title')
    if (type.value === 'Assignment') {
      if (!sessionId.value) throw new Error('Choose a session')
      await tutorApi.createAssignment({ session_id: Number(sessionId.value), title: title.value, description: description.value, due_date: dueDate.value })
    } else {
      if (!subjectId.value) throw new Error('Choose a subject')
      if (!topic.value.trim()) throw new Error('Enter the exact topic/concept')
      const created = await tutorApi.createQuiz({
        subject_id: Number(subjectId.value),
        assigned_student_id: assignedStudentId.value ? Number(assignedStudentId.value) : null,
        title: title.value,
        topic: topic.value,
        difficulty: difficulty.value,
        week_number: week.value
      })
      await loadQuizzes()
      const id = created?.quiz?.quiz_id || created?.data?.quiz?.quiz_id
      if (id) {
        question.value.quizId = id
        saveQuizId.value = id
      }
    }
    message.value = `${type.value} created`
    emit('toast', `${type.value} created in database`)
    title.value = ''
    description.value = ''
    dueDate.value = ''
    assignedStudentId.value = ''
    topic.value = ''
  } catch (e) {
    message.value = e.message
  }
}

async function addQuestion() {
  try {
    if (!question.value.quizId || !question.value.text || !question.value.correct) throw new Error('Choose quiz, enter question and correct option')
    await tutorApi.addQuizQuestion(question.value.quizId, {
      question: question.value.text,
      option_a: question.value.a,
      option_b: question.value.b,
      option_c: question.value.c,
      option_d: question.value.d,
      correct_option: question.value.correct,
      explanation: question.value.explanation
    })
    message.value = 'Question added'
    question.value = { ...question.value, text: '', a: '', b: '', c: '', d: '', correct: '', explanation: '' }
    await loadQuizzes()
    emit('toast', 'Quiz question saved')
  } catch (e) {
    message.value = e.message
  }
}

async function generateAiQuestions() {
  aiLoading.value = true
  aiQuestions.value = []
  try {
    const r = await tutorApi.aiGenerateQuestions({ subject: aiSubjectLabel.value, topic: aiTopic.value || title.value, difficulty: aiDifficulty.value, question_count: aiCount.value })
    aiQuestions.value = r.questions || r.data?.questions || []
    emit('toast', 'AI questions generated')
  } catch (e) {
    message.value = e.message
    emit('toast', e.message)
  } finally {
    aiLoading.value = false
  }
}

async function saveAiQuestions() {
  try {
    if (!saveQuizId.value) throw new Error('Choose a quiz to save into')
    savingAi.value = true
    for (const q of aiQuestions.value) {
      await tutorApi.addQuizQuestion(saveQuizId.value, q)
    }
    await loadQuizzes()
    emit('toast', 'AI questions saved to quiz')
  } catch (e) {
    message.value = e.message
    emit('toast', e.message)
  } finally {
    savingAi.value = false
  }
}

async function generateAiFlashcards() {
  aiFcLoading.value = true
  aiFlashcards.value = []
  try {
    const r = await tutorApi.aiGenerateFlashcards({
      subject: aiFcSubjectLabel.value,
      topic: aiFcTopic.value,
      class_level: aiFcClassLevel.value,
      context: aiFcContext.value,
      count: aiFcCount.value
    })
    aiFlashcards.value = r.flashcards || r.data?.flashcards || []
    emit('toast', 'AI flashcards generated')
  } catch (e) {
    message.value = e.message
    emit('toast', e.message)
  } finally {
    aiFcLoading.value = false
  }
}

async function saveAiFlashcards() {
  try {
    if (!aiFcSubjectId.value) throw new Error('Choose a subject')
    if (!aiFcTopic.value.trim()) throw new Error('Enter the exact topic/concept')
    if (!aiFlashcards.value.length) throw new Error('Generate flashcards first')
    savingFcAi.value = true
    const created = await tutorApi.createFlashcardSet({
      subject_id: Number(aiFcSubjectId.value),
      assigned_student_id: aiFcAssignedStudentId.value ? Number(aiFcAssignedStudentId.value) : null,
      title: aiFcSetTitle.value,
      topic: aiFcTopic.value,
      class_level: aiFcClassLevel.value,
      context: aiFcContext.value
    })
    const setId = created?.set?.set_id || created?.data?.set?.set_id
    if (!setId) throw new Error('Flashcard set was not created')
    for (const card of aiFlashcards.value) {
      await tutorApi.addFlashcard(setId, card)
    }
    saveFlashcardSetId.value = setId
    await loadFlashcardSets()
    emit('toast', 'Flashcards saved for students')
  } catch (e) {
    message.value = e.message
    emit('toast', e.message)
  } finally {
    savingFcAi.value = false
  }
}

async function remove(id) {
  try {
    await tutorApi.deleteAssignment(id)
    emit('toast', 'Assignment deleted')
    location.reload()
  } catch (e) {
    emit('toast', e.message)
  }
}
</script>

<style scoped>
.quiz-preview { margin-top: 12px; }
.quiz-question { border: 1px solid var(--border); border-radius: 10px; padding: 12px; margin-top: 10px; }
.quiz-option { display: flex; gap: 8px; align-items: center; padding: 6px 0; color: var(--text); }
</style>
