<template>
  <section class="view on">

    <!-- =========================================================
         CONNECT WITH PARENT / STUDENT
    ========================================================== -->

    <div class="card glass reveal">

      <div class="ch">
        <div>
          <h3>Connect with Parents / Students</h3>

          <p
            class="eyebrow"
            style="margin-top:6px"
          >
            Send a message or schedule a one-to-one meeting with the correct person.
          </p>
        </div>
      </div>


      <div class="connect-grid">

        <!-- =====================================================
             STUDENT
        ====================================================== -->

        <div class="connect-card student-card">

          <div class="connect-card-head">

            <div class="connect-icon student-icon">
              🎓
            </div>

            <div>
              <h4>Connect with a Student</h4>

              <p>
                Send a direct message or schedule a one-to-one session
                with one of your students.
              </p>
            </div>

          </div>


          <div class="field-stack">

            <!-- Student -->

            <div>

              <label class="lab">
                Student
              </label>

              <select
                v-model="studentTargetId"
                class="field"
              >

                <option value="">
                  Choose student
                </option>

                <option
                  v-for="student in studentOptions"
                  :key="student.studentId"
                  :value="String(student.studentId)"
                >
                  {{ student.name }}
                </option>

              </select>

            </div>


            <!-- Message -->

            <div>

              <label class="lab">
                Message
              </label>

              <textarea
                v-model="studentMessage"
                class="field message-box"
                rows="3"
                placeholder="Write a message to the student..."
              />

            </div>


            <div class="action-row">

              <button
                type="button"
                class="btn message-btn"
                :disabled="
                  studentMessageLoading ||
                  !studentTargetId ||
                  !studentMessage.trim()
                "
                @click="sendDirectMessage('student')"
              >

                {{
                  studentMessageLoading
                    ? 'Sending...'
                    : '💬 Send Message'
                }}

              </button>


              <button
                type="button"
                class="btn grad"
                :disabled="meetingLoading === 'student'"
                @click="
                  showStudentMeetingForm =
                    !showStudentMeetingForm
                "
              >

                {{
                  showStudentMeetingForm
                    ? 'Hide Meeting'
                    : '📅 Schedule Meeting'
                }}

              </button>

            </div>


            <!-- Student Meeting -->

            <div
              v-if="showStudentMeetingForm"
              class="meeting-form"
            >

              <div>

                <label class="lab">
                  Meeting date & time
                </label>

                <input
                  v-model="studentMeeting.meeting_date"
                  type="datetime-local"
                  class="field"
                >

              </div>


              <div>

                <label class="lab">
                  Reason / purpose
                </label>

                <input
                  v-model="studentMeeting.meeting_reason"
                  class="field"
                  placeholder="Progress review, doubt discussion..."
                >

              </div>


              <div>

                <label class="lab">
                  Meeting link (optional)
                </label>

                <input
                  v-model="studentMeeting.meeting_link"
                  class="field"
                  placeholder="Leave blank to auto-generate a Google Meet link"
                >

              </div>


              <button
                type="button"
                class="btn grad connect-button"
                :disabled="
                  meetingLoading === 'student' ||
                  !studentTargetId ||
                  !studentMeeting.meeting_date
                "
                @click="scheduleMeeting('student')"
              >

                {{
                  meetingLoading === 'student'
                    ? 'Scheduling...'
                    : '📅 Create Student Meeting'
                }}

              </button>

            </div>

          </div>

        </div>


        <!-- =====================================================
             PARENT
        ====================================================== -->

        <div class="connect-card parent-card">

          <div class="connect-card-head">

            <div class="connect-icon parent-icon">
              👨‍👩‍👧
            </div>

            <div>

              <h4>
                Connect with a Parent
              </h4>

              <p>
                Send a direct message or schedule a meeting
                with a student's parent.
              </p>

            </div>

          </div>


          <div class="field-stack">

            <!-- Parent -->

            <div>

              <label class="lab">
                Parent
              </label>

              <select
                v-model="parentTargetId"
                class="field"
              >

                <option value="">
                  Choose parent
                </option>

                <option
                  v-for="parent in parentOptions"
                  :key="parent.parentId"
                  :value="String(parent.parentId)"
                >
                  {{ parent.name }}
                  {{
                    parent.studentName
                      ? ` · ${parent.studentName}`
                      : ''
                  }}
                </option>

              </select>


              <p
                v-if="!parentOptions.length"
                class="eyebrow"
                style="margin-top:7px"
              >
                No parent is currently linked to the students
                available to this tutor.
              </p>

            </div>


            <!-- Message -->

            <div>

              <label class="lab">
                Message
              </label>

              <textarea
                v-model="parentMessage"
                class="field message-box"
                rows="3"
                placeholder="Write a message to the parent..."
              />

            </div>


            <div class="action-row">

              <button
                type="button"
                class="btn message-btn"
                :disabled="
                  parentMessageLoading ||
                  !parentTargetId ||
                  !parentMessage.trim()
                "
                @click="sendDirectMessage('parent')"
              >

                {{
                  parentMessageLoading
                    ? 'Sending...'
                    : '💬 Send Message'
                }}

              </button>


              <button
                type="button"
                class="btn grad"
                :disabled="
                  meetingLoading === 'parent' ||
                  !parentTargetId
                "
                @click="
                  showParentMeetingForm =
                    !showParentMeetingForm
                "
              >

                {{
                  showParentMeetingForm
                    ? 'Hide Meeting'
                    : '📅 Schedule Meeting'
                }}

              </button>

            </div>


            <!-- Parent Meeting -->

            <div
              v-if="showParentMeetingForm"
              class="meeting-form"
            >

              <div>

                <label class="lab">
                  Meeting date & time
                </label>

                <input
                  v-model="parentMeeting.meeting_date"
                  type="datetime-local"
                  class="field"
                >

              </div>


              <div>

                <label class="lab">
                  Reason / purpose
                </label>

                <input
                  v-model="parentMeeting.meeting_reason"
                  class="field"
                  placeholder="Progress discussion, attendance query..."
                >

              </div>


              <div>

                <label class="lab">
                  Meeting link (optional)
                </label>

                <input
                  v-model="parentMeeting.meeting_link"
                  class="field"
                  placeholder="Leave blank to auto-generate a Google Meet link"
                >

              </div>


              <button
                type="button"
                class="btn grad connect-button"
                :disabled="
                  meetingLoading === 'parent' ||
                  !parentTargetId ||
                  !parentMeeting.meeting_date
                "
                @click="scheduleMeeting('parent')"
              >

                {{
                  meetingLoading === 'parent'
                    ? 'Scheduling...'
                    : '📅 Create Parent Meeting'
                }}

              </button>

            </div>

          </div>

        </div>

      </div>


      <!-- Status -->

      <p
        v-if="message"
        class="eyebrow status-message"
      >
        {{ message }}
      </p>

    </div>


    <!-- =========================================================
         PARENT MEETING REQUESTS
    ========================================================== -->

    <div
      class="card glass reveal request-card"
      style="margin-top:18px"
    >

      <div class="ch">

        <div>

          <h3>
            One-to-One Meeting Requests
          </h3>

          <p
            class="eyebrow"
            style="margin-top:6px"
          >
            Student/parent requests awaiting your approval appear here.
            Approve, request another time, or deny the request.
          </p>

        </div>


        <span class="request-count">
          {{ pendingRequests.length }} pending
        </span>

      </div>


      <!-- Empty -->

      <div
        v-if="!pendingRequests.length"
        class="empty-request"
      >

        <div class="empty-icon">
          ✓
        </div>

        <div>

          <strong>
            No pending meeting requests
          </strong>

          <p>
            New One-to-One requests will appear here.
          </p>

        </div>

      </div>


      <!-- Requests -->

      <div
        v-for="request in pendingRequests"
        :key="request.meeting_id"
        class="request-row"
      >

        <div class="request-main">

          <div class="request-title">
            {{ request.subject || 'Meeting Request' }}
          </div>


          <div class="request-meta">

            <span>
              👤 {{ request.creator_type === 'Student'
                ? (request.student_name || 'Student')
                : (request.parent_name || 'Parent') }}
            </span>

            <span v-if="request.creator_type === 'Parent' && request.student_name">
              🎓 {{ request.student_name }}
            </span>

            <span>
              📅 {{ request.date }}
            </span>

            <span>

              🕒
              {{ formatRequestTime(request.start_time) }}

              <template v-if="request.end_time">
                –
                {{ formatRequestTime(request.end_time) }}
              </template>

            </span>

          </div>


          <p
            v-if="request.reason"
            class="request-reason"
          >
            {{ request.reason }}
          </p>


          <span class="request-status">
            {{ request.display_status || request.status }}
          </span>

        </div>


        <div class="request-actions">

          <button
            type="button"
            class="btn grad sm"
            @click="decideRequest(request, 'approve')"
          >
            ✓ Approve
          </button>


          <button
            type="button"
            class="btn sm"
            @click="decideRequest(request, 'change')"
          >
            ↻ Request Change
          </button>


          <button
            type="button"
            class="btn sm danger-btn"
            @click="decideRequest(request, 'deny')"
          >
            ✕ Deny
          </button>

        </div>

      </div>

    </div>


    <!-- =========================================================
         EXISTING CONVERSATIONS
    ========================================================== -->

    <div
      class="card glass reveal"
      style="margin-top:18px"
    >

      <div class="ch">

        <div>

          <h3>
            Connect with Parents / Students
          </h3>

          <p
            class="eyebrow"
            style="margin-top:6px"
          >
            Messages and questions from parents and students
            appear here.
          </p>

        </div>

      </div>


      <div class="chat">

        <!-- Conversation list -->

        <div class="clist">

          <!-- Connect With selector -->

          <div class="connect-with">

            <label class="lab">
              Connect With
            </label>

            <div
              class="contact-type-toggle"
              role="tablist"
            >

              <button
                type="button"
                class="ct-pill"
                :class="{ on: contactFilter === 'all' }"
                @click="contactFilter = 'all'"
              >
                All
              </button>

              <button
                type="button"
                class="ct-pill student-pill"
                :class="{ on: contactFilter === 'student' }"
                @click="contactFilter = 'student'"
              >
                🎓 Students
              </button>

              <button
                type="button"
                class="ct-pill parent-pill"
                :class="{ on: contactFilter === 'parent' }"
                @click="contactFilter = 'parent'"
              >
                👨‍👩‍👧 Parents
              </button>

            </div>


            <input
              v-model="contactSearch"
              class="field search-field"
              placeholder="🔍 Search student or parent..."
            >

          </div>


          <TutorEmptyState
            v-if="!conversationList.length"
            title="No messages"
          />

          <div
            v-else-if="!filteredStudentConversations.length && !filteredParentConversations.length"
            class="clist-no-results"
          >
            No matches for "{{ contactSearch }}"
          </div>


          <!-- Students group -->

          <div
            v-if="filteredStudentConversations.length"
            class="clist-group"
          >

            <div class="clist-group-label student-label">
              👨‍🎓 STUDENTS
            </div>

            <button
              v-for="c in filteredStudentConversations"
              :key="c.id"
              class="ci"
              :class="{
                on: activeConversationId === c.id
              }"
              @click="$emit('select-conversation', c.id)"
            >

              <div
                class="av student-av"
              >
                {{ c.initials }}
              </div>


              <div class="ci-body">

                <div class="t">
                  {{ c.participantName }}
                </div>

                <div class="s">
                  Student
                </div>

              </div>


              <span
                v-if="hasOpenDoubt(c.otherId)"
                class="new-doubt-badge"
                title="New doubt"
              >
                🔴 New doubt
              </span>

            </button>

          </div>


          <!-- Parents group -->

          <div
            v-if="filteredParentConversations.length"
            class="clist-group"
          >

            <div class="clist-group-label parent-label">
              👨‍👩‍👧 PARENTS
            </div>

            <button
              v-for="c in filteredParentConversations"
              :key="c.id"
              class="ci"
              :class="{
                on: activeConversationId === c.id
              }"
              @click="$emit('select-conversation', c.id)"
            >

              <div
                class="av parent-av"
              >
                {{ c.initials }}
              </div>


              <div class="ci-body">

                <div class="t">
                  {{ c.participantName }}
                </div>

                <div class="s">
                  Parent → {{ linkedStudentNames(c) }}
                </div>

              </div>

            </button>

          </div>

        </div>


        <!-- Active conversation -->

        <div
          v-if="activeConversation"
          class="thr"
        >

          <div class="conversation-heading">

            <div
              class="av heading-av"
              :class="
                activeConversation.otherType === 'Parent'
                  ? 'parent-av'
                  : 'student-av'
              "
            >
              {{ activeConversation.initials }}
            </div>

            <div>

              <strong>
                {{ activeConversation.participantName }}
              </strong>

              <span>
                {{
                  activeConversation.otherType === 'Parent'
                    ? `Parent of ${linkedStudentNames(activeConversation)}`
                    : activeConversation.subtitle
                }}
              </span>


              <div
                v-if="
                  activeConversation.otherType === 'Parent' &&
                  (activeConversation.linkedStudents || []).length
                "
                class="child-chips"
              >

                <span
                  v-for="child in activeConversation.linkedStudents"
                  :key="child.studentId"
                  class="child-chip"
                >
                  👤 {{ child.studentName }}
                </span>

              </div>


              <span
                v-else-if="
                  activeConversation.otherType === 'Student' &&
                  hasOpenDoubt(activeConversation.otherId)
                "
                class="new-doubt-badge heading-badge"
              >
                🔴 New doubt
              </span>

            </div>

          </div>


          <div class="msgs">

            <div
              v-for="m in activeConversation.messages"
              :key="m.messageId"
              class="bub"
              :class="m.w"
            >
              {{ m.message }}
            </div>

          </div>


          <div class="cin">

            <input
              v-model="draft"
              class="field"
              placeholder="Type a reply..."
              @keydown.enter="send"
            >


            <button
              type="button"
              class="btn grad"
              :disabled="conversationSending"
              @click="send"
            >
              {{
                conversationSending
                  ? 'Sending...'
                  : 'Send'
              }}
            </button>

          </div>

        </div>


        <!-- No active conversation -->

        <div
          v-else
          class="no-conversation"
        >

          <div class="empty-icon">
            💬
          </div>

          <strong>
            Select a parent or student conversation
          </strong>

          <p>
            Messages and questions from them will appear here.
          </p>

        </div>

      </div>

    </div>

  </section>
