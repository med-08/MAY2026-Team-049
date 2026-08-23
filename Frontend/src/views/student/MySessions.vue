<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import StatusBadge from '../../components/student/StatusBadge.vue'
import { studentApi } from '../../services/studentApi'
import { useToast } from '../../composables/useToast'

const { showToast } = useToast()
const busy = ref(null)
const data = ref({ upcoming: [], completed: [] })
const loading = ref(true)
const error = ref('')
let refreshTimer = null

const tutors = ref([])
const requestForm = ref({ tutor_id: '', date: '', startTime: '', endTime: '', notes: '' })
const requesting = ref(false)

async function loadTutors() {
  try {
    const r = await studentApi.getDoubtTutors()
    tutors.value = r.data?.tutors || []
  } catch {
    tutors.value = []
  }
}

async function submitMeetingRequest() {
  const f = requestForm.value
  if (!f.tutor_id || !f.date || !f.startTime) {
    showToast('Choose a tutor, date, and start time.', 'error')
    return
  }
  requesting.value = true
  try {
    await studentApi.requestMeeting({
      tutor_id: Number(f.tutor_id),
      preferred_date: f.date,
      preferred_time: f.startTime,
      preferred_end_time: f.endTime || undefined,
      notes: f.notes
    })
    showToast('Meeting requested. Your tutor has been notified.', 'success')
    requestForm.value = { tutor_id: '', date: '', startTime: '', endTime: '', notes: '' }
    await loadSessions(false)
  } catch (e) {
    showToast(e?.message || 'Unable to request meeting.', 'error')
  } finally {
    requesting.value = false
  }
}

async function loadSessions(showLoading = true) {
  if (showLoading) loading.value = true
  error.value = ''
  try {
    const r = await studentApi.getSessions()
    data.value = r.data || { upcoming: [], completed: [] }
  } catch (e) {
    error.value = e?.message || 'Unable to load sessions.'
  } finally {
    loading.value = false
  }
}

async function joinSession(s) {
  if (busy.value || !s?.can_join) return
  busy.value = s.id
  try {
    const r = await studentApi.joinSession(s.id)
    const url = r.data?.meeting_url || s.meeting_url || s.meetingUrl
    if (url) window.open(url, '_blank', 'noopener,noreferrer')
    showToast('Meeting opened. Your join time is being recorded.', 'success')
    await loadSessions(false)
  } catch (e) {
    showToast(e?.message || 'Unable to join meeting.', 'error')
  } finally {
    busy.value = null
  }
}

async function completeSession(s) {
  if (busy.value || !s?.can_complete) return
  busy.value = s.id
  try {
    const r = await studentApi.completeSession(s.id)
    const mins = Math.floor((r.data?.duration_seconds || 0) / 60)
    showToast(`Session marked complete${mins ? ` · ${mins} min recorded` : ''}.`, 'success')
    await loadSessions(false)
  } catch (e) {
    showToast(e?.message || 'Unable to complete session.', 'error')
  } finally {
    busy.value = null
  }
}

function meetingLabel(s) {
  return s?.meeting_lifecycle || s?.meeting_status || 'Meeting Not Started'
}

// Same Regular=blue / One-to-One=violet convention used on the tutor
// schedule and the session booking pages, so students see one consistent
// colour language for session type everywhere in the app.
function isOneToOne(s) {
  return (s?.type || s?.meeting_type_label || '').toLowerCase().includes('one')
}

function typeBadgeClasses(s) {
  return isOneToOne(s)
    ? 'bg-violet-50 text-violet-700 dark:bg-violet-900/20 dark:text-violet-300'
    : 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300'
}

onMounted(async () => {
  await loadSessions()
  await loadTutors()
  // The server is the source of truth for the lifecycle. Polling makes the
  // Join Meeting button appear/disappear automatically without a page reload.
  refreshTimer = window.setInterval(() => loadSessions(false), 15000)
})

onUnmounted(() => {
  if (refreshTimer) window.clearInterval(refreshTimer)
})
</script>

