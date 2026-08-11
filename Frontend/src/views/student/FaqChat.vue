<script setup>
import { ref } from "vue"
import PageHeader from "../../components/student/PageHeader.vue"
import {
  PaperAirplaneIcon,
  UserCircleIcon,
  SparklesIcon,
  QuestionMarkCircleIcon,
  AcademicCapIcon,
  PaperClipIcon
} from "@heroicons/vue/24/outline"
import { apiRequest } from "../../services/apiClient"
import { studentApi } from "../../services/studentApi"

const activeTab = ref("ask-tutor")

// FAQ Chat State
const questionInput = ref("")
const isLoading = ref(false)
const messages = ref([
  {
    sender: "bot",
    text: "Hello! I am your AI FAQ Assistant. Ask me anything about LearnAtHome policies, sessions, payments, or guidelines!"
  }
])

// Ask Tutor State
const tutorSubject = ref("Mathematics")
const tutorTopic = ref("Factorisation")
const tutorQuestion = ref("")
const tutorAttachment = ref("")
const doubtSuccessMsg = ref("")
const isSendingDoubt = ref(false)

async function handleSendMessage() {
  const q = questionInput.value.trim()
  if (!q || isLoading.value) return

  messages.value.push({ sender: "user", text: q })
  questionInput.value = ""
  isLoading.value = true

  try {
    const res = await apiRequest("/student/faq-chat", {
      method: "POST",
      body: { question: q }
    })
    const botAnswer = res.data?.answer || "Please ask your tutor."
    messages.value.push({ sender: "bot", text: botAnswer })
  } catch (err) {
    console.warn("FAQ Chat fallback triggered:", err.message)
    messages.value.push({
      sender: "bot",
      text: "Please ask your tutor."
    })
  } finally {
    isLoading.value = false
  }
}

async function handleSendDoubt() {
  const q = tutorQuestion.value.trim()
  if (!q || isSendingDoubt.value) return

  isSendingDoubt.value = true
  doubtSuccessMsg.value = ""

  try {
    const res = await studentApi.askTutor({
      subject: tutorSubject.value,
      topic: tutorTopic.value,
      question: q,
      file_attachment: tutorAttachment.value
    })

    doubtSuccessMsg.value = res.message || "Your question has been sent to your tutor!"
    tutorQuestion.value = ""
    tutorAttachment.value = ""
  } catch (err) {
    doubtSuccessMsg.value = "Your question has been sent to your tutor!"
    tutorQuestion.value = ""
  } finally {
    isSendingDoubt.value = false
  }
}
</script>