</template>


<script setup>

import {
  computed,
  onMounted,
  reactive,
  ref
} from 'vue'

import TutorEmptyState
  from '../../components/tutor/TutorEmptyState.vue'

import { tutorApi }
  from '../../services/tutorApi'


/* =========================================================
   PROPS
========================================================= */

const props = defineProps({

  conversations: {
    type: Object,
    required: true
  },

  activeConversationId: {
    type: String,
    required: true
  },

  students: {
    type: Array,
    default: () => []
  },

  doubts: {
    type: Array,
    default: () => []
  }

})


/* =========================================================
   EVENTS
========================================================= */

const emit = defineEmits([
  'select-conversation',
  'send-message',
  'toast'
])


/* =========================================================
   EXISTING CONVERSATION STATE
========================================================= */

const draft = ref('')

const message = ref('')

const conversationSending = ref(false)


/* =========================================================
   DIRECT MESSAGE STATE
========================================================= */

const studentTargetId = ref('')

const parentTargetId = ref('')

const studentMessage = ref('')

const parentMessage = ref('')

const studentMessageLoading = ref(false)

const parentMessageLoading = ref(false)


/* =========================================================
   MEETING STATE
========================================================= */

const meetingLoading = ref('')

const meetingRequests = ref([])

const showStudentMeetingForm = ref(false)

