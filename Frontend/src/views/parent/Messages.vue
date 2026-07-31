<script setup>
import { reactive } from 'vue'
import { ChatBubbleLeftRightIcon, PaperAirplaneIcon } from '@heroicons/vue/24/outline'
import EmptyState from '../../components/ui/EmptyState.vue'
import { useToast } from '../../composables/useToast'
import { useParentPortal } from '../../composables/useParentPortal'

const { showToast } = useToast()
const { parentMessages, sendMessageToTutor, replyExistingMessage } = useParentPortal(1)

function formatDateTime(dateStr) {
  if (!dateStr) return '\u2014'
  return new Date(dateStr).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
}

const replyDrafts = reactive({})
function sendReply(messageId) {
  const text = (replyDrafts[messageId] || '').trim()
  if (!text) return showToast('Write a message before sending.', 'error')
  replyExistingMessage(messageId, text)
  replyDrafts[messageId] = ''
  showToast('Message sent to tutor.')
}

const newMessage = reactive({ subject: '', message: '' })
function sendNewMessage() {
  if (!newMessage.subject.trim() || !newMessage.message.trim()) {
    return showToast('Add a subject and message before sending.', 'error')
  }
  sendMessageToTutor(newMessage.subject, newMessage.message)
  newMessage.subject = ''
  newMessage.message = ''
  showToast("Message sent to tutor. You'll get a reply within 24 hours.")
}
</script>

<template>
  <div class="space-y-6">
    <div class="card p-5">
      <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4 flex items-center gap-2">
        <ChatBubbleLeftRightIcon class="w-5 h-5 text-brand-green-500" />
        Messages with Tutor
      </h3>

      <div v-if="parentMessages.length" class="space-y-4 mb-6">
        <div v-for="m in parentMessages" :key="m.message_id" class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
          <div class="flex items-center justify-between">
            <p class="text-sm font-semibold text-slate-800 dark:text-slate-100">{{ m.subject }}</p>
            <span class="text-[11px] text-slate-400">{{ formatDateTime(m.sent_at) }}</span>
          </div>
          <p class="text-sm text-slate-600 dark:text-slate-300 mt-1.5">{{ m.message }}</p>

          <div v-if="m.reply_message" class="mt-3 pl-3 border-l-2 border-brand-green-500">
            <p class="text-xs font-semibold text-brand-green-700 dark:text-brand-green-400">Tutor replied</p>
            <p class="text-sm text-slate-600 dark:text-slate-300 mt-1">{{ m.reply_message }}</p>
          </div>
          <div v-else class="mt-3 flex flex-col sm:flex-row gap-2">
            <input
              v-model="replyDrafts[m.message_id]"
              type="text"
              placeholder="Follow up on this message..."
              class="input-field flex-1"
              @keyup.enter="sendReply(m.message_id)"
            />
            <button class="btn-secondary shrink-0" @click="sendReply(m.message_id)">
              <PaperAirplaneIcon class="w-4 h-4" />
              Send
            </button>
          </div>
        </div>
      </div>
      <EmptyState v-else title="No messages yet" message="Start a conversation with the tutor below." />

      <div class="border-t border-slate-100 dark:border-slate-800 pt-4">
        <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">New Message</p>
        <div class="space-y-2">
          <input v-model="newMessage.subject" type="text" placeholder="Subject" class="input-field" />
          <textarea v-model="newMessage.message" rows="3" placeholder="Write your message to the tutor..." class="input-field resize-none"></textarea>
          <button class="btn-primary" @click="sendNewMessage">
            <PaperAirplaneIcon class="w-4 h-4" />
            Send Message
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