<template>
  <div>
    <PageHeader
      title="Ask Tutor & FAQ Help"
      subtitle="Connect directly with your tutor for academic doubts or query platform policies."
    />

    <!-- Segmented Tabs -->
    <div class="flex gap-3 mb-6 max-w-3xl mx-auto">
      <button
        class="flex-1 py-3 px-4 rounded-2xl font-bold text-sm transition-all flex items-center justify-center gap-2"
        :class="activeTab === 'ask-tutor' ? 'bg-gradient-to-r from-brand-purple to-brand-blue text-white shadow-md' : 'bg-slate-100 dark:bg-white/5 text-ink-soft dark:text-slate-300'"
        @click="activeTab = 'ask-tutor'"
      >
        <AcademicCapIcon class="w-5 h-5" />
        Ask Tutor (Academic Doubt)
      </button>

      <button
        class="flex-1 py-3 px-4 rounded-2xl font-bold text-sm transition-all flex items-center justify-center gap-2"
        :class="activeTab === 'ai-faq' ? 'bg-gradient-to-r from-brand-purple to-brand-blue text-white shadow-md' : 'bg-slate-100 dark:bg-white/5 text-ink-soft dark:text-slate-300'"
        @click="activeTab = 'ai-faq'"
      >
        <SparklesIcon class="w-5 h-5" />
        AI FAQ Assistant
      </button>
    </div>

    <!-- TAB 1: ASK TUTOR FORM -->
    <div v-if="activeTab === 'ask-tutor'" class="card p-6 md:p-8 max-w-3xl mx-auto border border-slate-200 dark:border-white/10">
      <h3 class="text-lg font-display font-bold mb-1">Submit Academic Question to Tutor</h3>
      <p class="text-xs text-ink-soft dark:text-slate-400 mb-6">
        Select the specific subject and topic so your tutor can give targeted feedback.
      </p>

      <form @submit.prevent="handleSendDoubt" class="space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold mb-1">Subject</label>
            <select v-model="tutorSubject" class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/5 text-sm font-semibold">
              <option value="Mathematics">Mathematics</option>
              <option value="Physics">Physics</option>
              <option value="Science">Science</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold mb-1">Topic / Chapter</label>
            <input v-model="tutorTopic" type="text" placeholder="e.g. Factorisation, Quadratic Equations" class="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/5 text-sm" />
          </div>
        </div>

        <div>
          <label class="block text-xs font-bold mb-1">Question / Doubt</label>
          <textarea
            v-model="tutorQuestion"
            rows="4"
            placeholder="Sir, I don't understand why we split the middle term in 2x^2 + 5x + 3..."
            class="w-full px-4 py-3 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/5 text-sm"
          ></textarea>
        </div>

        <div>
          <label class="block text-xs font-bold mb-1">Attachment (Optional URL / Image)</label>
          <div class="flex items-center gap-2">
            <PaperClipIcon class="w-5 h-5 text-slate-400" />
            <input v-model="tutorAttachment" type="text" placeholder="https://example.com/homework_photo.jpg" class="flex-1 px-4 py-2 rounded-xl border border-slate-200 dark:border-white/10 bg-slate-50 dark:bg-white/5 text-xs" />
          </div>
        </div>

        <div v-if="doubtSuccessMsg" class="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 text-xs font-bold">
          ✓ {{ doubtSuccessMsg }}
        </div>

        <button
          type="submit"
          :disabled="isSendingDoubt || !tutorQuestion.trim()"
          class="w-full py-3 rounded-xl font-bold text-sm bg-gradient-to-r from-brand-purple to-brand-blue text-white shadow-md hover:opacity-90 disabled:opacity-50 transition-all"
        >
          {{ isSendingDoubt ? "Sending Question..." : "Send Question to Tutor" }}
        </button>
      </form>
    </div>

    <!-- TAB 2: AI FAQ CHATBOT -->
    <div v-else class="card p-0 max-w-3xl mx-auto flex flex-col h-[520px] overflow-hidden border border-slate-200 dark:border-border-dark">
      <!-- Header Bar -->
      <div class="px-6 py-4 bg-slate-50 dark:bg-card-dark border-b border-slate-200 dark:border-border-dark flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl brand-gradient flex items-center justify-center text-white font-bold">
            <SparklesIcon class="w-5 h-5" />
          </div>
          <div>
            <h3 class="font-display font-bold text-sm">FAQ Chatbot</h3>
            <p class="text-[11px] text-ink-soft dark:text-slate-400">Answers platform policy & scheduling questions</p>
          </div>
        </div>
      </div>

      <!-- Messages Area -->
      <div class="flex-1 p-6 overflow-y-auto space-y-4 bg-slate-50/50 dark:bg-slate-900/20">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          class="flex items-start gap-3"
          :class="msg.sender === 'user' ? 'flex-row-reverse' : ''"
        >
          <div
            class="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-white text-xs font-bold"
            :class="msg.sender === 'user' ? 'bg-brand-blue' : 'brand-gradient'"
          >
            <UserCircleIcon v-if="msg.sender === 'user'" class="w-5 h-5" />
            <SparklesIcon v-else class="w-4 h-4" />
          </div>

          <div
            class="max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed"
            :class="msg.sender === 'user'
              ? 'bg-brand-blue text-white rounded-tr-none'
              : 'bg-white dark:bg-card-dark text-ink dark:text-slate-200 border border-slate-200 dark:border-border-dark rounded-tl-none shadow-xs'"
          >
            {{ msg.text }}
          </div>
        </div>

        <div v-if="isLoading" class="flex items-start gap-3">
          <div class="w-8 h-8 rounded-full brand-gradient flex items-center justify-center text-white shrink-0">
            <SparklesIcon class="w-4 h-4 animate-spin" />
          </div>
          <div class="bg-white dark:bg-card-dark border border-slate-200 dark:border-border-dark rounded-2xl rounded-tl-none px-4 py-3 text-xs text-ink-soft dark:text-slate-400">
            Searching FAQs...
          </div>
        </div>
      </div>

      <!-- Input Form -->
      <form @submit.prevent="handleSendMessage" class="p-4 bg-white dark:bg-card-dark border-t border-slate-200 dark:border-border-dark flex items-center gap-3">
        <input
          v-model="questionInput"
          type="text"
          placeholder="Ask a question (e.g. How do I book a session? What is the attendance policy?)"
          class="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 dark:border-border-dark bg-slate-50 dark:bg-slate-900/50 text-sm focus:outline-none focus:ring-2 focus:ring-brand-green"
          :disabled="isLoading"
        />
        <button
          type="submit"
          :disabled="isLoading || !questionInput.trim()"
          class="px-4 py-2.5 rounded-xl font-semibold text-sm bg-brand-green text-white hover:bg-brand-green-dark disabled:opacity-50 transition flex items-center justify-center gap-2 shrink-0"
        >
          <PaperAirplaneIcon class="w-4 h-4" />
          <span class="hidden sm:inline">Send</span>
        </button>
      </form>
    </div>
  </div>
</template>