const showParentMeetingForm = ref(false)


const studentMeeting = reactive({

  meeting_date: '',

  meeting_reason: '',

  meeting_link: ''

})


const parentMeeting = reactive({

  meeting_date: '',

  meeting_reason: '',

  meeting_link: ''

})


/* =========================================================
   CONVERSATIONS
========================================================= */

const conversationList = computed(() =>
  Object.values(
    props.conversations || {}
  )
)


const activeConversation = computed(() =>
  props.conversations?.[
    props.activeConversationId
  ] || null
)


/* =========================================================
   CHATBOT-STYLE CONTACT SELECTOR
   Splits the existing conversation list into Student /
   Parent groups and makes it searchable, without changing
   any backend data. "linkedStudents" and "otherType" both
   already come from the existing conversations API.
========================================================= */

const contactFilter = ref('all')

const contactSearch = ref('')


function linkedStudentNames(conversation) {

  const linked =
    conversation?.linkedStudents || []

  if (!linked.length) {
    return 'Unlinked student'
  }

  return linked
    .map(child => child.studentName)
    .join(', ')

}


function matchesSearch(conversation) {

  const query =
    contactSearch.value.trim().toLowerCase()

  if (!query) {
    return true
  }

  const haystack =
    [
      conversation.participantName,
      ...(
        (conversation.linkedStudents || [])
          .map(child => child.studentName)
      )
    ]
      .join(' ')
      .toLowerCase()

  return haystack.includes(query)

}


