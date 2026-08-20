<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ClockIcon, VideoCameraIcon, CalendarDaysIcon, PencilSquareIcon, XMarkIcon, CheckBadgeIcon } from '@heroicons/vue/24/outline'
import { parentApi } from '../../services/parentApi'
import { useParentPortal } from '../../composables/useParentPortal'
import { useToast } from '../../composables/useToast'

const { parentId, children, loadProfile } = useParentPortal()
const { showToast } = useToast()
const rows = ref([])
const loading = ref(true)
const error = ref('')
const saving = ref(false)
const editingId = ref(null)

const form = reactive({
  student_id: null,
  tutor_id: null,
  preferredDate: '',
  preferredEndDate: '',
  reason: ''
})

const selectedChild = computed(() => children.value.find(c => Number(c.student_id) === Number(form.student_id)) || null)
const availableTutors = computed(() => selectedChild.value?.tutors || [])
const selectedTutor = computed(() => availableTutors.value.find(t => Number(t.tutor_id) === Number(form.tutor_id)) || null)

function statusLabel(s) {
  return s.meeting_lifecycle || s.status || 'Meeting Not Started'
}

function canEdit(s) {
  return ['Scheduled', 'Rescheduled'].includes(s.status) && statusLabel(s) === 'Meeting Not Started'
}

