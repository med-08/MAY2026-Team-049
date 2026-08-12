<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ChatBubbleLeftRightIcon, PaperAirplaneIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'
import { parentApi } from '../../services/parentApi'
import { useParentPortal } from '../../composables/useParentPortal'

const { parentId } = useParentPortal()

const messages = ref([])
const newMessage = ref('')
const subject = ref('')
const loading = ref(true)
const sending = ref(false)
const error = ref('')
const chatContainer = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

const fetchMessages = async () => {
  if (!parentId.value) return
  loading.value = true
  error.value = ''
  try {
    const res = await parentApi.getMessages(parentId.value)
    messages.value = res.data || []
    scrollToBottom()
  } catch (e) {
    error.value = e.message || 'Failed to load messages.'
  } finally {
    loading.value = false
  }
}

const handleSendMessage = async () => {
  if (!newMessage.value.trim() || sending.value) return

  sending.value = true
  error.value = ''

  const payload = {
    parent_id: parentId.value,
    tutor_id: 1, // Default tutor ID
    subject: subject.value.trim() || 'Parent Query',
    message: newMessage.value.trim()
  }

  try {
    const res = await parentApi.sendMessage(payload)
    if (res && (res.success || res.status === 'success')) {
      newMessage.value = ''
      subject.value = ''
      await fetchMessages()
    } else {
      error.value = res.message || 'Failed to send message.'
    }
  } catch (e) {
    error.value = e.message || 'Network error while sending message.'
  } finally {
    sending.value = false
  }
}

onMounted(() => {
  fetchMessages()
})
</script>

<template>
  <div class="space-y-6">
    <div class="card p-5">
      <!-- Header -->
      <div class="flex items-center justify-between mb-4 border-b border-slate-200 dark:border-slate-700 pb-3">
        <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 flex items-center gap-2 text-lg">
          <ChatBubbleLeftRightIcon class="w-6 h-6 text-brand-green-500" />
          Messages with Tutor
        </h3>
        <button 
          @click="fetchMessages" 
          class="p-2 text-slate-500 hover:text-brand-green-500 dark:text-slate-400 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          title="Refresh Messages"
        >
          <ArrowPathIcon class="w-5 h-5" :class="{ 'animate-spin': loading }" />
        </button>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-sm">
        {{ error }}
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-12">
        <ArrowPathIcon class="w-8 h-8 text-brand-green-500 animate-spin" />
        <span class="ml-2 text-slate-500 dark:text-slate-400">Loading messages...</span>
      </div>

      <!-- Conversation List -->
      <div v-else class="space-y-4">
        <div 
          ref="chatContainer"
          class="h-96 overflow-y-auto p-4 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-4"
        >
          <div v-if="!messages.length" class="text-center py-12 text-slate-400 dark:text-slate-500">
            No messages yet. Send a message to the tutor below.
          </div>

          <div 
            v-for="m in messages" 
            :key="m.message_id" 
            class="flex flex-col"
            :class="m.sender_type === 'Parent' ? 'items-end' : 'items-start'"
          >
            <div 
              class="max-w-[80%] rounded-2xl px-4 py-3 shadow-sm"
              :class="m.sender_type === 'Parent' 
                ? 'bg-brand-green-600 text-white rounded-br-none' 
                : 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 border border-slate-200 dark:border-slate-700 rounded-bl-none'"
            >
              <div class="flex items-center justify-between gap-4 mb-1 text-xs opacity-75">
                <span class="font-semibold">{{ m.sender_type === 'Parent' ? 'You' : 'Tutor' }}</span>
                <span>{{ m.sent_at }}</span>
              </div>
              <p v-if="m.subject" class="text-xs font-semibold underline mb-1">{{ m.subject }}</p>
              <p class="text-sm leading-relaxed whitespace-pre-wrap">{{ m.message }}</p>

              <!-- Reply Message -->
              <div v-if="m.reply_message" class="mt-2 pt-2 border-t border-slate-200/20 text-xs italic">
                <span class="font-semibold block mb-0.5">Tutor Reply:</span>
                <p>{{ m.reply_message }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Send Form -->
        <form @submit.prevent="handleSendMessage" class="space-y-3 pt-2">
          <div>
            <input 
              v-model="subject" 
              type="text" 
              placeholder="Subject (e.g. Science Progress, Class Schedule)"
              class="w-full px-4 py-2 text-sm rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-brand-green-500"
            />
          </div>
          <div class="flex gap-2">
            <textarea 
              v-model="newMessage" 
              rows="2"
              placeholder="Type your message to the tutor..." 
              class="flex-1 px-4 py-2 text-sm rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-brand-green-500 resize-none"
              required
            ></textarea>
            <button 
              type="submit" 
              :disabled="sending || !newMessage.trim()"
              class="px-5 py-2 bg-brand-green-500 hover:bg-brand-green-600 disabled:opacity-50 text-white font-medium rounded-lg flex items-center justify-center gap-2 transition-colors self-end h-10"
            >
              <PaperAirplaneIcon v-if="!sending" class="w-4 h-4" />
              <ArrowPathIcon v-else class="w-4 h-4 animate-spin" />
              <span>{{ sending ? 'Sending...' : 'Send' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>