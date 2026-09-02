<template>
  <section class="view on">

    <!-- =========================================================
         Schedule Form
    ========================================================== -->

    <div class="card glass reveal">

      <div class="ch">
        <h3>{{ editingSessionId ? 'Edit regular session' : 'Schedule a regular session' }}</h3>
      </div>

      <div
        class="grid"
        style="
          grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
          gap:10px;
          margin-bottom:18px
        "
      >

        <!-- Subject -->
        <div>
          <label class="lab">Subject</label>

          <select
            v-model="form.subject_id"
            class="field"
            :disabled="!subjectOptions.length"
          >
            <option value="">
              {{
                subjectOptions.length
                  ? 'Choose'
                  : 'No subject assigned'
              }}
            </option>

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

        <div>
          <label class="lab">Meeting Link</label>

          <input
            v-model="form.meeting_link"
            type="url"
            class="field"
            placeholder="https://meet.google.com/xxxxx"
          >
        </div>

      </div>

      <div class="flex flex-wrap items-center gap-2">
        <button
          class="btn grad"
          @click="editingSessionId ? saveEdit() : add()"
          :disabled="loading || !subjectOptions.length"
        >
          {{ loading ? 'Saving...' : (editingSessionId ? 'Save Changes' : 'Add Regular Session') }}
        </button>
        <button v-if="editingSessionId" type="button" class="btn sm" @click="cancelEdit">Cancel Edit</button>
      </div>

      <p
        v-if="message"
        class="eyebrow"
        style="margin-top:10px"
      >
        {{ message }}
      </p>

    </div>


    <!-- =========================================================
         Existing Sessions
    ========================================================== -->

    <div
      class="card glass reveal"
      style="margin-top:18px"
    >

      <div class="ch">
        <h3>Class History & Schedule</h3>
      </div>

      <div
        v-if="!displaySessions.length"
        class="eyebrow"
      >
        No sessions yet.
      </div>


      <div
        v-for="s in displaySessions"
        :key="s.id"
        class="row"
      >

        <!-- Session information -->
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

          <!--
            REASON

            Only rendered when the meeting actually has one.
            Regular tutor-created classes without a MeetingRequest
            have no reason, so this line is simply omitted for them
            rather than showing a fake placeholder.
          -->
          <p
            v-if="s.meeting_reason"
            class="mt-1 truncate text-xs text-slate-500"
          >
            Reason: {{ s.meeting_reason }}
          </p>


          <!-- ===================================================
               Meeting link
          ==================================================== -->

          <div
            v-if="s.meeting_url || s.meetingUrl"
            class="meeting-link-box"
          >
            <span class="meeting-icon">
              🎥
            </span>

            <div class="meeting-info">

              <!--
                ALWAYS show the actual meeting type.
              -->
              <div
                class="meeting-type-badge"
                :class="{
                  'one-to-one': s.meeting_type === 'ONE_TO_ONE',
                  'regular': s.meeting_type === 'REGULAR',
                  'unknown': !s.meeting_type
                }"
              >
                {{ s.meeting_type_label }}
              </div>

              <!--
                Regular class:
                  Students

                Student ONE-TO-ONE:
                  Student

                Parent-created/requested ONE-TO-ONE:
                  Parent + Student

                Parent-only ONE-TO-ONE:
                  Parent

                Unknown:
                  Not Set
              -->
              <div class="meeting-participants">
                <span class="meeting-with-label">With:</span>
                <strong>{{ s.meeting_participant_label }}</strong>
              </div>

              <div class="meeting-status">
                Google Meet ready
              </div>

            </div>

            <button
              type="button"
              class="meeting-copy"
              @click="copyMeetingLink(s)"
            >
              Copy Link
            </button>
          </div>

        </div>


        <!-- ===================================================
             Session actions
        ==================================================== -->

        <div class="session-actions">

          <span class="badge">
            {{ s.badge }}
          </span>

          <!-- =================================================
               JOIN MEETING

               IMPORTANT:
               Once a meeting URL exists, it remains available
               even after moving between Tutor panels.
          ================================================== -->

          <a
            v-if="s.can_join && s.meeting_request_status !== 'Pending Approval'"
            :href="
              s.meeting_url ||
              s.meetingUrl
            "
            target="_blank"
            rel="noopener noreferrer"
            class="btn grad sm inline-flex items-center justify-center gap-2"
          >
            Join Meeting
          </a>


          <!-- =================================================
               START MEETING

               Only show if there is no meeting URL and the
               session has not been completed/cancelled.
          ================================================== -->

          <button
            v-if="s.can_start && !s.can_join && s.badge !== 'Meeting Ended' && s.badge !== 'Completed' && s.badge !== 'Done'"
            type="button"
            class="btn grad sm inline-flex items-center justify-center gap-2"
            :disabled="startingSessionId === s.id"
            @click="startMeeting(s)"
          >
            <span v-if="startingSessionId === s.id">
              Starting...
            </span>

            <span v-else>
              Start Meeting
            </span>
          </button>


          <!-- =================================================
               END MEETING

               A meeting is considered active when:
               - meeting URL exists
               - session is Live
          ================================================== -->

          <button
            v-if="s.can_end"
            type="button"
            class="btn end-btn sm inline-flex items-center justify-center gap-2"
            :disabled="endingSessionId === s.id"
            @click="endMeeting(s)"
          >
            <span v-if="endingSessionId === s.id">
              Ending...
            </span>

            <span v-else>
              End Meeting
            </span>
          </button>

          <button type="button" class="btn sm" @click="openDetails(s)">Details</button>

          <button
            v-if="s.badge === 'Meeting Not Started'"
            type="button"
            class="btn sm"
            @click="beginEdit(s)"
          >Edit</button>

          <button
            v-if="s.status !== 'Live' && !['Meeting Ended', 'Completed', 'Done'].includes(s.badge)"
            type="button"
            class="btn sm cancel-session-btn"
            @click="deleteSession(s)"
          >Delete</button>

        </div>

      </div>

    </div>

    <div v-if="detailsSession" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 p-4" @click.self="detailsSession = null">
      <div class="w-full max-w-5xl rounded-2xl bg-white dark:bg-slate-900 p-6 shadow-2xl">
        <div class="flex items-center justify-between gap-4 mb-5">
          <div><h3 class="text-lg font-bold">Session Details</h3><p class="text-xs text-slate-500">{{ detailsSession.subject }} · {{ detailsSession.date }} · {{ detailsSession.time }}–{{ detailsSession.endTime }}</p></div>
          <button class="btn sm" @click="detailsSession = null">Close</button>
        </div>
        <div v-if="detailsLoading" class="py-8 text-center text-sm text-slate-500">Loading details...</div>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-left text-sm"><thead><tr class="border-b"><th class="p-3">Student</th><th class="p-3">Attendance</th><th class="p-3">Learning Pace</th><th class="p-3">Observation</th></tr></thead><tbody><tr v-for="r in detailsRecords" :key="r.student_id" class="border-b last:border-0"><td class="p-3 font-semibold">{{ r.student_name }}</td><td class="p-3"><select v-model="r.attendance_status" class="field"><option :value="null">Not recorded</option><option>Present</option><option>Absent</option><option>Late</option><option>Pending</option></select></td><td class="p-3"><select v-model="r.learning_pace" class="field"><option :value="null">Not set</option><option>Fast</option><option>Average</option><option>Needs Practice</option></select></td><td class="p-3"><input v-model="r.observation" class="field" placeholder="No tutor observation recorded" /></td></tr></tbody></table>
          <div class="mt-5 flex justify-end gap-2"><button class="btn sm" @click="detailsSession = null">Cancel</button><button class="btn grad" @click="saveDetails">Save Session Details</button></div>
        </div>
      </div>
    </div>
  </section>
