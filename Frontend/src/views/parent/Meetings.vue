<script setup>
import { reactive, onMounted } from 'vue'
import { VideoCameraIcon, PlusIcon } from '@heroicons/vue/24/outline'
import EmptyState from '../../components/ui/EmptyState.vue'
import { useToast } from '../../composables/useToast'
import { useParentPortal } from '../../composables/useParentPortal'

const { showToast } = useToast()
const { children, meetings, loadProfile, loadMeetings, submitMeetingRequest } = useParentPortal()

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
  if (status === 'Scheduled') return 'bg-brand-blue-100 text-brand-blue-700 dark:bg-brand-blue-500/15 dark:text-brand-blue-400'
  return 'bg-brand-purple-100 text-brand-purple-700 dark:bg-brand-purple-500/15 dark:text-brand-purple-400'
}

const requestForm = reactive({
  reason: '',
  preferredDate: '',
  student_id: null,
  tutor_id: null
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
      tutor_id: requestForm.tutor_id
    })

    requestForm.reason = ''
    requestForm.preferredDate = ''
    requestForm.student_id = children.value[0]?.student_id || null
    requestForm.tutor_id = children.value[0]?.tutor_id || null

    showToast('Meeting request sent. The tutor will confirm soon.', 'success')
  } catch (err) {
    showToast(err.message || 'Failed to send meeting request.', 'error')
  }
}

onMounted(async () => {
  try {
    await loadProfile()
    requestForm.student_id = children.value[0]?.student_id || null
    requestForm.tutor_id = children.value[0]?.tutor_id || null
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
              {{ m.status }}
            </span>
            <span class="text-xs text-slate-400">{{ formatDateTime(m.meeting_date) }}</span>
          </div>
          <p class="text-sm text-slate-700 dark:text-slate-300 mt-2">{{ m.meeting_reason }}</p>
          <a v-if="m.meeting_link" :href="m.meeting_link" target="_blank" rel="noopener" class="btn-secondary mt-3 w-full justify-center">
            <VideoCameraIcon class="w-4 h-4" />
            Join Meeting
          </a>
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