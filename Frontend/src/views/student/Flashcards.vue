<script setup>
import { ref, onMounted } from "vue"
import PageHeader from "../../components/student/PageHeader.vue"
import {
  SparklesIcon,
  PencilSquareIcon,
  PlusIcon,
  TrashIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ArrowPathIcon,
  FolderIcon,
  AcademicCapIcon,
  CheckCircleIcon
} from "@heroicons/vue/24/outline"
import { apiRequest } from "../../services/apiClient"

// Active Tab: 'ai' | 'manual'
const activeTab = ref("ai")

// AI Generation Form
const aiTopic = ref("")

// Manual Creation Form State: Starts with 1 empty card row by default
const manualTopic = ref("")
const manualCards = ref([
  { front: "", back: "" }
])

// Saved Decks & Viewing State
const savedDecks = ref([])
const activeDeck = ref(null)
const currentIndex = ref(0)
const isFlipped = ref(false)

const isLoading = ref(false)
const isSaving = ref(false)
const message = ref("")
const errorMessage = ref("")

async function fetchDecks() {
  try {
    const res = await apiRequest("/student/flashcards/decks")
    if (res.data && Array.isArray(res.data)) {
      savedDecks.value = res.data
      if (savedDecks.value.length > 0 && !activeDeck.value) {
        selectDeck(savedDecks.value[0])
      }
    }
  } catch (err) {
    console.warn("Could not fetch flashcard decks:", err.message)
  }
}

function selectDeck(deck) {
  activeDeck.value = deck
  currentIndex.value = 0
  isFlipped.value = false
}

// Generate Deck via AI
async function handleGenerateAI() {
  const topic = aiTopic.value.trim()
  if (!topic || isLoading.value) return

  isLoading.value = true
  message.value = ""
  errorMessage.value = ""

  try {
    const res = await apiRequest("/student/flashcards", {
      method: "POST",
      body: { topic, is_manual: false }
    })
    message.value = res.message || `AI Flashcards for "${topic}" generated and saved!`
    aiTopic.value = ""
    await fetchDecks()
    if (res.data) {
      selectDeck(res.data)
    }
  } catch (err) {
    errorMessage.value = err.message || "Failed to generate AI flashcards."
  } finally {
    isLoading.value = false
  }
}

// Multi-Card Manual Builder Methods
function addManualCardRow() {
  manualCards.value.push({ front: "", back: "" })
}

function removeManualCardRow(idx) {
  if (manualCards.value.length > 1) {
    manualCards.value.splice(idx, 1)
  } else {
    manualCards.value[0] = { front: "", back: "" }
  }
}

// Save Manual Deck to Database
async function handleSaveManualDeck() {
  const topic = manualTopic.value.trim()
  const validCards = manualCards.value.filter(
    (c) => c.front.trim() !== "" && c.back.trim() !== ""
  )

  if (!topic || validCards.length === 0 || isSaving.value) return

  isSaving.value = true
  message.value = ""
  errorMessage.value = ""

  try {
    const res = await apiRequest("/student/flashcards", {
      method: "POST",
      body: {
        topic,
        is_manual: true,
        cards: validCards
      }
    })
    message.value = res.message || `Custom deck "${topic}" with ${validCards.length} cards saved!`
    manualTopic.value = ""
    manualCards.value = [{ front: "", back: "" }]
    await fetchDecks()
    if (res.data) {
      selectDeck(res.data)
    }
  } catch (err) {
    errorMessage.value = err.message || "Failed to save custom flashcard deck."
  } finally {
    isSaving.value = false
  }
}

// Delete Entire Deck from DB
async function handleDeleteDeck(deckId, e) {
  if (e) e.stopPropagation()
  if (!confirm("Are you sure you want to delete this flashcard deck?")) return

  try {
    await apiRequest(`/student/flashcards/decks/${deckId}`, {
      method: "DELETE"
    })
    if (activeDeck.value && activeDeck.value.deck_id === deckId) {
      activeDeck.value = null
    }
    await fetchDecks()
  } catch (err) {
    errorMessage.value = err.message || "Failed to delete deck."
  }
}