</template>


<script setup>

import {
  computed,
  reactive,
  ref
} from 'vue'

import { tutorApi } from '../../services/tutorApi'


/* ============================================================
   PROPS
============================================================ */

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

  subjects: {
    type: Array,
    default: () => []
  },

})


/* ============================================================
   EVENTS
============================================================ */

const emit = defineEmits([
  'toast',
  'session-updated'
])


/* ============================================================
   FORM
============================================================ */

const form = reactive({

  subject_id: '',

  session_date: '',

  start_time: '16:00',

  end_time: '17:00',

  session_type: 'Regular',

  meeting_link: ''

})


/* ============================================================
   STATE
============================================================ */

const message = ref('')

const loading = ref(false)

const startingSessionId = ref(null)

const endingSessionId = ref(null)
const editingSessionId = ref(null)
const detailsSession = ref(null)
const detailsRecords = ref([])
const detailsLoading = ref(false)


/* ============================================================
   SUBJECT OPTIONS
============================================================ */

const subjectOptions = computed(() => {

  if (
    !Array.isArray(props.subjects)
  ) {
    return []
  }

  return props.subjects

})


/* ============================================================
   NORMALISE SESSION
============================================================ */

function normaliseSession(s) {
  if (!s) return null

  const meetingUrl = s.meeting_url || s.meetingUrl || ''

  const badge =
    s.meeting_lifecycle ||
    s.badge ||
    s.status ||
    'Meeting Not Started'

  /*
   * ============================================================
   * MEETING TYPE — NO SILENT REGULAR FALLBACK
   * ============================================================
   *
   * The UI must never turn an explicitly One-to-One session
   * into "Regular Class".
   *
   * We check every field that can explicitly describe the
   * session/meeting type.
   *
   * Priority:
   *   1. Explicit ONE_TO_ONE anywhere
   *   2. Explicit REGULAR
   *   3. If neither exists, show "Meeting Type Not Set"
   *
   * This is intentionally NOT:
   *
   *   "anything unknown = REGULAR"
   *
   * because that was causing the bug where a One-to-One
   * session was displayed as a Regular Class.
   */
  const typeCandidates = [
    s.meeting_type,
    s.meetingType,
    s.session_type,
    s.sessionType,
    s.classLevel,
    s.class_level,
    s.type
  ]
    .filter(value => value !== undefined && value !== null)
    .map(value => String(value).trim().toUpperCase())

  const hasOneToOneType = typeCandidates.some(value =>
    [
      'ONE_TO_ONE',
      'ONE-TO-ONE',
      'ONE TO ONE',
      'ONE TO ONE MEETING',
      'ONE-ON-ONE',
      'ONE ON ONE',
      'ONE2ONE'
    ].includes(value)
  )

  const hasRegularType = typeCandidates.some(value =>
    [
      'REGULAR',
      'REGULAR CLASS',
      'REGULAR_SESSION',
      'REGULAR SESSION'
    ].includes(value)
  )

  let meetingType = null

  if (hasOneToOneType) {
    meetingType = 'ONE_TO_ONE'
  } else if (hasRegularType) {
    meetingType = 'REGULAR'
  }

  /*
   * ============================================================
   * WHO CREATED / REQUESTED THE ONE-TO-ONE?
   * ============================================================
   */
  const creatorRole = String(
    s.created_by_role ||
    s.createdByRole ||
    s.creator_role ||
    s.creatorRole ||
    ''
  ).trim().toUpperCase()

  const requesterRole = String(
    s.requested_by_role ||
    s.requestedByRole ||
    s.requester_role ||
    s.requesterRole ||
    s.meeting_requested_by_role ||
    s.meetingRequestedByRole ||
    ''
  ).trim().toUpperCase()

  /*
   * ============================================================
   * PARTICIPANTS
   * ============================================================
   *
   * ONE-TO-ONE:
   *
   *   Parent-created/requested  -> Parent + Student
   *   Student-created/requested -> Student
   *   Tutor/Teacher-created     -> Student
   *
   * REGULAR:
   *
   *   -> Students
   *
   * Unknown:
   *
   *   -> Not set
   *
   * Explicit backend participant type always wins.
   */
  const explicitParticipantType = String(
    s.meeting_participant_type ||
    s.meetingParticipantType ||
    s.participant_type ||
    s.participantType ||
    ''
  ).trim().toUpperCase()

  let participantType = ''

  if (explicitParticipantType) {
    if (
      explicitParticipantType === 'PARENT+STUDENT' ||
      explicitParticipantType === 'PARENT_AND_STUDENT' ||
      explicitParticipantType === 'PARENT_STUDENT'
    ) {
      participantType = 'PARENT_STUDENT'
    } else if (
      explicitParticipantType === 'PARENT_ONLY' ||
      explicitParticipantType === 'PARENT'
    ) {
      participantType = 'PARENT'
    } else if (
      explicitParticipantType === 'STUDENT' ||
      explicitParticipantType === 'STUDENT_ONLY'
    ) {
      participantType = 'STUDENT'
    }
  }

  if (!participantType && meetingType === 'ONE_TO_ONE') {
    /*
     * ONE-TO-ONE participant rules:
     *
     * Parent-created/requested -> Parent + Student
     * Student-created/requested -> Student
     * Tutor/Teacher-created -> Student
     *
     * A parent-created ONE-TO-ONE is a meeting between the parent
     * and the student, so it must display "Parent + Student".
     */
    if (
      requesterRole === 'PARENT' ||
      creatorRole === 'PARENT'
    ) {
      participantType = 'PARENT_STUDENT'
    } else {
      participantType = 'STUDENT'
    }
  }

  if (!participantType && meetingType === 'REGULAR') {
    participantType = 'STUDENTS'
  }

  /*
   * ============================================================
   * DISPLAY LABELS
   * ============================================================
   */
  let meetingTypeLabel = 'Meeting Type Not Set'
  let meetingParticipantLabel = 'Not Set'

  if (meetingType === 'ONE_TO_ONE') {
    meetingTypeLabel = 'ONE-TO-ONE'

    if (participantType === 'PARENT_STUDENT') {
      meetingParticipantLabel = 'Parent + Student'
    } else if (participantType === 'PARENT') {
      meetingParticipantLabel = 'Parent'
    } else {
      meetingParticipantLabel = 'Student'
    }
  } else if (meetingType === 'REGULAR') {
    meetingTypeLabel = 'Regular Class'
    meetingParticipantLabel = 'Students'
  }

  return {
    ...s,

    id: s.id ?? s.session_id,

    meeting_url: meetingUrl,
    meetingUrl: meetingUrl,

    badge,

    /*
     * Resolved UI values.
     *
     * meeting_type remains null when the backend has not told us
     * whether this is Regular or One-to-One. It is NOT silently
     * changed to Regular.
     */
    meeting_type: meetingType,
    meeting_participant_type: participantType,

    meeting_type_label: meetingTypeLabel,
    meeting_participant_label: meetingParticipantLabel,

    meeting_creator_role: creatorRole,
    meeting_requester_role: requesterRole,

    can_join: Boolean(s.can_join),

    can_start:
      s.can_start !== false &&
      badge !== 'Meeting Ended' &&
      badge !== 'Done' &&
      badge !== 'Completed',

    can_end: Boolean(s.can_end),
  }
}


