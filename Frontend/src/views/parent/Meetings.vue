<script setup>
import { reactive, ref, onMounted, computed, watch } from 'vue'
import { VideoCameraIcon, PlusIcon } from '@heroicons/vue/24/outline'
import EmptyState from '../../components/ui/EmptyState.vue'
import { useToast } from '../../composables/useToast'
import { useParentPortal } from '../../composables/useParentPortal'
import { parentApi } from '../../services/parentApi'

const { showToast } = useToast()
const { children, meetings, loadProfile, loadMeetings, submitMeetingRequest } = useParentPortal()
const endingMeetingId = ref(null)

function formatDateTime(dateStr) {
  return new Date(dateStr).toLocaleString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit'
  })
}

function statusStyle(status) {
  if (status === 'Completed') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400'
  if (status === 'Cancelled') return 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-400'
  if (status === 'Meeting Started') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400'
  if (status === 'Meeting Not Started') return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
  if (status === 'Meeting Ended') return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
  if (status === 'Request Accepted') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400'
  if (status === 'Awaiting Tutor Approval') return 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-400'
  if (status === 'Denied') return 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-400'
  if (status === 'Reschedule Requested') return 'bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-400'
  if (status === 'Scheduled') return 'bg-brand-blue-100 text-brand-blue-700 dark:bg-brand-blue-500/15 dark:text-brand-blue-400'
  return 'bg-brand-purple-100 text-brand-purple-700 dark:bg-brand-purple-500/15 dark:text-brand-purple-400'
}

const requestForm = reactive({
  reason: '',
  preferredDate: '',
  student_id: null,
  tutor_id: null,
  includeStudent: true
})
const selectedChild = computed(() => children.value.find(c => Number(c.student_id) === Number(requestForm.student_id)) || null)
const availableTutors = computed(() => selectedChild.value?.tutors || [])
watch(() => requestForm.student_id, () => {
  requestForm.tutor_id = availableTutors.value.length === 1 ? availableTutors.value[0].tutor_id : null
})

async function submitRequest() {
  if (!requestForm.reason.trim() || !requestForm.preferredDate || !requestForm.student_id || !requestForm.tutor_id) {
    showToast('Select child, add a reason and preferred date/time.', 'error')
    return
  }

  try {
    await submitMeetingRequest({
      reason: requestForm.reason,
      preferredDate: requestForm.preferredDate,
      student_id: requestForm.student_id,
      tutor_id: requestForm.tutor_id,
      includeStudent: requestForm.includeStudent
    })

    requestForm.reason = ''
    requestForm.preferredDate = ''
    requestForm.includeStudent = true
    requestForm.student_id = children.value[0]?.student_id || null
    requestForm.tutor_id = children.value[0]?.tutors?.length === 1 ? children.value[0].tutors[0].tutor_id : null

    showToast('Meeting request sent. The tutor will confirm soon.', 'success')
  } catch (err) {
    showToast(err.message || 'Failed to send meeting request.', 'error')
  }
}

async function endMeeting(meeting) {
  if (!meeting?.session_id) return

  if (!confirm('Are you sure you want to end this meeting?')) return

  endingMeetingId.value = meeting.meeting_id

  try {
    await parentApi.endScheduleSession(meeting.session_id)
    showToast('Meeting ended successfully.', 'success')
    await loadMeetings()
  } catch (err) {
    showToast(err.message || 'Failed to end the meeting.', 'error')
  } finally {
    endingMeetingId.value = null
  }
}


onMounted(async () => {
  try {
    await loadProfile()
    requestForm.student_id = children.value[0]?.student_id || null
    requestForm.tutor_id = children.value[0]?.tutors?.length === 1 ? children.value[0].tutors[0].tutor_id : null
    await loadMeetings()
  } catch (err) {
    showToast(err.message || 'Failed to load meetings.', 'error')
  }
})
</script>

