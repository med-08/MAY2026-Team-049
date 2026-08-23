<script setup>
import { ref, onMounted, computed } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import { studentApi } from '../../services/studentApi'
import { authApi } from '../../services/authApi'

const loading = ref(true)
const error = ref('')
const flashcardSets = ref([])
const selectedSetId = ref('')
const flashcards = ref([])
const flashcardIndex = ref(0)
const flashcardFlipped = ref(false)
const currentFlashcard = computed(() => flashcards.value[flashcardIndex.value] || null)
const selectedFlashcardSet = computed(() => flashcardSets.value.find((s) => String(s.set_id) === String(selectedSetId.value)) || null)

const subjects = ref([])
const genSubjectId = ref('')
const genTopic = ref('')
const genClassLevel = ref('')
const genContext = ref('')
const genCount = ref(10)
const genCards = ref([])
const genLoading = ref(false)
const savingGen = ref(false)
const genMessage = ref('')

async function loadFlashcardCards() {
  if (!selectedSetId.value) {
    flashcards.value = []
    return
  }
  try {
    const r = await studentApi.getFlashcardSetCards(selectedSetId.value)
    flashcards.value = r.data?.cards || []
    flashcardIndex.value = 0
    flashcardFlipped.value = false
  } catch (e) {
    error.value = e.message || 'Unable to load flashcards.'
    flashcards.value = []
  }
}

async function loadFlashcardSets() {
  try {
    const r = await studentApi.getFlashcardSets()
    flashcardSets.value = r.data?.sets || []
    if (!selectedSetId.value && flashcardSets.value.length) {
      selectedSetId.value = flashcardSets.value[0].set_id
    }
    await loadFlashcardCards()
  } catch (e) {
    error.value = e.message || 'Unable to load flashcard sets.'
  }
}

function moveFlashcard(step) {
  if (!flashcards.value.length) return
  flashcardIndex.value = (flashcardIndex.value + step + flashcards.value.length) % flashcards.value.length
  flashcardFlipped.value = false
}

async function generateOwnFlashcards() {
  genMessage.value = ''
  if (!genSubjectId.value) { genMessage.value = 'Choose a subject.'; return }
  if (!genTopic.value.trim()) { genMessage.value = 'Enter the exact topic you want to practice.'; return }
  genLoading.value = true
  genCards.value = []
  try {
    const subjectLabel = subjects.value.find((s) => String(s.subject_id) === String(genSubjectId.value))?.subject_name || ''
    const r = await studentApi.aiGenerateFlashcards({
      subject: subjectLabel,
      topic: genTopic.value,
      class_level: genClassLevel.value,
      context: genContext.value,
      count: genCount.value
    })
    genCards.value = r.data?.flashcards || []
  } catch (e) {
    genMessage.value = e.message || 'Unable to generate flashcards.'
  } finally {
    genLoading.value = false
  }
}

async function saveOwnFlashcards() {
  if (!genCards.value.length) return
  savingGen.value = true
  genMessage.value = ''
  try {
    const subjectLabel = subjects.value.find((s) => String(s.subject_id) === String(genSubjectId.value))?.subject_name || 'Subject'
    const r = await studentApi.createOwnFlashcardSet({
      subject_id: Number(genSubjectId.value),
      title: `${subjectLabel}: ${genTopic.value}`,
      topic: genTopic.value,
      class_level: genClassLevel.value,
      context: genContext.value,
      cards: genCards.value
    })
    const newSetId = r.data?.set_id
    genCards.value = []
    genTopic.value = ''
    genClassLevel.value = ''
    genContext.value = ''
    await loadFlashcardSets()
    if (newSetId) selectedSetId.value = newSetId
    await loadFlashcardCards()
    genMessage.value = 'Saved! Scroll up to practice.'
  } catch (e) {
    genMessage.value = e.message || 'Unable to save flashcards.'
  } finally {
    savingGen.value = false
  }
}