/* ============================================================
   DISPLAY SESSIONS

   IMPORTANT:
   There is NO local ref containing a copy of the sessions.

   The parent TutorLayout owns sessionsState.

   Therefore changing:
      Schedule -> Attendance -> Materials -> Schedule

   does not lose the meeting state.
============================================================ */

const displaySessions = computed(() => {

  return (
    props.sessions || []
  )
    .map(normaliseSession)
    .filter(Boolean)
    .sort((a, b) => {
      const aKey = `${a.date || ''} ${a.start_time || a.time || ''}`
      const bKey = `${b.date || ''} ${b.start_time || b.time || ''}`
      return aKey.localeCompare(bKey)
    })

})


/* ============================================================
   UPDATE PARENT SESSION
============================================================ */

function notifySessionUpdate(session) {

  if (!session) {
    return
  }

  emit(
    'session-updated',
    session
  )

}


function beginEdit(s) {
  editingSessionId.value = s.id
  form.subject_id = String(s.subjectId ?? s.subject_id ?? '')
  form.session_date = s.date || ''
  form.start_time = s.start_time || ''
  form.end_time = s.end_time || ''
  form.session_type = 'Regular'
  form.meeting_link = s.meeting_url || s.meetingUrl || ''
  message.value = 'Edit the schedule, then save changes.'
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelEdit() {
  editingSessionId.value = null
  form.subject_id = ''
  form.session_date = ''
  form.start_time = '16:00'
  form.end_time = '17:00'
  form.session_type = 'Regular'
  form.meeting_link = ''
  message.value = ''
}

async function saveEdit() {
  if (!editingSessionId.value) return
  loading.value = true
  try {
    const result = await tutorApi.updateClass(editingSessionId.value, {
      subject_id: Number(form.subject_id),
      session_date: form.session_date,
      start_time: form.start_time,
      end_time: form.end_time,
      session_type: 'Regular',
      meeting_link: form.meeting_link
    })
    const updated = result?.session || result?.data?.session || result?.data || null
    if (updated) notifySessionUpdate(updated)
    emit('toast', 'Session updated · students and parents notified')
    cancelEdit()
  } catch (error) {
    message.value = error?.message || 'Unable to update session.'
    emit('toast', message.value)
  } finally {
    loading.value = false
  }
}

async function deleteSession(s) {
  if (!window.confirm(`Delete the ${s.subject} session on ${s.date}?`)) return
  try {
    await tutorApi.deleteClass(s.id)
    emit('session-updated', { id: s.id, session_id: s.id, status: 'Cancelled', removed: true, badge: 'Meeting Ended', meeting_lifecycle: 'Meeting Ended', meeting_url: null })
    emit('toast', 'Session cancelled and removed from the active schedule')
  } catch (error) {
    emit('toast', error?.message || 'Unable to delete session.')
  }
}


async function openDetails(s) {
  detailsSession.value = s
  detailsLoading.value = true
  try {
    const r = await tutorApi.getSessionDetails(s.id)
    detailsRecords.value = r?.records || r?.data?.records || []
  } catch (e) {
    emit('toast', e?.message || 'Unable to load session details.')
  } finally { detailsLoading.value = false }
}

async function saveDetails() {
  if (!detailsSession.value) return
  try {
    await tutorApi.saveSessionDetails(detailsSession.value.id, detailsRecords.value.map(r => ({ student_id: r.student_id, attendance_status: r.attendance_status || null, learning_pace: r.learning_pace || null, observation: r.observation || '' })))
    emit('toast', 'Session details saved · parent and student records updated')
    detailsSession.value = null
  } catch (e) { emit('toast', e?.message || 'Unable to save session details.') }
}

async function decideRequest(s, decision) {
  if (!s.meeting_id) return
  let payload = { decision }
  if (decision === 'deny') {
    const reason = window.prompt('Reason for denying this meeting request:')
    if (reason === null) return
    payload.reason = reason
  } else if (decision === 'change') {
    const proposedDate = window.prompt('Preferred date (YYYY-MM-DD):')
    if (proposedDate === null) return
    const proposedStart = window.prompt('Preferred start time (HH:MM):')
    if (proposedStart === null) return
    const proposedEnd = window.prompt('Preferred end time (HH:MM):')
    if (proposedEnd === null) return
    const reason = window.prompt('Reason / message for the parent:')
    if (reason === null) return
    payload.session_date = proposedDate
    payload.start_time = proposedStart
    payload.end_time = proposedEnd
    payload.reason = reason
  }
  try {
    await tutorApi.decideMeeting(s.meeting_id, payload)
    emit('toast', decision === 'approve' ? 'Meeting approved and parent/student notified' : decision === 'deny' ? 'Meeting denied and parent notified' : 'Change request sent to parent')
    emit('session-updated', { id: s.id, meeting_request_status: decision === 'approve' ? 'Scheduled' : decision === 'deny' ? 'Denied' : 'Reschedule Requested', status: decision === 'deny' ? 'Cancelled' : s.status })
  } catch (e) { emit('toast', e?.message || 'Unable to update meeting request.') }
}

/* ============================================================
   START MEETING
============================================================ */

async function startMeeting(s) {

  if (!s?.id) {
    return
  }

  startingSessionId.value = s.id

  message.value = ''


  /*
   * Open the tab BEFORE the API request.

   * This prevents browser popup blocking.
   */

  const popup =
    window.open(
      'about:blank',
      '_blank'
    )


  try {

    const response =
      await tutorApi.startClass(
        s.id
      )


    /*
     * Support all common response shapes.
     */

    const data =
      response?.data ||
      response ||
      {}


    const url =
      data.meeting_url ||
      data.meetingUrl ||
      data.session?.meeting_url ||
      data.session?.meetingUrl ||
      ''


    if (!url) {

      if (popup) {
        popup.close()
      }

      throw new Error(
        'Meeting started, but the backend did not return a Google Meet link.'
      )

    }


    /*
     * Build the persistent session state.

     * This object is emitted to TutorLayout.
     */

    const updatedSession = {

      ...s,

      id:
        s.id ??
        s.session_id,

      meeting_url:
        url,

      meetingUrl:
        url,

      badge:
        'Meeting Started',

      meeting_lifecycle:
        'Meeting Started',

      can_join:
        true,

      can_start:
        false,

      can_end:
        true,

      meeting_started_at:
        data.meeting_started_at ||
        data.meetingStartedAt ||
        new Date().toISOString(),

      meeting_ended_at:
        null

    }


    /*
     * IMPORTANT:
     * Tell TutorLayout about the change.

     * TutorLayout survives route changes.
     */

    notifySessionUpdate(
      updatedSession
    )


    /*
     * Open Google Meet.
     */

    if (popup) {

      popup.location.href = url

    } else {

      message.value =
        'Meeting started. Your browser blocked the new tab. Use Join Meeting to open it.'

    }


    emit(
      'toast',
      'Meeting started · students notified'
    )

  }

  catch (error) {

    console.error(
      '[Tutor Schedule] Start meeting error:',
      error
    )


    message.value =
      error?.message ||
      'Unable to start the meeting.'


    emit(
      'toast',
      message.value
    )

  }

  finally {

    startingSessionId.value = null

  }

}


/* ============================================================
   END MEETING
============================================================ */

async function endMeeting(s) {

  if (!s?.id) {
    return
  }

  endingSessionId.value = s.id

  message.value = ''


  try {

    const response =
      await tutorApi.endClass(
        s.id
      )


    const data =
      response?.data ||
      response ||
      {}


    const durationSeconds =
      Number(
        data.duration_seconds ||
        data.durationSeconds ||
        data.session?.duration_seconds ||
        0
      )


    const durationMinutes =
      Math.floor(
        durationSeconds / 60
      )


    /*
     * Keep the session in the parent's state.

     * Do NOT reload the browser.
     */

    const updatedSession = {

      ...s,

      badge:
        'Meeting Ended',

      meeting_lifecycle:
        'Meeting Ended',

      can_join:
        false,

      can_start:
        false,

      can_end:
        false,

      status:
        'Completed',

      meeting_ended_at:
        data.meeting_ended_at ||
        data.meetingEndedAt ||
        new Date().toISOString(),

      meeting_duration_seconds:
        durationSeconds

    }


    notifySessionUpdate(
      updatedSession
    )


    emit(
      'toast',
      `Meeting ended · ${durationMinutes} min recorded`
    )

  }

  catch (error) {

    console.error(
      '[Tutor Schedule] End meeting error:',
      error
    )


    message.value =
      error?.message ||
      'Unable to end the meeting.'


    emit(
      'toast',
      message.value
    )

  }

  finally {

    endingSessionId.value = null

  }

}


/* ============================================================
   COPY MEETING LINK
============================================================ */

async function copyMeetingLink(s) {

  const url =
    s?.meeting_url ||
    s?.meetingUrl


  if (!url) {
    return
  }


  try {

    await navigator.clipboard.writeText(
      url
    )

    emit(
      'toast',
      'Google Meet link copied'
    )

  }

  catch (error) {

    console.error(
      '[Tutor Schedule] Copy failed:',
      error
    )

    message.value =
      'Unable to copy the meeting link.'

  }

}


/* ============================================================
   ADD SESSION
============================================================ */

async function add() {

  message.value = ''


  if (!form.subject_id) {

    message.value =
      subjectOptions.value.length
        ? 'Please choose a subject.'
        : 'No subject is assigned to your tutor profile.'

    return

  }


  if (!form.session_date) {

    message.value =
      'Please choose a date.'

    return

  }

  if (
    !form.start_time ||
    !form.end_time
  ) {

    message.value =
      'Please choose start and end times.'

    return

  }


  if (
    form.end_time <=
    form.start_time
  ) {

    message.value =
      'End time must be after start time.'

    return

  }


  loading.value = true


  try {

    const payload = {

      subject_id:
        Number(
          form.subject_id
        ),

      session_date:
        form.session_date,

      start_time:
        form.start_time,

      end_time:
        form.end_time,

      session_type:
        'Regular',

      meeting_link:
        form.meeting_link

    }


    const result =
      await tutorApi.addClass(
        payload
      )


    /*
     * Do NOT do:
     *
     * window.location.reload()
     *
     * That was one of the things causing the page to
     * completely reload.
     */


    const created =
      result?.session ||
      result?.data?.session ||
      result?.data ||
      null


    if (created) {

      emit(
        'session-updated',
        created
      )

    }


    message.value =
      result?.message ||
      result?.data?.message ||
      'Session created successfully.'


    emit(
      'toast',
      'Session added to real schedule'
    )


    /*
     * Reset only the form.
     */

    form.subject_id = ''
    form.meeting_link = ''

  }

  catch (error) {

    console.error(
      '[Tutor Schedule] Failed to create session:',
      error
    )


    message.value =
      error?.message ||
      'Unable to create session. Please try again.'

  }

  finally {

    loading.value = false

  }

}

</script>


<style scoped>

.session-actions {

  display: flex;

  align-items: center;

  justify-content: flex-end;

  gap: 8px;

  flex-wrap: wrap;

}


.meeting-link-box {

  display: flex;

  flex-direction: row;

  flex-wrap: wrap;

  align-items: center;

  gap: 10px;

  margin-top: 7px;

  padding: 7px 10px;

  border-radius: 9px;

  background: rgba(59, 130, 246, 0.07);

  border: 1px solid rgba(59, 130, 246, 0.12);

  width: fit-content;

  max-width: 100%;

  overflow-x: auto;

}



.meeting-icon {

  font-size: 13px;

}


.meeting-text {

  font-size: 11px;

  font-weight: 600;

  color: #2563eb;

}


.meeting-copy {

  border: 0;

  background: transparent;

  color: #2563eb;

  font-size: 11px;

  font-weight: 700;

  cursor: pointer;

  padding: 0;

}


.meeting-copy:hover {

  text-decoration: underline;

}


.end-btn {

  background: #fff1f2 !important;

  color: #e11d48 !important;

  border: 1px solid #fecdd3 !important;

}


.end-btn:hover {

  background: #ffe4e6 !important;

}


.meeting-info {

  display: flex;

  flex-direction: row;

  flex-wrap: wrap;

  align-items: center;

  justify-content: flex-start;

  gap: 10px;

  min-width: 0;

  flex: 1;

  white-space: nowrap;

}



.meeting-type-badge {
  display: inline-flex;
  width: fit-content;
  max-width: 100%;
  align-items: center;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 10px;
  line-height: 1.2;
  font-weight: 800;
  letter-spacing: 0.04em;
  white-space: nowrap;
}

.meeting-type-badge.regular {
  background: rgba(59, 130, 246, 0.10);
  color: #2563eb;
}

.meeting-type-badge.unknown {
  background: rgba(100, 116, 139, 0.10);
  color: #64748b;
}

.meeting-type-badge.one-to-one {
  background: rgba(124, 58, 237, 0.10);
  color: #7c3aed;
}

.meeting-participants {

  display: flex;

  flex-direction: row;

  align-items: center;

  gap: 4px;

  font-size: 11px;

  line-height: 1.3;

  color: #475569;

  white-space: nowrap;

  flex-shrink: 0;

}



.meeting-with-label {
  color: #64748b;
}

.meeting-participants strong {
  font-weight: 800;
  color: #334155;
}

.meeting-status {
  font-size: 10px;
  line-height: 1.2;
  color: #64748b;
}

.row {

  display: flex;

  flex-direction: row;

  align-items: center;

  justify-content: space-between;

  gap: 18px;

}



.g1 {

  flex: 1;

  min-width: 0;

}



.session-actions {

  display: flex;

  flex-direction: row;

  align-items: center;

  justify-content: flex-end;

  gap: 8px;

  flex-wrap: wrap;

  flex-shrink: 0;

}



@media (max-width: 640px) {

  .session-actions {

    justify-content: flex-start;

  }

  .meeting-link-box {

    max-width: 100%;

  }

  .meeting-info {

    flex-wrap: wrap;

  }

}

.cancel-session-btn { background: #fff1f2 !important; color: #e11d48 !important; border: 1px solid #fecdd3 !important; }
.cancel-session-btn:hover { background: #ffe4e6 !important; }
</style>