<template>
  <div>
    <PageHeader title="My Sessions" subtitle="View your booked tuition sessions." />

    <div class="card mb-6 px-5 py-5">
      <h3 class="font-display text-lg font-bold text-slate-800 dark:text-white">Request a Meeting</h3>
      <p class="mb-3 text-xs text-slate-500">Ask a tutor for a one-on-one session at a time that works for you.</p>
      <div class="grid grid-cols-1 gap-2.5 sm:grid-cols-2 lg:grid-cols-5">
        <select v-model="requestForm.tutor_id" class="rounded-lg border border-slate-200 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900">
          <option value="">Choose tutor</option>
          <option v-for="t in tutors" :key="t.tutor_id" :value="t.tutor_id">{{ t.name }}</option>
        </select>
        <input v-model="requestForm.date" type="date" class="rounded-lg border border-slate-200 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900">
        <input v-model="requestForm.startTime" type="time" class="rounded-lg border border-slate-200 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900">
        <input v-model="requestForm.endTime" type="time" class="rounded-lg border border-slate-200 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900" placeholder="End (optional)">
        <button
          type="button"
          class="rounded-lg bg-gradient-to-r from-teal-500 to-blue-500 px-3 py-2 text-xs font-bold text-white disabled:opacity-50"
          :disabled="requesting"
          @click="submitMeetingRequest"
        >{{ requesting ? 'Requesting...' : 'Request Meeting' }}</button>
      </div>
      <input v-model="requestForm.notes" class="mt-2.5 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-900" placeholder="What would you like to discuss? (optional)">
    </div>

    <div v-if="loading" class="py-10 text-center text-sm text-slate-500">Loading sessions...</div>

    <div v-else-if="error" class="mb-5 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600">
      {{ error }}
      <button class="ml-2 font-semibold underline" @click="loadSessions">Retry</button>
    </div>

    <template v-else>
      <section class="mb-7">
        <div class="mb-3 flex items-center justify-between">
          <div>
            <h3 class="font-display text-lg font-bold text-slate-800 dark:text-white">Upcoming Sessions</h3>
            <p class="text-xs text-slate-500">Your scheduled tuition sessions</p>
          </div>
          <span v-if="data.upcoming.length" class="rounded-full bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-700">
            {{ data.upcoming.length }} {{ data.upcoming.length === 1 ? 'session' : 'sessions' }}
          </span>
        </div>

        <div v-if="!data.upcoming.length" class="card px-5 py-5 text-sm text-slate-500">No upcoming sessions booked.</div>

        <div v-else class="space-y-2.5">
          <div
            v-for="s in data.upcoming"
            :key="s.id"
            class="group flex items-center gap-4 rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm transition hover:border-teal-200 hover:shadow-md dark:border-slate-700 dark:bg-slate-900"
          >
            <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-teal-500 text-sm font-bold text-white">
              {{ s.subject?.charAt(0)?.toUpperCase() || '?' }}
            </div>

            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <h4 class="font-display font-bold text-slate-800 dark:text-white">{{ s.subject }}</h4>
                <StatusBadge :status="meetingLabel(s)" />
              </div>
              <div class="mt-1 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500">
                <span
                  v-if="s.meeting_type_label"
                  class="rounded-full px-2 py-0.5 text-[11px] font-bold"
                  :class="typeBadgeClasses(s)"
                >{{ s.meeting_type_label }}</span>
                <span v-if="s.created_by_label">{{ s.created_by_label }}</span>
                <span>👨‍🏫 {{ s.tutor }}</span>
                <span v-if="s.parent">👪 {{ s.parent }}</span>
                <span>📅 {{ s.date }}</span>
                <span>🕐 {{ s.time }} – {{ s.end_time }}</span>
                <span v-if="s.duration">⏱ {{ s.duration }}</span>
              </div>
              <div v-if="s.meeting_reason" class="mt-1 truncate text-xs text-slate-500">Reason: {{ s.meeting_reason }}</div>
              <div v-if="s.attendance_status" class="mt-1 text-[11px] font-semibold text-slate-400">
                Attendance: {{ s.attendance_status }}
              </div>
            </div>

            <div class="flex shrink-0 flex-wrap items-center justify-end gap-2">
              <button
                v-if="s.can_join && s.meeting_request_status !== 'Pending Approval'"
                type="button"
                class="rounded-lg bg-gradient-to-r from-teal-500 to-blue-500 px-3 py-2 text-xs font-bold text-white"
                :disabled="busy === s.id"
                @click="joinSession(s)"
              >Join Meeting</button>
              <a
                v-else-if="s.meeting_url || s.meetingUrl"
                :href="s.meeting_url || s.meetingUrl"
                target="_blank"
                rel="noopener noreferrer"
                class="rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-600 dark:bg-slate-800 dark:text-slate-300"
              >Meeting Link</a>
              <span v-else-if="meetingLabel(s) === 'Meeting Not Started'" class="rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-500 dark:bg-slate-800 dark:text-slate-400">
                Meeting Not Started
              </span>
              <button
                v-if="s.can_complete"
                type="button"
                class="rounded-lg border border-emerald-200 px-3 py-2 text-xs font-semibold text-emerald-700"
                :disabled="busy === s.id"
                @click="completeSession(s)"
              >Mark as Attended</button>
            </div>
          </div>
        </div>
      </section>

      <section>
        <div class="mb-3">
          <h3 class="font-display text-lg font-bold text-slate-800 dark:text-white">Completed Sessions</h3>
          <p class="text-xs text-slate-500">Previous tuition sessions and ended meetings</p>
        </div>

        <div v-if="!data.completed.length" class="card px-5 py-5 text-sm text-slate-500">No completed sessions yet.</div>
        <div v-else class="space-y-2">
          <div v-for="s in data.completed" :key="s.id" class="flex items-center gap-4 rounded-xl border border-slate-200 bg-white px-4 py-3 dark:border-slate-700 dark:bg-slate-900">
            <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-sm font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
              {{ s.subject?.charAt(0)?.toUpperCase() || '?' }}
            </div>
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <h4 class="font-semibold text-slate-800 dark:text-white">{{ s.subject }}</h4>
                <StatusBadge :status="meetingLabel(s)" />
              </div>
              <div class="mt-1 flex flex-wrap gap-x-4 text-xs text-slate-500">
                <span>👨‍🏫 {{ s.tutor }}</span>
                <span v-if="s.parent">👪 {{ s.parent }}</span>
                <span>📅 {{ s.date }} · {{ s.time }} – {{ s.end_time }}</span>
                <span v-if="s.meeting_request_status === 'Pending Approval'" class="text-[11px] font-semibold text-indigo-600">Tutor approval pending</span>
                <span v-if="s.attendance_status">Attendance: {{ s.attendance_status }}</span>
              </div>
              <div v-if="s.topics?.length || s.homework" class="mt-1 text-xs text-slate-400">
                <span v-if="s.topics?.length">Topics: {{ s.topics.join(', ') }}</span>
                <span v-if="s.homework" class="ml-3">Homework: {{ s.homework }}</span>
              </div>
            </div>
            <button v-if="s.can_complete" type="button" class="rounded-lg border border-emerald-200 px-3 py-2 text-xs font-semibold text-emerald-700" :disabled="busy === s.id" @click="completeSession(s)">Mark as Attended</button>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>
