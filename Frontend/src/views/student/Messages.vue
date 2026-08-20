<script setup>
import { computed, onMounted, ref } from 'vue'
import { studentApi } from '../../services/studentApi'

const conversations = ref([])
const tutors = ref([])
const selectedTutorId = ref('')
const draft = ref('')
const loading = ref(true)
const sending = ref(false)
const error = ref('')

const activeConversation = computed(() =>
  conversations.value.find(c => String(c.tutor_id) === String(selectedTutorId.value)) || null
)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [messagesRes, sessionsRes] = await Promise.all([
      studentApi.getMessages(),
      studentApi.getMeetings().catch(() => ({ data: [] }))
    ])
    // studentApi returns the parsed backend envelope directly:
    // { success: true, data: { conversations, tutors } }.
    // Never iterate over the envelope itself.
    const messageData = messagesRes?.data && typeof messagesRes.data === 'object' ? messagesRes.data : {}
    const meetingData = sessionsRes?.data && typeof sessionsRes.data === 'object' ? sessionsRes.data : {}
    conversations.value = Array.isArray(messageData.conversations) ? messageData.conversations : []
    const map = new Map()
    const linkedTutors = Array.isArray(messageData.tutors) ? messageData.tutors : []
    linkedTutors.forEach(t => {
      if (t?.tutor_id && t?.tutor_name) {
        map.set(String(t.tutor_id), { tutor_id: t.tutor_id, tutor_name: t.tutor_name })
      }
    })
    const meetings = Array.isArray(meetingData.meetings) ? meetingData.meetings : []
    meetings.forEach(s => {
      if (s?.tutor_id && s?.tutor) {
        map.set(String(s.tutor_id), { tutor_id: s.tutor_id, tutor_name: s.tutor })
      }
    })
    conversations.value.forEach(c => {
      if (c?.tutor_id && c?.tutor_name) {
        map.set(String(c.tutor_id), { tutor_id: c.tutor_id, tutor_name: c.tutor_name })
      }
    })
    tutors.value = [...map.values()]
    if (!selectedTutorId.value && tutors.value.length) selectedTutorId.value = String(tutors.value[0].tutor_id)
  } catch (e) {
    error.value = e.message || 'Unable to load messages.'
  } finally {
    loading.value = false
  }
}

async function send() {
  const text = draft.value.trim()
  if (!text || !selectedTutorId.value || sending.value) return
  sending.value = true
  try {
    await studentApi.sendMessage({ tutor_id: Number(selectedTutorId.value), message: text })
    draft.value = ''
    await load()
  } catch (e) {
    error.value = e.message || 'Message could not be sent.'
  } finally {
    sending.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="space-y-6">
    <div class="card p-5">
      <div class="flex items-center justify-between gap-4 mb-5">
        <div>
          <h2 class="font-display text-xl font-bold">Messages</h2>
          <p class="text-sm text-slate-500 mt-1">Chat directly with any tutor linked to your sessions.</p>
        </div>
        <button class="btn-secondary" @click="load">Refresh</button>
      </div>

      <p v-if="error" class="text-sm text-rose-600 mb-4">{{ error }}</p>

      <div class="grid lg:grid-cols-[260px_1fr] gap-4 min-h-[430px]">
        <div class="rounded-2xl bg-slate-50 dark:bg-slate-800/60 p-3">
          <p class="text-xs font-bold uppercase tracking-wide text-slate-400 px-2 mb-2">Your tutors</p>
          <button
            v-for="t in tutors"
            :key="t.tutor_id"
            class="w-full text-left rounded-xl px-3 py-3 mb-1 transition"
            :class="String(selectedTutorId) === String(t.tutor_id) ? 'bg-white dark:bg-slate-700 shadow-sm text-brand-blue-600' : 'hover:bg-white/80 dark:hover:bg-slate-700/60'"
            @click="selectedTutorId = String(t.tutor_id)"
          >
            <span class="font-semibold text-sm">{{ t.tutor_name }}</span>
            <span class="block text-xs text-slate-400 mt-0.5">Tutor</span>
          </button>
          <p v-if="!tutors.length && !loading" class="text-xs text-slate-400 p-2">No linked tutors found yet.</p>
        </div>

        <div class="rounded-2xl border border-slate-100 dark:border-slate-700 flex flex-col overflow-hidden">
          <div class="px-4 py-3 border-b border-slate-100 dark:border-slate-700">
            <p class="font-semibold">{{ activeConversation?.tutor_name || 'Select a tutor' }}</p>
            <p class="text-xs text-slate-400">Tutor messages and your replies stay in this conversation.</p>
          </div>

          <div class="flex-1 p-4 space-y-3 overflow-y-auto min-h-[300px]">
            <div v-if="loading" class="text-sm text-slate-400">Loading messages...</div>
            <div v-else-if="!activeConversation?.messages?.length" class="text-sm text-slate-400 text-center py-16">No messages yet. Start the conversation.</div>
            <div
              v-for="m in activeConversation?.messages || []"
              :key="m.message_id"
              class="max-w-[80%] rounded-2xl px-4 py-3 text-sm"
              :class="m.sender_type === 'Student' ? 'ml-auto bg-brand-blue-600 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200'"
            >
              <p class="whitespace-pre-wrap">{{ m.message }}</p>
              <p class="text-[10px] mt-1 opacity-70">{{ m.sent_at ? new Date(m.sent_at).toLocaleString() : '' }}</p>
            </div>
          </div>

          <div class="p-3 border-t border-slate-100 dark:border-slate-700 flex gap-2">
            <input v-model="draft" class="input-field flex-1" placeholder="Write a message..." @keydown.enter="send">
            <button class="btn-primary" :disabled="sending || !selectedTutorId || !draft.trim()" @click="send">{{ sending ? 'Sending...' : 'Send' }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