async function load() {
  if (!parentId.value) return
  loading.value = true
  error.value = ''
  try {
    const r = await parentApi.getSchedule(parentId.value)
    rows.value = r.data || []
  } catch (e) {
    error.value = e?.message || 'Unable to load family schedule.'
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.student_id = children.value[0]?.student_id || null
  form.tutor_id = children.value[0]?.tutors?.length === 1 ? children.value[0].tutors[0].tutor_id : null
  form.preferredDate = ''
  form.preferredEndDate = ''
  form.reason = ''
  editingId.value = null
}

async function scheduleMeeting() {
  if (!form.student_id || !form.tutor_id || !selectedChild.value || !form.preferredDate || !form.preferredEndDate) {
    showToast('Select a child and enter start/end date and time.', 'error')
    return
  }
  saving.value = true
  try {
    const [preferred_date, preferred_time] = form.preferredDate.split('T')
    const [, preferred_end_time] = form.preferredEndDate.split('T')
    await parentApi.requestMeeting({
      parent_id: parentId.value,
      tutor_id: form.tutor_id,
      student_id: form.student_id,
      preferred_date,
      preferred_time,
      preferred_end_time,
      notes: form.reason
    })
    showToast('Meeting scheduled. Student and tutor have been notified.', 'success')
    resetForm()
    await load()
  } catch (e) {
    showToast(e?.message || 'Unable to schedule meeting.', 'error')
  } finally {
    saving.value = false
  }
}

function editSession(s) {
  editingId.value = s.session_id
  form.student_id = s.student_id
  form.tutor_id = s.tutor_id
  form.preferredDate = `${s.date}T${s.start_time}`
  form.preferredEndDate = `${s.date}T${s.end_time}`
  form.reason = ''
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

async function saveEdit() {
  if (!editingId.value || !form.preferredDate || !form.preferredEndDate) return
  saving.value = true
  try {
    const [date, start_time] = form.preferredDate.split('T')
    const [, end_time] = form.preferredEndDate.split('T')
    await parentApi.updateScheduleSession(editingId.value, { session_date: date, start_time, end_time })
    showToast('Meeting schedule updated. Student and tutor were notified.', 'success')
    resetForm()
    await load()
  } catch (e) {
    showToast(e?.message || 'Unable to update meeting.', 'error')
  } finally {
    saving.value = false
  }
}

async function cancelSession(s) {
  if (!confirm(`Cancel the ${s.subject} session for ${s.student_name}?`)) return
  try {
    await parentApi.cancelScheduleSession(s.session_id)
    showToast('Meeting cancelled and participants notified.', 'success')
    await load()
  } catch (e) {
    showToast(e?.message || 'Unable to cancel meeting.', 'error')
  }
}

async function startSession(s) {
  try {
    const r = await parentApi.startScheduleSession(s.session_id)
    const url = r?.data?.meeting_url || s.meeting_url
    showToast('Meeting started. Student and tutor were notified.', 'success')
    if (url) window.open(url, '_blank', 'noopener,noreferrer')
    await load()
  } catch (e) { showToast(e?.message || 'Unable to start meeting.', 'error') }
}

async function requestConfirmation(s) {
  try {
    await parentApi.requestAttendanceConfirmation(s.student_id, s.session_id)
    showToast('Attendance confirmation request sent to the tutor.', 'success')
    await load()
  } catch (e) {
    showToast(e?.message || 'Unable to request tutor confirmation.', 'error')
  }
}

watch(() => form.student_id, () => {
  const tutors = selectedChild.value?.tutors || []
  form.tutor_id = tutors.length === 1 ? tutors[0].tutor_id : null
})

onMounted(async () => {
  try { await loadProfile() } catch {}
  resetForm()
  await load()
})
</script>

<template>
  <div class="space-y-5">
    <div class="flex items-end justify-between">
      <div>
        <h2 class="font-display text-xl font-bold text-slate-800 dark:text-white">Connect with Your Child</h2>
        <p class="mt-1 text-xs text-slate-500">Schedule and monitor one shared session for your child, tutor and parent.</p>
      </div>
      <span v-if="!loading" class="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-600">{{ rows.length }} sessions</span>
    </div>

    <div class="card p-5">
      <div class="flex items-center justify-between gap-3 mb-4">
        <div>
          <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100">{{ editingId ? 'Reschedule meeting' : 'Schedule a one-on-one meeting' }}</h3>
          <p class="mt-1 text-xs text-slate-500">This creates one shared Session record for the child, tutor and parent.</p>
        </div>
        <button v-if="editingId" type="button" class="text-xs font-semibold text-slate-500 hover:underline" @click="resetForm">Cancel edit</button>
      </div>

      <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
        <div>
          <label class="text-xs font-semibold text-slate-500 mb-1 block">Child</label>
          <select v-model="form.student_id" class="input-field" :disabled="!!editingId">
            <option :value="null" disabled>Select child</option>
            <option v-for="child in children" :key="child.student_id" :value="child.student_id">{{ child.student_name }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-semibold text-slate-500 mb-1 block">Tutor</label>
          <select v-model="form.tutor_id" class="input-field" :disabled="!!editingId">
            <option :value="null" disabled>Select tutor</option>
            <option v-for="t in availableTutors" :key="t.tutor_id" :value="t.tutor_id">{{ t.tutor_name }}</option>
          </select>
        </div>
        <div>
          <label class="text-xs font-semibold text-slate-500 mb-1 block">Start</label>
          <input v-model="form.preferredDate" type="datetime-local" class="input-field" />
        </div>
        <div>
          <label class="text-xs font-semibold text-slate-500 mb-1 block">End</label>
          <input v-model="form.preferredEndDate" type="datetime-local" class="input-field" />
        </div>
        <div>
          <label class="text-xs font-semibold text-slate-500 mb-1 block">Note</label>
          <input v-model="form.reason" type="text" placeholder="Optional reason" class="input-field" />
        </div>
      </div>
      <p v-if="selectedChild && !availableTutors.length" class="mt-2 text-xs text-amber-600">No tutor is currently associated with this child. Select a child with an existing tutor/session relationship.</p>
      <button v-if="!editingId" class="btn-primary mt-4" :disabled="saving" @click="scheduleMeeting">{{ saving ? 'Scheduling...' : 'Schedule Meeting' }}</button>
      <button v-else class="btn-primary mt-4" :disabled="saving" @click="saveEdit">{{ saving ? 'Saving...' : 'Save Reschedule' }}</button>
    </div>

    <div v-if="loading" class="card p-8 text-center text-sm text-slate-500">Loading schedule...</div>
    <div v-else-if="error" class="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600">{{ error }} <button class="ml-2 font-semibold underline" @click="load">Retry</button></div>
    <div v-else-if="!rows.length" class="card border-dashed p-8 text-center text-sm text-slate-500">No parent-created child meetings yet.</div>

    <div v-else class="grid gap-3 lg:grid-cols-2">
      <div v-for="s in rows" :key="`${s.student_id}-${s.session_id}`" class="card p-4 transition hover:-translate-y-0.5 hover:shadow-md">
        <div class="flex items-start gap-3">
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-teal-500 text-sm font-bold text-white">{{ s.subject?.charAt(0) || '?' }}</div>
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <h3 class="font-display font-bold">{{ s.subject }}</h3>
              <span class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-300">{{ statusLabel(s) }}</span>
            </div>
            <p class="mt-1 text-xs text-slate-500">{{ s.student_name }} · Tutor: {{ s.tutor }}</p>
            <p v-if="s.meeting_reason" class="mt-1 text-xs text-slate-500">Reason: {{ s.meeting_reason }}</p>
            <p v-if="s.meeting_request_status" class="mt-1 text-[11px] font-semibold text-indigo-600">Request: {{ s.meeting_request_status }}</p>
            <div class="mt-2 flex flex-wrap gap-x-4 text-xs text-slate-500">
              <span class="inline-flex items-center gap-1"><CalendarDaysIcon class="h-3.5 w-3.5"/>{{ s.date }}</span>
              <span class="inline-flex items-center gap-1"><ClockIcon class="h-3.5 w-3.5"/>{{ s.start_time }}–{{ s.end_time }}</span>
            </div>
            <p class="mt-2 text-xs font-semibold" :class="s.attendance_status === 'Present' ? 'text-emerald-600' : s.attendance_status === 'Absent' ? 'text-rose-600' : 'text-slate-500'">
              Attendance: {{ s.attendance_status || 'Not recorded' }}
            </p>
          </div>
        </div>

        <div class="mt-3 flex flex-wrap justify-end gap-2">
          <button v-if="s.meeting_request_status === 'Scheduled' && s.can_start && !s.meeting_started_at" type="button" class="inline-flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-indigo-500 to-blue-500 px-3 py-2 text-xs font-bold text-white" @click="startSession(s)">Start Meeting</button>
          <a v-if="s.can_join && s.meeting_request_status !== 'Pending Approval'" :href="s.meeting_url || s.meetingUrl" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1.5 rounded-lg bg-gradient-to-r from-teal-500 to-blue-500 px-3 py-2 text-xs font-bold text-white"><VideoCameraIcon class="h-4 w-4"/>Join Meeting</a>
          <span v-else-if="statusLabel(s) === 'Meeting Not Started'" class="rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-500 dark:bg-slate-800 dark:text-slate-400">Meeting Not Started</span>
          <span v-else class="rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-500 dark:bg-slate-800 dark:text-slate-400">Meeting Ended</span>
          <button v-if="canEdit(s)" type="button" class="btn-secondary" @click="editSession(s)"><PencilSquareIcon class="w-4 h-4"/>Edit</button>
          <button v-if="canEdit(s)" type="button" class="inline-flex items-center gap-1 rounded-lg border border-rose-200 px-3 py-2 text-xs font-semibold text-rose-600" @click="cancelSession(s)"><XMarkIcon class="w-4 h-4"/>Cancel</button>
          <button v-if="s.meeting_lifecycle === 'Meeting Ended' && !s.attendance_status" type="button" class="inline-flex items-center gap-1 rounded-lg border border-indigo-200 px-3 py-2 text-xs font-semibold text-indigo-600" @click="requestConfirmation(s)"><CheckBadgeIcon class="w-4 h-4"/>Ask Tutor to Confirm Attendance</button>
          <span v-if="s.attendance_status === 'Pending'" class="rounded-lg bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-700">Tutor confirmation pending</span>
        </div>
      </div>
    </div>
  </div>
</template>