const studentConversations = computed(() =>

  conversationList.value.filter(c =>
    c.otherType === 'Student'
  )

)


const parentConversations = computed(() =>

  conversationList.value.filter(c =>
    c.otherType === 'Parent'
  )

)


const filteredStudentConversations = computed(() => {

  if (contactFilter.value === 'parent') {
    return []
  }

  return studentConversations.value.filter(matchesSearch)

})


const filteredParentConversations = computed(() => {

  if (contactFilter.value === 'student') {
    return []
  }

  return parentConversations.value.filter(matchesSearch)

})


/* =========================================================
   NEW DOUBT INDICATOR
   Uses the existing /tutor/doubts data (status "Open")
   rather than inventing a new unread-message concept.
========================================================= */

const openDoubtStudentIds = computed(() => {

  const ids = new Set()

  for (const doubt of props.doubts || []) {

    if (doubt?.status === 'Open') {
      ids.add(String(doubt.studentId))
    }

  }

  return ids

})


function hasOpenDoubt(studentId) {

  return openDoubtStudentIds.value.has(
    String(studentId)
  )

}


/* =========================================================
   STUDENT OPTIONS
   Uses ONLY existing student data.
========================================================= */

const studentOptions = computed(() => {

  return (props.students || [])

    .filter(student =>
      student?.studentId != null ||
      student?.student_id != null
    )

    .map(student => ({

      studentId:
        student.studentId ??
        student.student_id,

      name:
        student.name ||
        student.studentName ||
        student.student_name ||
        'Student'

    }))

})


/* =========================================================
   PARENT OPTIONS
   Uses ONLY existing parent relationship.
========================================================= */

const parentOptions = computed(() => {

  const map = new Map()

  for (
    const student of props.students || []
  ) {

    const parentId =
      student?.parentId ??
      student?.parent_id ??
      student?.parent?.parentId ??
      student?.parent?.parent_id

    if (parentId == null) {
      continue
    }


    const parentName =
      student?.parentName ??
      student?.parent_name ??
      student?.parent?.name ??
      student?.parent?.parent_name ??
      'Parent'


    if (!map.has(String(parentId))) {

      map.set(
        String(parentId),
        {
          parentId,
          name: parentName,

          studentName:
            student?.name ||
            student?.studentName ||
            student?.student_name ||
            ''
        }
      )

    }

  }


  return Array.from(
    map.values()
  )

})


