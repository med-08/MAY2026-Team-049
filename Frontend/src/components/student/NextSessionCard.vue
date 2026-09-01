<script setup>
import { ref } from 'vue'
import { studentApi } from '../../services/studentApi'
import { useToast } from '../../composables/useToast'

const props = defineProps({ session: { type: Object, default: () => ({}) } })
const { showToast } = useToast()
const busy = ref(false)
const hasSession = () => !!(props.session && props.session.session_id)

function meetingLabel() {
  return props.session?.meeting_lifecycle || props.session?.meeting_status || 'Meeting Not Started'
}

async function join() {
  if (busy.value || !props.session?.can_join) return
  busy.value = true
  try {
    const r = await studentApi.joinSession(props.session.session_id)
    const url = r.data?.meeting_url || props.session.meeting_url || props.session.meetingUrl
    if (url) window.open(url, '_blank', 'noopener,noreferrer')
  } catch (e) {
    showToast(e?.message || 'Unable to join meeting.', 'error')
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div v-if="!hasSession()" class="card flex flex-col items-center justify-center text-center py-10 px-6">
    <h3 class="font-display font-bold mb-1">No Upcoming Session</h3>
    <p class="text-sm text-ink-soft dark:text-slate-400">You don't have any session booked yet. Head to Session Booking to schedule one.</p>
  </div>

  <div v-else class="rounded-2xl overflow-hidden bg-gradient-to-br from-brand-blue to-indigo-600 shadow-lg shadow-brand-blue/20">
    <div class="p-6 text-white">
      <div class="flex items-start justify-between gap-3">
        <div>
          <p class="text-white/80 text-xs font-semibold tracking-wide uppercase">Next Session</p>
          <h3 class="text-white font-display font-bold text-lg">{{ session.subject }}</h3>
        </div>
        <span class="bg-white/20 text-white text-xs font-semibold px-3 py-1 rounded-full">{{ meetingLabel() }}</span>
      </div>

      <div class="mt-5 grid grid-cols-2 gap-4">
        <div><p class="text-white/70 text-xs">Tutor</p><p class="text-sm font-semibold">{{ session.tutor }}</p></div>
        <div><p class="text-white/70 text-xs">Session Type</p><p class="text-sm font-semibold">{{ session.type }}</p></div>
        <div><p class="text-white/70 text-xs">Date</p><p class="text-sm font-semibold">{{ session.date }}</p></div>
        <div><p class="text-white/70 text-xs">Time</p><p class="text-sm font-semibold">{{ session.start_time_display || session.time }} – {{ session.end_time_display || session.end_time }} · {{ session.duration }}</p></div>
      </div>
    </div>

    <div class="px-6 pb-6">
      <button
        v-if="session.can_join"
        type="button"
        class="w-full rounded-xl bg-white px-4 py-3 text-sm font-bold text-brand-blue hover:bg-slate-50 disabled:opacity-60"
        :disabled="busy"
        @click="join"
      >Join Google Meet</button>
      <a
        v-else-if="session.meeting_url || session.meetingUrl"
        :href="session.meeting_url || session.meetingUrl"
        target="_blank"
        rel="noopener noreferrer"
        class="block w-full rounded-xl bg-white px-4 py-3 text-center text-sm font-bold text-brand-blue hover:bg-slate-50"
      >Meeting Link</a>
      <div v-else class="rounded-xl bg-white/15 px-4 py-3 text-center text-sm font-semibold text-white">
        {{ meetingLabel() }}
      </div>
    </div>
  </div>
</template>