// Delete Single Card from Active Deck
async function handleDeleteCurrentCard() {
  if (!activeDeck.value || !activeDeck.value.cards[currentIndex.value]) return
  const currentCard = activeDeck.value.cards[currentIndex.value]

  if (!confirm("Delete this card from deck?")) return

  try {
    if (currentCard.card_id) {
      await apiRequest(`/student/flashcards/items/${currentCard.card_id}`, {
        method: "DELETE"
      })
    }
    activeDeck.value.cards.splice(currentIndex.value, 1)
    if (currentIndex.value >= activeDeck.value.cards.length) {
      currentIndex.value = Math.max(0, activeDeck.value.cards.length - 1)
    }
    isFlipped.value = false
  } catch (err) {
    errorMessage.value = err.message || "Failed to delete card."
  }
}

function nextCard() {
  if (activeDeck.value && currentIndex.value < activeDeck.value.cards.length - 1) {
    isFlipped.value = false
    currentIndex.value++
  }
}

function prevCard() {
  if (currentIndex.value > 0) {
    isFlipped.value = false
    currentIndex.value--
  }
}

onMounted(() => {
  fetchDecks()
})
</script>

<template>
  <div>
    <PageHeader
      title="Flashcards"
      subtitle="Study with interactive AI-generated flashcards or build custom multi-card study decks."
    />

    <!-- Creation Tabs -->
    <div class="flex border-b border-slate-200 dark:border-border-dark mb-6 gap-6">
      <button
        @click="activeTab = 'ai'"
        class="pb-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition"
        :class="activeTab === 'ai' ? 'border-brand-green text-brand-green' : 'border-transparent text-ink-soft dark:text-slate-400 hover:text-ink'"
      >
        <SparklesIcon class="w-4 h-4" />
        Generate with AI
      </button>

      <button
        @click="activeTab = 'manual'"
        class="pb-3 text-sm font-semibold flex items-center gap-2 border-b-2 transition"
        :class="activeTab === 'manual' ? 'border-brand-green text-brand-green' : 'border-transparent text-ink-soft dark:text-slate-400 hover:text-ink'"
      >
        <PencilSquareIcon class="w-4 h-4" />
        Create Manually
      </button>
    </div>

    <!-- TAB 1: AI Generation Form -->
    <div v-if="activeTab === 'ai'" class="card p-5 mb-8 bg-gradient-to-r from-brand-green-500/10 to-brand-blue-500/10 border border-brand-green-500/20">
      <div class="flex items-center gap-2 mb-2">
        <SparklesIcon class="w-5 h-5 text-brand-green" />
        <h3 class="text-base font-display font-bold">Generate AI Flashcard Deck</h3>
      </div>
      <p class="text-xs text-ink-soft dark:text-slate-300 mb-3">
        Enter any subject or topic (e.g. Computer Architecture, Organic Chemistry, World History) to generate 10 subject-specific flashcards saved directly to your account.
      </p>

      <form @submit.prevent="handleGenerateAI" class="flex flex-col sm:flex-row gap-3">
        <input
          v-model="aiTopic"
          type="text"
          placeholder="e.g. Computer Science, Quadratic Equations, Cell Biology..."
          class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-border-dark bg-white dark:bg-card-dark text-sm focus:outline-none focus:ring-2 focus:ring-brand-green"
          :disabled="isLoading"
        />
        <button
          type="submit"
          :disabled="isLoading || !aiTopic.trim()"
          class="px-5 py-2.5 rounded-xl font-semibold text-sm bg-brand-green text-white hover:bg-brand-green-dark disabled:opacity-50 transition flex items-center justify-center gap-2"
        >
          <SparklesIcon v-if="!isLoading" class="w-4 h-4" />
          <span>{{ isLoading ? "Generating AI Deck..." : "Generate & Save Deck" }}</span>
        </button>
      </form>
    </div>

    <!-- TAB 2: Multi-Card Manual Creation Builder -->
    <div v-else-if="activeTab === 'manual'" class="card p-6 mb-8 border border-slate-200 dark:border-border-dark">
      <h3 class="text-base font-display font-bold mb-3 flex items-center gap-2">
        <PencilSquareIcon class="w-5 h-5 text-brand-blue" />
        Build Custom Multi-Card Deck
      </h3>

      <div class="mb-5">
        <label class="block text-xs font-bold text-ink-soft dark:text-slate-400 mb-1">Deck Subject / Title</label>
        <input
          v-model="manualTopic"
          type="text"
          placeholder="e.g. Math Formulas, Physics Units, French Vocabulary..."
          class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-border-dark bg-slate-50 dark:bg-slate-900/50 text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue"
        />
      </div>

      <!-- Multiple Card Input Rows -->
      <div class="space-y-4 mb-5">
        <div
          v-for="(card, idx) in manualCards"
          :key="idx"
          class="p-4 rounded-xl border border-slate-200 dark:border-border-dark bg-slate-50/70 dark:bg-slate-900/30 relative group"
        >
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold text-brand-blue uppercase tracking-wider">
              Card #{{ idx + 1 }}
            </span>
            <button
              @click="removeManualCardRow(idx)"
              class="text-slate-400 hover:text-danger text-xs font-semibold flex items-center gap-1 transition"
              title="Remove this card"
            >
              <TrashIcon class="w-4 h-4" /> Remove
            </button>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label class="block text-[11px] font-semibold text-ink-soft dark:text-slate-400 mb-1">Front (Question or Term)</label>
              <textarea
                v-model="card.front"
                rows="2"
                placeholder="e.g. What is 2 + 2?"
                class="w-full p-2.5 text-sm rounded-lg border border-slate-200 dark:border-border-dark bg-white dark:bg-card-dark focus:outline-none focus:ring-1 focus:ring-brand-blue"
              ></textarea>
            </div>

            <div>
              <label class="block text-[11px] font-semibold text-ink-soft dark:text-slate-400 mb-1">Back (Answer or Definition)</label>
              <textarea
                v-model="card.back"
                rows="2"
                placeholder="e.g. 4"
                class="w-full p-2.5 text-sm rounded-lg border border-slate-200 dark:border-border-dark bg-white dark:bg-card-dark focus:outline-none focus:ring-1 focus:ring-brand-blue"
              ></textarea>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-200 dark:border-border-dark pt-4">
        <button
          type="button"
          @click="addManualCardRow"
          class="w-full sm:w-auto px-4 py-2.5 rounded-xl font-semibold text-xs border border-brand-blue text-brand-blue hover:bg-brand-blue/10 transition flex items-center justify-center gap-1.5"
        >
          <PlusIcon class="w-4 h-4" /> Add Another Card (+ Card #{{ manualCards.length + 1 }})
        </button>

        <button
          @click="handleSaveManualDeck"
          :disabled="!manualTopic.trim() || manualCards.filter(c => c.front.trim() && c.back.trim()).length === 0 || isSaving"
          class="w-full sm:w-auto px-6 py-2.5 rounded-xl font-semibold text-sm bg-brand-green text-white hover:bg-brand-green-dark disabled:opacity-40 disabled:cursor-not-allowed transition flex items-center justify-center gap-2"
        >
          <CheckCircleIcon class="w-4 h-4" />
          <span>{{ isSaving ? "Saving..." : `Save Custom Deck (${manualCards.filter(c => c.front.trim() && c.back.trim()).length} Cards)` }}</span>
        </button>
      </div>
    </div>

    <!-- Status Feedback -->
    <p v-if="message" class="text-xs font-semibold text-brand-green mb-4">
      {{ message }}
    </p>
    <p v-if="errorMessage" class="text-xs font-semibold text-danger mb-4">
      {{ errorMessage }}
    </p>

    <!-- Main Section: Saved Decks & Active Flashcard Flipper -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Sidebar: Saved Decks -->
      <div class="lg:col-span-1 space-y-3">
        <h3 class="text-sm font-display font-bold flex items-center gap-2 text-ink-soft dark:text-slate-300">
          <FolderIcon class="w-4 h-4 text-brand-blue" />
          Saved Flashcard Decks ({{ savedDecks.length }})
        </h3>

        <div v-if="savedDecks.length === 0" class="card p-5 text-center text-xs text-ink-soft dark:text-slate-400">
          No saved flashcard decks yet. Use the form above to generate an AI deck or build your own custom cards!
        </div>

        <div v-else class="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
          <div
            v-for="deck in savedDecks"
            :key="deck.deck_id"
            @click="selectDeck(deck)"
            class="card p-4 cursor-pointer transition flex items-center justify-between border"
            :class="activeDeck && activeDeck.deck_id === deck.deck_id
              ? 'border-brand-green bg-brand-green/5 shadow-xs'
              : 'border-slate-200 dark:border-border-dark hover:bg-slate-50 dark:hover:bg-white/5'"
          >
            <div>
              <h4 class="font-display font-bold text-sm text-ink dark:text-white">
                {{ deck.topic }}
              </h4>
              <p class="text-xs text-ink-soft dark:text-slate-400 mt-0.5">
                {{ deck.card_count || deck.cards.length }} cards · {{ deck.created_at || 'Saved' }}
              </p>
            </div>

            <button
              @click="(e) => handleDeleteDeck(deck.deck_id, e)"
              title="Delete Deck"
              class="p-1.5 rounded-lg text-slate-400 hover:text-danger hover:bg-danger/10 transition"
            >
              <TrashIcon class="w-4.5 h-4.5" />
            </button>
          </div>
        </div>
      </div>

      <!-- Main Viewer: Active Deck Flashcard Flip -->
      <div class="lg:col-span-2">
        <div v-if="!activeDeck || activeDeck.cards.length === 0" class="card p-12 text-center text-ink-soft dark:text-slate-400">
          <AcademicCapIcon class="w-12 h-12 text-slate-300 mx-auto mb-2" />
          <p class="text-sm font-medium">Select a saved deck from the left list or create a new deck to start studying.</p>
        </div>

        <div v-else class="max-w-xl mx-auto">
          <!-- Card info & actions -->
          <div class="flex items-center justify-between mb-3 text-xs font-semibold text-ink-soft dark:text-slate-400">
            <span>Card {{ currentIndex + 1 }} of {{ activeDeck.cards.length }}</span>
            <div class="flex items-center gap-3">
              <span class="flex items-center gap-1 text-brand-blue cursor-pointer hover:underline" @click="isFlipped = !isFlipped">
                <ArrowPathIcon class="w-4 h-4" /> Tap card to flip
              </span>
              <button @click="handleDeleteCurrentCard" class="text-danger hover:text-rose-700 flex items-center gap-1 ml-2">
                <TrashIcon class="w-4 h-4" /> Delete Card
              </button>
            </div>
          </div>

          <!-- Flashcard View -->
          <div
            @click="isFlipped = !isFlipped"
            class="card p-8 md:p-12 min-h-[260px] flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 hover:shadow-lg relative overflow-hidden select-none border-2"
            :class="isFlipped
              ? 'border-brand-blue bg-brand-blue/5 dark:bg-brand-blue/10'
              : 'border-brand-green/30 bg-white dark:bg-card-dark'"
          >
            <span
              class="absolute top-4 left-4 px-2.5 py-1 rounded-full text-[11px] font-bold uppercase tracking-wider text-white"
              :class="isFlipped ? 'bg-brand-blue' : 'bg-brand-green'"
            >
              {{ isFlipped ? "Answer" : "Question" }}
            </span>

            <div class="my-auto px-4">
              <!-- Render text safely using {{ }} -->
              <h3 v-if="!isFlipped" class="text-xl md:text-2xl font-display font-semibold text-ink dark:text-white leading-relaxed">
                {{ activeDeck.cards[currentIndex].front }}
              </h3>
              <p v-else class="text-lg md:text-xl font-medium text-slate-700 dark:text-slate-200 leading-relaxed">
                {{ activeDeck.cards[currentIndex].back }}
              </p>
            </div>

            <p class="text-xs text-ink-soft dark:text-slate-400 mt-4">
              Tap anywhere on card to flip
            </p>
          </div>

          <!-- Navigation Controls -->
          <div class="flex items-center justify-between mt-5">
            <button
              @click="prevCard"
              :disabled="currentIndex === 0"
              class="px-4 py-2.5 rounded-xl font-semibold text-sm border border-slate-200 dark:border-border-dark disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 dark:hover:bg-white/5 transition flex items-center gap-1"
            >
              <ChevronLeftIcon class="w-4 h-4" /> Previous
            </button>

            <span class="text-xs font-semibold text-ink-soft dark:text-slate-400">
              {{ activeDeck.topic }}
            </span>

            <button
              @click="nextCard"
              :disabled="currentIndex === activeDeck.cards.length - 1"
              class="px-4 py-2.5 rounded-xl font-semibold text-sm bg-brand-green text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-brand-green-dark transition flex items-center gap-1"
            >
              Next <ChevronRightIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