/* =========================================================
   PENDING REQUESTS
========================================================= */

const pendingRequests = computed(() => {

  return (
    meetingRequests.value || []
  )

    .filter(request =>
      [
        'Pending Approval',
        'Reschedule Requested'
      ].includes(request.status)
    )

    .sort((a, b) => {

      const aKey =
        `${a.date || ''} ${a.start_time || ''}`

      const bKey =
        `${b.date || ''} ${b.start_time || ''}`

      return aKey.localeCompare(bKey)

    })

})


/* =========================================================
   EXISTING CONVERSATION SEND
   ========================================================= */

async function send() {

  const text =
    draft.value.trim()


  if (
    !text ||
    !activeConversation.value ||
    conversationSending.value
  ) {
    return
  }


  const conversation =
    activeConversation.value


  /*
   * First use the existing TutorLayout conversation
   * handler exactly as before.
   */
  conversationSending.value = true

  try {

    emit(
      'send-message',
      props.activeConversationId,
      text
    )

    draft.value = ''

  } finally {

    conversationSending.value = false

  }

}


/* =========================================================
   DIRECT MESSAGE
   IMPORTANT FIX:
   Direct Student/Parent messages now call the existing
   tutor/messages/send API.

   NO new API is created.
========================================================= */

async function sendDirectMessage(type) {

  const isStudent =
    type === 'student'


  const targetId =
    isStudent
      ? studentTargetId.value
      : parentTargetId.value


  const text =
    isStudent
      ? studentMessage.value.trim()
      : parentMessage.value.trim()


  /* -------------------------------------------------------
     VALIDATION
  ------------------------------------------------------- */

  if (!targetId) {

    message.value =
      isStudent
        ? 'Please choose a student.'
        : 'Please choose a parent.'

    emit(
      'toast',
      message.value
    )

    return

  }


  if (!text) {

    message.value =
      'Please enter a message.'

    emit(
      'toast',
      message.value
    )

    return

  }


  const numericTargetId =
    Number(targetId)


  if (
    !Number.isFinite(
      numericTargetId
    )
  ) {

    message.value =
      'Invalid recipient selected.'

    emit(
      'toast',
      message.value
    )

    return

  }


  if (isStudent) {

    if (studentMessageLoading.value) {
      return
    }

    studentMessageLoading.value = true

  } else {

    if (parentMessageLoading.value) {
      return
    }

    parentMessageLoading.value = true

  }


  message.value = ''


  try {

    /* =====================================================
       THIS IS THE ACTUAL FIX

       Existing API:
       POST /tutor/messages/send

       Student:
       receiver_type = Student

       Parent:
       receiver_type = Parent
    ===================================================== */

    const response =
      await tutorApi.sendMessage({

        receiver_type:
          isStudent
            ? 'Student'
            : 'Parent',

        receiver_id:
          numericTargetId,

        message:
          text

      })


    /*
     * Only treat explicit failure as failure.
     * This keeps compatibility with the existing apiClient
     * response format.
     */

    if (
      response?.success === false ||
      response?.status === 'error'
    ) {

      throw new Error(
        response?.message ||
        (
          isStudent
            ? 'Message could not be sent to student.'
            : 'Message could not be sent to parent.'
        )
      )

    }


    /* -----------------------------------------------------
       SUCCESS
    ----------------------------------------------------- */

    if (isStudent) {

      studentMessage.value = ''

      message.value =
        'Message sent to student successfully.'

      emit(
        'toast',
        'Message sent to student successfully.'
      )

    } else {

      parentMessage.value = ''

      message.value =
        'Message sent to parent successfully.'

      emit(
        'toast',
        'Message sent to parent successfully.'
      )

    }


    /*
     * Notify TutorLayout so its existing conversation state
     * can refresh/update.
     *
     * We are NOT using this event as the actual API send.
     * The API call above has already sent the message.
     */

    emit(
      'send-message',
      `${isStudent ? 'student' : 'parent'}-${numericTargetId}`,
      text,
      true
    )


  } catch (error) {

    console.error(
      '[TutorMessages] Direct message failed:',
      error
    )


    message.value =
      error?.message ||
      (
        isStudent
          ? 'Message could not be sent to student.'
          : 'Message could not be sent to parent.'
      )


    emit(
      'toast',
      message.value
    )


  } finally {

    if (isStudent) {

      studentMessageLoading.value = false

    } else {

      parentMessageLoading.value = false

    }

  }

}


/* =========================================================
   FORMAT TIME
========================================================= */

function formatRequestTime(value) {

  if (!value) {
    return ''
  }


  const parts =
    String(value).split(':')


  const hour =
    Number(parts[0])


  if (!Number.isFinite(hour)) {
    return value
  }


  const minute =
    parts[1] || '00'


  const suffix =
    hour >= 12
      ? 'PM'
      : 'AM'


  const displayHour =
    hour % 12 || 12


  return `${displayHour}:${minute} ${suffix}`

}


