<script setup>
import { ref } from 'vue'
import { parentApi } from '@/api/parentApi'

const props = defineProps({
  parentId: { type: Number, required: true },
  tutorId: { type: Number, required: true },
  studentId: { type: Number, required: true }
})

const preferredDate = ref('')
const preferredTime = ref('')
const meetingType = ref('Virtual')
const notes = ref('')
const loading = ref(false)
const feedback = ref(null)

async function handleScheduleMeeting() {
  loading.value = true
  feedback.value = null
  
  try {
    const payload = {
      parent_id: props.parentId,
      tutor_id: props.tutorId,
      student_id: props.studentId,
      preferred_date: preferredDate.value,
      preferred_time: preferredTime.value,
      meeting_type: meetingType.value,
      notes: notes.value
    }
    
    const res = await parentApi.requestMeeting(payload)
    feedback.value = { type: 'success', text: res.message || 'Meeting requested successfully!' }
    
    // Reset form
    preferredDate.value = ''
    preferredTime.value = ''
    notes.value = ''
  } catch (err) {
    feedback.value = { type: 'error', text: err.message || 'Failed to submit meeting request.' }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="card p-6 max-w-lg mx-auto">
    <h2 class="text-xl font-semibold mb-4">Request a Tutor Meeting</h2>
    
    <div v-if="feedback" :class="feedback.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="p-3 rounded-lg text-sm mb-4">
      {{ feedback.text }}
    </div>

    <form @submit.prevent="handleScheduleMeeting" class="space-y-4">
      <div>
        <label class="block text-xs font-semibold uppercase mb-1">Preferred Date</label>
        <input type="date" v-model="preferredDate" class="input-field" required />
      </div>

      <div>
        <label class="block text-xs font-semibold uppercase mb-1">Preferred Time</label>
        <input type="time" v-model="preferredTime" class="input-field" required />
      </div>

      <div>
        <label class="block text-xs font-semibold uppercase mb-1">Type</label>
        <select v-model="meetingType" class="input-field">
          <option value="Virtual">Virtual (Online)</option>
          <option value="In-Person">In-Person</option>
        </select>
      </div>

      <div>
        <label class="block text-xs font-semibold uppercase mb-1">Notes / Topic</label>
        <textarea v-model="notes" rows="3" class="input-field" placeholder="Describe what you would like to discuss..."></textarea>
      </div>

      <button type="submit" :disabled="loading" class="btn-primary w-full justify-center">
        {{ loading ? 'Submitting...' : 'Request Meeting' }}
      </button>
    </form>
  </div>
</template>