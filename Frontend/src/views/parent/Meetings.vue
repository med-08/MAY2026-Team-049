<script setup>
import { reactive } from 'vue'
import { VideoCameraIcon, PlusIcon } from '@heroicons/vue/24/outline'
import EmptyState from '../../components/ui/EmptyState.vue'
import { useToast } from '../../composables/useToast'
import { useParentPortal } from '../../composables/useParentPortal'
import { meetingRequests } from '../../data/parentMockData'

const { showToast } = useToast()
const { parentMeetingRequests } = useParentPortal(1)

function formatDateTime(dateStr) {
  return new Date(dateStr).toLocaleString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
}

function statusStyle(status) {
  if (status === 'Completed') return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-400'
  if (status === 'Cancelled') return 'bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-400'
  return 'bg-brand-purple-100 text-brand-purple-700 dark:bg-brand-purple-500/15 dark:text-brand-purple-400'
}

// Story 3.3 is tutor-initiated in the DB design (MeetingRequest has no requester
// role column), so a parent "request" is modeled the same way — a new record
// awaiting the tutor's confirmation.
const requestForm = reactive({ reason: '', preferredDate: '' })
let meetingSeq = meetingRequests.length + 1

function submitRequest() {
  if (!requestForm.reason.trim() || !requestForm.preferredDate) {
    showToast('Add a reason and preferred date/time.', 'error')
    return
  }
  meetingRequests.push({
    meeting_id: meetingSeq++,
    tutor_id: 1,
    student_id: null,
    parent_id: 1,
    meeting_date: requestForm.preferredDate,
    meeting_link: null,
    meeting_reason: requestForm.reason,
    status: 'Requested'
  })
  requestForm.reason = ''
  requestForm.preferredDate = ''
  showToast('Meeting request sent. The tutor will confirm within 48 hours.')
}
</script>

<template>
  <div class="space-y-6">
    <div class="card p-5">
      <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">Your Meeting Requests</h3>
      <div v-if="parentMeetingRequests.length" class="grid sm:grid-cols-2 gap-4">
        <div v-for="m in parentMeetingRequests" :key="m.meeting_id" class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
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
        Can't make it in person? Request a virtual check-in with the tutor and they'll confirm a time within 48 hours.
      </p>
      <div class="space-y-3">
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
