<template>
  <section class="view on">

    <!-- Schedule Form -->
    <div class="card glass reveal">
      <div class="ch">
        <h3>Schedule</h3>
      </div>

      <div
        class="grid"
        style="grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:18px"
      >

        <!-- Subject -->
        <div>
          <label class="lab">Subject</label>

          <select
            v-model="form.subject_id"
            class="field"
          >
            <option value="">Choose</option>

            <option
              v-for="s in subjectOptions"
              :key="s.subjectId"
              :value="s.subjectId"
            >
              {{ s.subject }}
            </option>
          </select>
        </div>

        <!-- Date -->
        <div>
          <label class="lab">Date</label>

          <input
            v-model="form.session_date"
            type="date"
            class="field"
          >
        </div>

        <!-- Start -->
        <div>
          <label class="lab">Start</label>

          <input
            v-model="form.start_time"
            type="time"
            class="field"
          >
        </div>

        <!-- End -->
        <div>
          <label class="lab">End</label>

          <input
            v-model="form.end_time"
            type="time"
            class="field"
          >
        </div>

        <!-- Type -->
        <div>
          <label class="lab">Type</label>

          <select
            v-model="form.session_type"
            class="field"
          >
            <option>Regular</option>
            <option>One-to-One</option>
          </select>
        </div>

      </div>

      <button
        class="btn grad"
        @click="add"
        :disabled="loading"
      >
        {{ loading ? 'Adding...' : 'Add Session' }}
      </button>

      <p
        v-if="message"
        class="eyebrow"
        style="margin-top:10px"
      >
        {{ message }}
      </p>
    </div>


    <!-- Existing Sessions -->
    <div
      class="card glass reveal"
      style="margin-top:18px"
    >

      <div class="ch">
        <h3>Existing sessions</h3>
      </div>

      <div
        v-if="!sessions.length"
        class="eyebrow"
      >
        No sessions yet.
      </div>

      <div
        v-for="s in sessions"
        :key="s.id"
        class="row"
      >
        <div class="g1">

          <div class="t">
            {{ s.subject }}
          </div>

          <div class="s">
            {{ s.date }}
            ·
            {{ s.time }}
            –
            {{ s.endTime }}
            ·
            {{ s.classLevel }}
          </div>

        </div>

        <div class="flex items-center gap-2">
          <span class="badge">
            {{ s.badge }}
          </span>

          <button
            v-if="s.badge === 'Scheduled' || s.badge === 'Rescheduled'"
            type="button"
            class="btn grad sm inline-flex items-center justify-center gap-2"
            :disabled="startingSessionId === s.id"
            @click="startSession(s)"
          >
            <span v-if="startingSessionId === s.id">Starting...</span>
            <span v-else>Start Session</span>
          </button>
        </div>

      </div>

    </div>

  </section>
</template>


<script setup>
import { computed, reactive, ref } from 'vue'
import { tutorApi } from '../../services/tutorApi'


const props = defineProps({

  rows: {
    type: Array,
    required: true
  },

  events: {
    type: Array,
    required: true
  },

  sessions: {
    type: Array,
    default: () => []
  },

  /*
   * NEW:
   * Subjects returned by the real backend.
   *
   * Example:
   *
   * [
   *   {
   *     subjectId: 1,
   *     subject: "Mathematics"
   *   },
   *   {
   *     subjectId: 2,
   *     subject: "Physics"
   *   }
   * ]
   */
  subjects: {
    type: Array,
    default: () => []
  }

})


const emit = defineEmits(['toast'])


const form = reactive({
  subject_id: '',
  session_date: '',
  start_time: '16:00',
  end_time: '17:00',
  session_type: 'Regular'
})


const message = ref('')
const loading = ref(false)
const startingSessionId = ref(null)


const sessions = computed(() => props.sessions)


/*
 * Subject dropdown.
 *
 * IMPORTANT:
 *
 * Previously this was:
 *
 * props.sessions.forEach(...)
 *
 * That meant:
 *
 * No existing sessions
 *        ↓
 * No subjects
 *        ↓
 * Cannot create first session
 *
 * Now we use the real subjects returned by
 * /tutor/schedule.
 *
 * We keep the old session-based logic as a
 * fallback so existing behaviour is preserved.
 */
const subjectOptions = computed(() => {

  // Preferred source:
  // real subjects returned by backend
  if (props.subjects && props.subjects.length) {
    return props.subjects
  }


  // Backward-compatible fallback:
  // derive subjects from existing sessions
  const map = new Map()

  props.sessions.forEach((s) => {

    if (!s.subjectId) {
      return
    }

    map.set(
      s.subjectId,
      {
        subjectId: s.subjectId,
        subject: s.subject
      }
    )

  })


  return [...map.values()]
})


async function startSession(s) {
  const existingUrl = s?.meetingUrl || s?.meeting_url

  // If a Meet already exists, open it immediately.
  if (existingUrl) {
    window.open(existingUrl, '_blank', 'noopener,noreferrer')
    return
  }

  // Open a tab immediately from the user click so popup blockers do not
  // prevent the newly-created Meet URL from opening after the API call.
  const popup = window.open('about:blank', '_blank')
  startingSessionId.value = s.id
  message.value = ''

  try {
    const result = await tutorApi.startClass(s.id)
    const meetingUrl = result?.data?.meeting_url || result?.meeting_url

    if (!meetingUrl) {
      if (popup) popup.close()
      throw new Error('Google Meet was not returned by the backend.')
    }

    if (popup) {
      popup.location.href = meetingUrl
    } else {
      window.location.href = meetingUrl
    }

    emit('toast', 'Google Meet started')
  } catch (e) {
    if (popup) popup.close()
    console.error('[Tutor Schedule] Failed to start session:', e)
    message.value = e?.message || 'Unable to start the Google Meet.'
    emit('toast', message.value)
  } finally {
    startingSessionId.value = null
  }
}


async function add() {

  message.value = ''


  // Validate subject
  if (!form.subject_id) {
    message.value = 'Please choose a subject.'
    return
  }


  // Validate date
  if (!form.session_date) {
    message.value = 'Please choose a date.'
    return
  }


  // Validate times
  if (!form.start_time || !form.end_time) {
    message.value = 'Please choose start and end times.'
    return
  }


  // End must be after start
  if (form.end_time <= form.start_time) {
    message.value = 'End time must be after start time.'
    return
  }


  loading.value = true


  try {

    /*
     * Send REAL data to the existing backend.
     *
     * Convert subject_id to a number because
     * SQLAlchemy expects the actual Subject ID.
     */
    const payload = {
      subject_id: Number(form.subject_id),
      session_date: form.session_date,
      start_time: form.start_time,
      end_time: form.end_time,
      session_type: form.session_type
    }


    const result = await tutorApi.addClass(payload)

    message.value =
      result?.message ||
      'Session created successfully.'

    emit(
      'toast',
      result?.data?.meeting_url || result?.meeting_url
        ? 'Session created with Google Meet'
        : 'Session added to real schedule'
    )


    /*
     * Reload so the newly created database
     * session is fetched and displayed.
     */
    window.location.reload()

  } catch (e) {

    console.error(
      '[Tutor Schedule] Failed to create session:',
      e
    )


    message.value =
      e?.message ||
      'Unable to create session. Please try again.'

  } finally {

    loading.value = false

  }

}
</script>