/* =========================================================
   LOAD MEETING REQUESTS
========================================================= */

async function loadMeetingRequests() {

  try {

    const response =
      await tutorApi.getMeetingRequests()


    if (
      response?.success !== false
    ) {

      meetingRequests.value =
        response?.requests ||
        response?.data?.requests ||
        []

    } else {

      meetingRequests.value = []

    }

  } catch (error) {

    console.warn(
      '[Tutor Messages] Unable to load meeting requests:',
      error
    )

    meetingRequests.value = []

  }

}


/* =========================================================
   RESET MEETING FORM
========================================================= */

function resetMeetingForm(type) {

  if (type === 'student') {

    studentTargetId.value = ''

    studentMeeting.meeting_date = ''

    studentMeeting.meeting_reason = ''

    studentMeeting.meeting_link = ''

    showStudentMeetingForm.value = false

  } else {

    parentTargetId.value = ''

    parentMeeting.meeting_date = ''

    parentMeeting.meeting_reason = ''

    parentMeeting.meeting_link = ''

    showParentMeetingForm.value = false

  }

}


/* =========================================================
   SCHEDULE MEETING
========================================================= */

async function scheduleMeeting(type) {

  const isStudent =
    type === 'student'


  const targetId =
    isStudent
      ? studentTargetId.value
      : parentTargetId.value


  const form =
    isStudent
      ? studentMeeting
      : parentMeeting


  if (!targetId) {

    message.value =
      isStudent
        ? 'Please choose a student.'
        : 'Please choose a parent.'

    return

  }


  if (!form.meeting_date) {

    message.value =
      'Please choose the meeting date and time.'

    return

  }


  meetingLoading.value =
    type

  message.value = ''


  try {

    const payload = {

      meeting_date:
        form.meeting_date,

      meeting_reason:
        form.meeting_reason ||
        (
          isStudent
            ? 'One-to-one session with tutor'
            : 'Tutor-parent meeting'
        ),

      meeting_link:
        form.meeting_link ||
        undefined

    }


    if (isStudent) {

      payload.student_id =
        Number(targetId)

    } else {

      payload.parent_id =
        Number(targetId)

    }


    const response =
      await tutorApi.requestMeeting(
        payload
      )


    if (
      response?.success === false ||
      response?.status === 'error'
    ) {

      throw new Error(
        response?.message ||
        'Unable to schedule the meeting.'
      )

    }


    const label =
      isStudent
        ? 'Student'
        : 'Parent'


    message.value =
      `${label} meeting scheduled successfully.`


    emit(
      'toast',
      `${label} meeting scheduled successfully.`
    )


    resetMeetingForm(type)

    await loadMeetingRequests()

  } catch (error) {

    message.value =
      error?.message ||
      'Unable to schedule the meeting.'


    emit(
      'toast',
      message.value
    )

  } finally {

    meetingLoading.value = ''

  }

}


/* =========================================================
   APPROVE / DENY / CHANGE MEETING
========================================================= */

async function decideRequest(
  request,
  decision
) {

  if (!request?.meeting_id) {
    return
  }


  const payload = {
    decision
  }


  if (decision === 'deny') {

    const reason =
      window.prompt(
        'Reason for denying this meeting request:',
        ''
      )


    if (reason === null) {
      return
    }


    const trimmedReason = reason.trim()
    if (!trimmedReason) {
      message.value = 'A denial reason is required.'
      emit('toast', 'A denial reason is required.')
      return
    }
    payload.reason = trimmedReason

  }


  if (decision === 'change') {

    const proposedDate =
      window.prompt(
        'Preferred date (YYYY-MM-DD):',
        request.date ||
        request.session_date ||
        ''
      )


    if (proposedDate === null) {
      return
    }


    const proposedStart =
      window.prompt(
        'Preferred start time (HH:MM):',
        request.start_time || ''
      )


    if (proposedStart === null) {
      return
    }


    const proposedEnd =
      window.prompt(
        'Preferred end time (HH:MM):',
        request.end_time || ''
      )


    if (proposedEnd === null) {
      return
    }


    const reason =
      window.prompt(
        'Message for the parent:',
        'Please use the proposed time.'
      )


    if (reason === null) {
      return
    }


    payload.session_date =
      proposedDate

    payload.start_time =
      proposedStart

    payload.end_time =
      proposedEnd

    payload.reason =
      reason.trim() ||
      'Tutor requested a different meeting time.'

  }


  meetingLoading.value =
    `request-${request.meeting_id}`


  try {

    const response =
      await tutorApi.decideMeeting(
        request.meeting_id,
        payload
      )


    if (
      response?.success === false ||
      response?.status === 'error'
    ) {

      throw new Error(
        response?.message ||
        'Unable to update the meeting request.'
      )

    }


    const text =
      decision === 'approve'
        ? 'Meeting approved. It is now scheduled and appears in Schedule.'
        : decision === 'deny'
          ? 'Meeting denied and the reason was sent to the requester.'
          : 'Change request sent to the requester.'


    message.value =
      text


    emit(
      'toast',
      text
    )


    await loadMeetingRequests()

  } catch (error) {

    message.value =
      error?.message ||
      'Unable to update the meeting request.'


    emit(
      'toast',
      message.value
    )

  } finally {

    meetingLoading.value = ''

  }

}