onMounted(async () => {
  try {
    const [setsRes, subjectsRes] = await Promise.all([
      studentApi.getFlashcardSets(),
      authApi.getSubjects()
    ])
    flashcardSets.value = setsRes.data?.sets || []
    subjects.value = subjectsRes.data || []
    if (flashcardSets.value.length) {
      selectedSetId.value = flashcardSets.value[0].set_id
      await loadFlashcardCards()
    }
  } catch (e) {
    error.value = e.message || 'Unable to load flashcard sets.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <PageHeader
      title="Flashcards"
      subtitle="Practice with flashcards your tutor made, or generate your own to self-quiz."
    />

    <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      <p v-if="loading" class="text-sm text-slate-500">Loading flashcards...</p>
      <p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>

      <template v-else>
        <div v-if="!flashcardSets.length" class="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 text-center text-slate-500">
          No flashcards yet. Generate your own below, or wait for your tutor to make a set.
        </div>

        <div v-else class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <div class="flex items-center justify-between gap-3">
            <div>
              <h3 class="text-lg font-semibold text-slate-800">{{ selectedFlashcardSet?.title }}</h3>
              <p v-if="selectedFlashcardSet" class="text-sm text-slate-500 mt-1">
                {{ selectedFlashcardSet.subject }} - {{ selectedFlashcardSet.topic }}
                <span v-if="selectedFlashcardSet.class_level"> - {{ selectedFlashcardSet.class_level }}</span>
              </p>
            </div>
            <span v-if="flashcards.length" class="text-xs text-slate-400 shrink-0">{{ flashcardIndex + 1 }} / {{ flashcards.length }}</span>
          </div>

          <select
            v-model="selectedSetId"
            class="mt-3 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm text-slate-700"
            @change="loadFlashcardCards()"
          >
            <option v-for="s in flashcardSets" :key="s.set_id" :value="s.set_id">{{ s.subject }} - {{ s.topic }} ({{ s.cardCount }} cards)</option>
          </select>

          <div
            v-if="currentFlashcard"
            class="mt-4 rounded-2xl border border-slate-200 p-5 min-h-[150px] cursor-pointer"
            @click="flashcardFlipped = !flashcardFlipped"
          >
            <p class="text-xs font-semibold text-brand-blue">{{ flashcardFlipped ? 'Answer' : 'Question' }}</p>
            <p class="mt-3 text-sm leading-6 text-slate-700">
              {{ flashcardFlipped ? currentFlashcard.back : currentFlashcard.front }}
            </p>
            <p v-if="flashcardFlipped && currentFlashcard.explanation" class="mt-3 text-sm text-slate-500">
              {{ currentFlashcard.explanation }}
            </p>
          </div>
          <p v-else class="mt-4 text-sm text-slate-500">This set has no cards saved yet.</p>

          <div v-if="flashcards.length" class="flex items-center gap-2 mt-4">
            <button class="px-4 py-2 rounded-xl border border-slate-200 text-sm font-semibold" @click="moveFlashcard(-1)">Previous</button>
            <button class="flex-1 px-4 py-2 rounded-xl bg-brand-blue text-white text-sm font-semibold" @click="flashcardFlipped = !flashcardFlipped">Reveal</button>
            <button class="px-4 py-2 rounded-xl border border-slate-200 text-sm font-semibold" @click="moveFlashcard(1)">Next</button>
          </div>
        </div>

        <div class="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h3 class="text-lg font-semibold text-slate-800">Generate Your Own Flashcards</h3>
          <p class="text-xs text-slate-500 mt-1 mb-3">Enter a topic to practice and AI will make flashcards just for you.</p>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
            <select v-model="genSubjectId" class="rounded-lg border border-slate-200 px-3 py-2 text-sm">
              <option value="">Choose subject</option>
              <option v-for="s in subjects" :key="s.subject_id" :value="s.subject_id">{{ s.subject_name }}</option>
            </select>
            <input v-model="genTopic" class="rounded-lg border border-slate-200 px-3 py-2 text-sm" placeholder="Exact topic, e.g. Vowels">
            <input v-model="genClassLevel" class="rounded-lg border border-slate-200 px-3 py-2 text-sm" placeholder="Class level (optional)">
            <input v-model.number="genCount" type="number" min="1" max="20" class="rounded-lg border border-slate-200 px-3 py-2 text-sm" placeholder="Card count">
          </div>
          <textarea v-model="genContext" rows="2" class="mt-2.5 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" placeholder="Context / description for the AI (optional)"></textarea>

          <button
            type="button"
            class="mt-3 px-4 py-2 rounded-xl bg-brand-blue text-white text-sm font-semibold disabled:opacity-50"
            :disabled="genLoading"
            @click="generateOwnFlashcards"
          >{{ genLoading ? 'Generating...' : 'Generate Flashcards' }}</button>

          <p v-if="genMessage" class="mt-3 text-sm" :class="genCards.length || genMessage.startsWith('Saved') ? 'text-emerald-600' : 'text-red-600'">{{ genMessage }}</p>

          <div v-if="genCards.length" class="mt-4 space-y-2">
            <div v-for="(c, i) in genCards" :key="i" class="rounded-xl border border-slate-200 p-3 text-sm">
              <p class="font-medium text-slate-700">{{ i + 1 }}. {{ c.front }}</p>
              <p class="text-slate-500 mt-1">Answer: {{ c.back }}</p>
            </div>
            <button
              type="button"
              class="px-4 py-2 rounded-xl bg-emerald-600 text-white text-sm font-semibold disabled:opacity-50"
              :disabled="savingGen"
              @click="saveOwnFlashcards"
            >{{ savingGen ? 'Saving...' : 'Save & Add to My Flashcards' }}</button>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
