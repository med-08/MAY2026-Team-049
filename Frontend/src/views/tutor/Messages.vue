<template>
  <section class="view on">
    <div class="card glass reveal">
      <div class="ch"><h3>Messages</h3><button class="btn sm magnetic" type="button" @click="meetingOpen = !meetingOpen"><svg viewBox="0 0 24 24"><path d="M15 10l5-3v10l-5-3M4 6h11v12H4Z"/></svg> Request meeting</button></div>
      <div v-show="meetingOpen" style="border:1px solid var(--ring);border-radius:14px;padding:16px;margin-bottom:16px;background:var(--panel)">
        <div class="eyebrow" style="margin-bottom:10px">Virtual meeting request · confirmed within 48h</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px">
          <div><label class="lab" for="meet-with">With</label><input id="meet-with" class="field" placeholder="Parent · Aarav"></div>
          <div><label class="lab" for="meet-date">Date</label><input id="meet-date" class="field" placeholder="Sat, 12 Jul"></div>
          <div><label class="lab" for="meet-time">Time</label><input id="meet-time" class="field" placeholder="11:00 AM"></div>
        </div>
        <button class="btn grad sm magnetic" type="button" style="margin-top:12px" @click="$emit('toast', 'Meeting request sent · confirm within 48h')">Send request</button>
      </div>
      <div class="chat">
        <div class="clist">
          <TutorEmptyState v-if="!conversationList.length" title="No messages" />
          <button v-for="conversation in pagedConversations" :key="conversation.id" class="ci" :class="{ on: activeConversationId === conversation.id }" type="button" @click="$emit('select-conversation', conversation.id)">
            <div class="av" :style="{ background: conversation.gradient }">{{ conversation.initials }}</div><div><div class="t" style="font-size:12.5px">{{ conversation.participantName }}</div><div class="s" style="font-size:11px">{{ conversation.subtitle }}</div></div>
          </button>
          <TutorPagination v-if="conversationList.length" v-model:page="page" :total-pages="totalPages" />
        </div>
        <div class="thr">
          <div ref="msgsRef" class="msgs">
            <div v-for="message in activeConversation.messages" :key="message.messageId" class="bub" :class="message.w">{{ message.message }}</div>
          </div>
          <div class="cin"><input v-model="draft" class="field" placeholder="Type a reply…" @keydown.enter="send"><button class="btn grad magnetic" type="button" @click="send">Send</button></div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, nextTick, ref, watch } from 'vue'
import TutorEmptyState from '../../components/tutor/TutorEmptyState.vue'
import TutorPagination from '../../components/tutor/TutorPagination.vue'
const props = defineProps({
  conversations: { type: Object, required: true },
  activeConversationId: { type: String, required: true }
})
const emit = defineEmits(['select-conversation', 'send-message', 'toast'])
const draft = ref('')
const meetingOpen = ref(false)
const msgsRef = ref(null)
const page = ref(1)
const pageSize = 3
const conversationList = computed(() => Object.values(props.conversations))
const totalPages = computed(() => Math.max(1, Math.ceil(conversationList.value.length / pageSize)))
const pagedConversations = computed(() => conversationList.value.slice((page.value - 1) * pageSize, page.value * pageSize))
const activeConversation = computed(() => props.conversations[props.activeConversationId])
function send() {
  const message = draft.value.trim()
  if (!message) return
  emit('send-message', props.activeConversationId, message)
  draft.value = ''
}
function scrollToBottom() {
  nextTick(() => {
    if (msgsRef.value) msgsRef.value.scrollTop = msgsRef.value.scrollHeight
  })
}
watch(() => activeConversation.value.messages.length, scrollToBottom)
watch(() => props.activeConversationId, scrollToBottom, { immediate: true })
</script>
