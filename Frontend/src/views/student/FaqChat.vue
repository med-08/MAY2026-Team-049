<script setup>
import { ref } from "vue"
import PageHeader from "../../components/student/PageHeader.vue"
import {
  PaperAirplaneIcon,
  ChatBubbleLeftRightIcon,
  UserCircleIcon,
  SparklesIcon,
  QuestionMarkCircleIcon
} from "@heroicons/vue/24/outline"
import { apiRequest } from "../../services/apiClient"

const questionInput = ref("")
const isLoading = ref(false)

const messages = ref([
  {
    sender: "bot",
    text: "Hello! I am your AI FAQ Assistant. Ask me anything about LearnAtHome policies, sessions, payments, or guidelines!"
  }
])

async function handleSendMessage() {
  const q = questionInput.value.trim()
  if (!q || isLoading.value) return

  // Add user message
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
</script>

<template>
  <div>
    <PageHeader
      title="AI FAQ Assistant"
      subtitle="Ask questions about platform policies, schedules, and guidelines answered directly from official FAQs."
    />

    <div class="card p-0 max-w-3xl mx-auto flex flex-col h-[550px] overflow-hidden border border-slate-200 dark:border-border-dark">
      <!-- Header Bar -->
      <div class="px-6 py-4 bg-slate-50 dark:bg-card-dark border-b border-slate-200 dark:border-border-dark flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl brand-gradient flex items-center justify-center text-white font-bold">
            <SparklesIcon class="w-5 h-5" />
          </div>
          <div>
            <h3 class="font-display font-bold text-sm">FAQ Chatbot</h3>
            <p class="text-[11px] text-ink-soft dark:text-slate-400">Strictly answers from official FAQ database</p>
          </div>
        </div>

        <RouterLink
          to="/student/faq"
          class="text-xs font-semibold text-brand-blue hover:underline flex items-center gap-1"
        >
          <QuestionMarkCircleIcon class="w-4 h-4" /> View FAQ Board
        </RouterLink>
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
            <!-- Safe text rendering using {{ }} interpolation -->
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