<template>
  <div class="space-y-6">
    <div class="card p-5">
      <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">Your Meeting Requests</h3>
      <div v-if="meetings.length" class="grid sm:grid-cols-2 gap-4">
        <div v-for="m in meetings" :key="m.meeting_id" class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold px-2 py-0.5 rounded-full" :class="statusStyle(m.status)">
              {{ m.meeting_lifecycle || m.status }}
            </span>
            <span class="text-xs text-slate-400">{{ formatDateTime(m.meeting_date) }}</span>
          </div>
          <div class="mt-2 space-y-1 text-sm text-slate-700 dark:text-slate-300"><p class="font-semibold">{{ m.subject }} · {{ m.tutor_name }} <span class="text-xs font-medium text-slate-400">· {{ m.session_type || 'One-to-One' }}</span></p><p>{{ formatDateTime(m.meeting_date) }}<span v-if="m.end_time"> · {{ m.start_time }}–{{ m.end_time }}</span></p><p v-if="m.student_name" class="text-xs text-slate-500">Child: {{ m.student_name }}</p><p v-if="m.meeting_reason" class="text-xs text-slate-500">Reason: {{ m.meeting_reason }}</p><p v-if="m.status !== 'Scheduled'" class="text-xs font-semibold text-indigo-600">Request status: {{ m.status }}</p><p v-if="m.tutor_message" class="text-xs rounded-lg bg-amber-50 dark:bg-amber-500/10 px-3 py-2 text-slate-600 dark:text-slate-300"><strong>Tutor message:</strong> {{ m.tutor_message }}</p></div>
          <a v-if="m.can_join && m.meeting_link" :href="m.meeting_link" target="_blank" rel="noopener" class="btn-secondary mt-3 w-full justify-center">
            <VideoCameraIcon class="w-4 h-4" />
            Join Meeting
          </a>

          <button
            v-if="m.can_end"
            type="button"
            class="mt-3 w-full rounded-lg bg-rose-600 px-3 py-2 text-sm font-bold text-white hover:bg-rose-700 disabled:opacity-50"
            :disabled="endingMeetingId === m.meeting_id"
            @click="endMeeting(m)"
          >
            {{ endingMeetingId === m.meeting_id ? 'Ending...' : 'End Meeting' }}
          </button>

          <div v-if="!m.can_join && !m.can_end" class="mt-3 rounded-lg bg-slate-100 dark:bg-slate-800 px-3 py-2 text-center text-xs font-semibold text-slate-500">
            {{ m.meeting_lifecycle || 'Meeting Not Started' }}
          </div>
        </div>
      </div>
      <EmptyState v-else title="No meeting requests" message="Requests with the tutor will show up here." />
    </div>

    <div class="card p-5">
      <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4 flex items-center gap-2">
        <PlusIcon class="w-5 h-5 text-brand-green-500" />
        Request a Virtual Meeting
      </h3>
      <p class="text-sm text-slate-500 dark:text-slate-400 mb-4">
        Can't make it in person? Request a virtual check-in with the tutor and they'll confirm a time.
      </p>
      <div class="space-y-3">
        <div>
          <label class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block">Child</label>
          <select v-model="requestForm.student_id" class="input-field">
            <option :value="null" disabled>Select child</option>
            <option v-for="child in children" :key="child.student_id" :value="child.student_id">
              {{ child.student_name }}
            </option>
          </select>
        </div>

        <div>
          <label class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block">Tutor</label>
          <select v-model="requestForm.tutor_id" class="input-field">
            <option :value="null" disabled>Select tutor</option>
            <option v-for="t in availableTutors" :key="t.tutor_id" :value="t.tutor_id">{{ t.tutor_name }}</option>
          </select>
        </div>

        <label class="flex items-center gap-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 px-3 py-3 cursor-pointer">
          <input v-model="requestForm.includeStudent" type="checkbox" class="w-4 h-4">
          <span>
            <span class="block text-sm font-semibold">Include student in this meeting</span>
            <span class="block text-xs text-slate-500">Turn this off for a private parent–tutor one-to-one.</span>
          </span>
        </label>

        <div>
          <label class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block">Reason for meeting</label>
          <input v-model="requestForm.reason" type="text" placeholder="e.g. Discuss upcoming exam preparation" class="input-field" />
        </div>

        <div>
          <label class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block">Preferred date & time</label>
          <input v-model="requestForm.preferredDate" type="datetime-local" class="input-field" />
        </div>

        <button class="btn-primary" @click="submitRequest">
          Send Request
        </button>
      </div>
    </div>
  </div>
</template>