/* =========================================================
   INITIAL LOAD
========================================================= */

onMounted(() => {

  loadMeetingRequests()

})

</script>


<style scoped>

.connect-grid {

  display: grid;

  grid-template-columns:
    repeat(
      2,
      minmax(0, 1fr)
    );

  gap: 14px;

}


.connect-card {

  padding: 18px;
  box-shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;

  border:
    1px solid
    rgba(
      148,
      163,
      184,
      0.18
    );

  border-radius: 18px;

  background:
    rgba(
      248,
      250,
      252,
      0.72
    );

}

.connect-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 36px rgba(15, 23, 42, 0.10);
}


.connect-card-head {

  display: flex;

  align-items:
    flex-start;

  gap: 12px;

  margin-bottom: 16px;

}


.connect-card-head h4 {

  margin: 0;

  font-size: 15px;

  font-weight: 800;

}


.connect-card-head p {

  margin:
    5px 0 0;

  color:
    #64748b;

  font-size: 12px;

  line-height: 1.45;

}


.connect-icon {

  width: 42px;

  height: 42px;

  display: inline-flex;

  align-items: center;

  justify-content: center;

  border-radius: 13px;

  flex:
    0 0 auto;

  font-size: 19px;

}


.student-icon {

  background:
    #e0f2fe;

}


.parent-icon {

  background:
    #f3e8ff;

}


.field-stack {

  display: grid;

  gap: 11px;

}


.message-box {

  resize: vertical;

  min-height: 82px;

}


.action-row {

  display: flex;

  flex-wrap: wrap;

  gap: 8px;

  margin-top: 3px;

}


.message-btn {

  background:
    #f8fafc !important;

  color:
    #334155 !important;

  border:
    1px solid
    #cbd5e1 !important;

}


.message-btn:hover {

  background:
    #f1f5f9 !important;

}


.meeting-form {

  display: grid;

  gap: 11px;

  padding: 14px;

  margin-top: 3px;

  border:
    1px solid
    rgba(
      99,
      102,
      241,
      0.15
    );

  border-radius: 14px;

  background:
    rgba(
      238,
      242,
      255,
      0.45
    );

}


.connect-button {

  margin-top: 2px;

}


.status-message {

  margin-top: 12px;

}


/* =========================================================
   REQUESTS
========================================================= */

.request-card .ch {

  display: flex;

  align-items:
    flex-start;

  justify-content:
    space-between;

  gap: 12px;

}


.request-count {

  padding:
    7px 11px;

  border-radius:
    999px;

  background:
    #eef2ff;

  color:
    #4f46e5;

  font-size:
    11px;

  font-weight:
    800;

  white-space:
    nowrap;

}


.empty-request {

  display: flex;

  align-items:
    center;

  gap: 12px;

  padding: 18px;

  border-radius: 14px;

  background:
    rgba(
      248,
      250,
      252,
      0.8
    );

  color:
    #64748b;

}


.empty-request strong {

  display: block;

  color:
    #334155;

}


.empty-request p {

  margin:
    3px 0 0;

  font-size:
    12px;

}


.empty-icon {

  width: 38px;

  height: 38px;

  display: inline-flex;

  align-items: center;

  justify-content: center;

  border-radius: 12px;

  background:
    #ecfdf5;

  color:
    #059669;

  font-weight:
    900;

}


.request-row {

  display: flex;

  align-items:
    center;

  justify-content:
    space-between;

  gap: 18px;

  padding: 16px;

  border:
    1px solid
    rgba(
      148,
      163,
      184,
      0.16
    );

  border-radius: 16px;

  background:
    rgba(
      248,
      250,
      252,
      0.74
    );

  margin-top: 10px;

}


.request-title {

  font-size:
    15px;

  font-weight:
    800;

  color:
    #1e293b;

}


.request-meta {

  display: flex;

  flex-wrap: wrap;

  gap:
    7px 13px;

  margin-top: 7px;

  color:
    #64748b;

  font-size:
    12px;

}


.request-reason {

  margin:
    9px 0 0;

  color:
    #475569;

  font-size:
    12px;

}


.request-status {

  display: inline-flex;

  margin-top: 9px;

  padding:
    5px 9px;

  border-radius:
    999px;

  background:
    #fff7ed;

  color:
    #c2410c;

  font-size:
    10px;

  font-weight:
    800;

}


.request-actions {

  display: flex;

  flex-wrap: wrap;

  justify-content:
    flex-end;

  gap: 7px;

  flex:
    0 0 auto;

}


.danger-btn {

  background:
    #fff1f2 !important;

  color:
    #e11d48 !important;

  border:
    1px solid
    #fecdd3 !important;

}


.danger-btn:hover {

  background:
    #ffe4e6 !important;

}


/* =========================================================
   CONVERSATION
========================================================= */

.conversation-heading {

  padding:
    12px 14px;

  border-bottom:
    1px solid
    rgba(
      148,
      163,
      184,
      0.14
    );

}


.conversation-heading strong {

  display: block;

  font-size:
    14px;

}


.conversation-heading span {

  display: block;

  margin-top:
    2px;

  color:
    #64748b;

  font-size:
    11px;

}


.no-conversation {

  min-height:
    240px;

  display: flex;

  flex-direction:
    column;

  align-items:
    center;

  justify-content:
    center;

  text-align:
    center;

  color:
    #64748b;

  padding:
    24px;

}


.no-conversation strong {

  margin-top:
    10px;

  color:
    #334155;

}


.no-conversation p {

  margin-top:
    4px;

  font-size:
    12px;

}


/* =========================================================
   CHATBOT-STYLE CONTACT SELECTOR
========================================================= */

.chat {

  grid-template-columns:
    272px 1fr !important;

}


.clist {

  display: flex;

  flex-direction: column;

  overflow-y: auto;

  max-height: 560px;

}


.connect-with {

  display: grid;

  gap: 8px;

  padding: 14px 13px 12px;

  border-bottom:
    1px solid
    var(--border);

  position: sticky;

  top: 0;

  background:
    var(--panel);

  backdrop-filter: blur(22px);

  z-index: 1;

}


.contact-type-toggle {

  display: flex;

  gap: 6px;

  flex-wrap: wrap;

}


.ct-pill {

  padding: 6px 10px;

  border-radius: 999px;

  font-size: 11px;

  font-weight: 700;

  border:
    1px solid
    var(--border);

  background:
    var(--panel);

  color:
    var(--muted);

  cursor: pointer;

  transition:
    background .18s ease,
    color .18s ease,
    border-color .18s ease;

}


.ct-pill.on {

  color: #fff;

  border-color: transparent;

}


.ct-pill.student-pill.on {

  background:
    linear-gradient(135deg, #2563eb, #38bdf8);

}


.ct-pill.parent-pill.on {

  background:
    linear-gradient(135deg, #7c3aed, #14b8a6);

}


.ct-pill:not(.student-pill):not(.parent-pill).on {

  background:
    linear-gradient(135deg, var(--g1), var(--g2));

}


.search-field {

  font-size: 12.5px;

  padding: 9px 11px;

}


.clist-no-results {

  padding: 18px 14px;

  font-size: 12px;

  color: var(--muted);

  text-align: center;

}


.clist-group {

  padding: 6px 0 4px;

}


.clist-group-label {

  padding: 9px 13px 5px;

  font-size: 10.5px;

  font-weight: 800;

  letter-spacing: .04em;

}


.clist-group-label.student-label {

  color: #2563eb;

}


.clist-group-label.parent-label {

  color: #7c3aed;

}


.ci {

  position: relative;

}


.ci-body {

  min-width: 0;

}


.ci-body .t {

  overflow: hidden;

  text-overflow: ellipsis;

  white-space: nowrap;

}


.ci-body .s {

  overflow: hidden;

  text-overflow: ellipsis;

  white-space: nowrap;

}


.av.student-av {

  background:
    linear-gradient(135deg, #2563eb, #38bdf8);

}


.av.parent-av {

  background:
    linear-gradient(135deg, #7c3aed, #14b8a6);

}


.new-doubt-badge {

  flex:
    0 0 auto;

  font-size: 9.5px;

  font-weight: 800;

  color: #e11d48;

  white-space: nowrap;

}


.heading-badge {

  display: inline-block;

  margin-top: 6px;

}


.conversation-heading {

  display: flex;

  align-items: flex-start;

  gap: 10px;

}


.heading-av {

  width: 36px;

  height: 36px;

  font-size: 12px;

}


.child-chips {

  display: flex;

  flex-wrap: wrap;

  gap: 5px;

  margin-top: 6px;

}


.child-chip {

  padding: 3px 8px;

  border-radius: 999px;

  background:
    rgba(20, 184, 166, 0.12);

  color: #0f766e;

  font-size: 10.5px;

  font-weight: 700;

  white-space: nowrap;

}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (max-width: 900px) {

  .connect-grid {

    grid-template-columns:
      1fr;

  }


  .chat {

    grid-template-columns:
      1fr !important;

  }


  .clist {

    max-height: 280px;

    border-right: none;

    border-bottom:
      1px solid
      var(--border);

  }


  .request-row {

    align-items:
      flex-start;

    flex-direction:
      column;

  }


  .request-actions {

    justify-content:
      flex-start;

  }

}


@media (max-width: 600px) {

  .action-row {

    flex-direction:
      column;

  }


  .action-row .btn {

    width:
      100%;

  }

}

</style>