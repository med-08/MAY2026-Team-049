<template>
  <div class="tutor-portal">

    <svg
      width="0"
      height="0"
      style="position:absolute"
    >
      <defs>
        <linearGradient
          id="ig"
          x1="0"
          y1="0"
          x2="1"
          y2="1"
        >
          <stop
            offset="0"
            stop-color="#8B6BFF"
          />

          <stop
            offset="1"
            stop-color="#4CC9F0"
          />
        </linearGradient>
      </defs>
    </svg>

    <div class="aurora">
      <b class="a1"></b>
      <b class="a2"></b>
      <b class="a3"></b>
    </div>

    <div
      ref="ringRef"
      class="cur-ring"
    ></div>

    <div
      ref="dotRef"
      class="cur-dot"
    ></div>

    <div
      class="scrim"
      :class="{ on: Boolean(selectedStudent) }"
      @click="closeDrawer"
    ></div>

    <div class="shell">

      <!-- =====================================================
           TUTOR SIDEBAR
      ====================================================== -->

      <TutorSidebar
        :groups="navGroups"
        :active-view="activeView"
        :mobile-open="mobileMenuOpen"
        :dark="isDark"
        :counts="{
          openDoubts,
          unreadMessages
        }"
        @navigate="navigate"
        @toggle-theme="toggleTheme"
        @logout="logoutModalOpen = true"
      />

      <!-- =====================================================
           MAIN CONTENT
      ====================================================== -->

      <main
        ref="mainRef"
        class="main"
      >

        <TutorTopbar
          :title="activeTitle"
          :clock-label="clockLabel"
          :mobile-open="mobileMenuOpen"
          :notifications-open="notificationsOpen"
          :notifications="notificationState"
          @toggle-menu="
            mobileMenuOpen = !mobileMenuOpen
          "
          @open-command="
            commandOpen = true
          "
          @toggle-notifications="
            notificationsOpen =
              !notificationsOpen
          "
          @close-notifications="
            notificationsOpen = false
          "
          @select-notification="
            selectNotification
          "
          @open-profile="
            navigate('profile')
          "
        />

        <!-- =====================================================
             ROUTER VIEW

             The router-view changes only the page content.
             TutorLayout remains mounted.

             Session state therefore remains available when
             moving between Schedule, Dashboard, Attendance,
             Materials, Assignments, etc.
        ====================================================== -->

        <router-view v-slot="{ Component }">
          <component
            :is="Component"
            v-bind="routeProps"
            @navigate="navigate"
            @toast="addToast"
            @select-student="selectedStudent = $event"
            @confirm-action="requestConfirm"
            @publish="publishFaq"
            @delete-faq="deleteFaq"
            @reply="replyToDoubt"
            @select-conversation="activeConversationId = $event"
            @send-message="sendMessage"
            @session-updated="updateSessionState"
          />
        </router-view>

      </main>

    </div>

    <!-- =======================================================
         STUDENT DRAWER
    ======================================================== -->

    <TutorStudentDrawer
      :student="selectedStudent"
      :scores="selectedStudentScores"
      :sessions="selectedStudentSessions"
      @close="closeDrawer"
      @toast="addToast"
    />

    <!-- =======================================================
         COMMAND PALETTE
    ======================================================== -->

    <TutorCommandPalette
      :open="commandOpen"
      :items="commandItems"
      @close="
        commandOpen = false
      "
      @run="runCommand"
    />

    <!-- =======================================================
         CONFIRM MODAL
    ======================================================== -->

    <TutorConfirmModal
      :open="confirm.open"
      title="Confirm action"
      :message="confirm.message"
      @cancel="
        confirm.open = false
      "
      @confirm="confirmAction"
    />

    <!-- =======================================================
         LOGOUT MODAL
    ======================================================== -->

    <TutorConfirmModal
      :open="logoutModalOpen"
      title="Log out of LearnAtHome?"
      message="You will need to sign in again to access the tutor dashboard."
      @cancel="
        logoutModalOpen = false
      "
      @confirm="confirmLogout"
    />

    <!-- =======================================================
         TOAST
    ======================================================== -->

    <TutorToastContainer
      :toasts="toasts"
    />

  </div>
</template>


<script setup>

import {
  computed,
  nextTick,
  onMounted,
  onUnmounted,
  reactive,
  ref,
  watch
} from 'vue'

import {
  useRoute,
  useRouter
} from 'vue-router'

import { useTheme } from '../../composables/useTheme'

import { useLogout } from '../../composables/useLogout'

import TutorCommandPalette
  from '../tutor/TutorCommandPalette.vue'

import TutorConfirmModal
  from '../tutor/TutorConfirmModal.vue'

import TutorSidebar
  from '../tutor/TutorSidebar.vue'

import TutorStudentDrawer
  from '../tutor/TutorStudentDrawer.vue'

import TutorToastContainer
  from '../tutor/TutorToastContainer.vue'

import TutorTopbar
  from '../tutor/TutorTopbar.vue'

import { tutorApi }
  from '../../services/tutorApi'

import '../../assets/tutorStyles.css'


/* ============================================================
   NAVIGATION
============================================================ */

const navGroups = [

  {
    label: 'Teaching',

    items: [

      {
        id: 'dashboard',
        label: 'Dashboard',
        icon: '<rect x="3" y="3" width="7" height="9" rx="1.5"/>'
      },

      {
        id: 'schedule',
        label: 'Schedule',
        icon: '<rect x="3" y="4.5" width="18" height="16" rx="2"/>'
      },

      {
        id: 'students',
        label: 'Students',
        icon: '<circle cx="9" cy="8" r="3.2"/>'
      },

      {
        id: 'attendance',
        label: 'Attendance',
        icon: '<rect x="3.5" y="4" width="17" height="17" rx="2.5"/>'
      }

    ]
  },

  {
    label: 'Content',

    items: [

      {
        id: 'assignments',
        label: 'Assignments',
        icon: '<path d="M8 3h8l3 3v14H5V4Z"/>'
      },

      {
        id: 'materials',
        label: 'Materials',
        icon: '<path d="M4 6a2 2 0 0 1 2-2h4l2 2h6a2 2 0 0 1 2 2v9H6a2 2 0 0 1-2-2Z"/>'
      },

      {
        id: 'qa',
        label: 'Q&A board',
        icon: '<path d="M4 5h16v11H8l-4 3.5V5Z"/>'
      }

    ]
  },

  {
    label: 'You',

    items: [

      {
        id: 'doubts',
        label: 'Doubts',
        icon: '<path d="M12 3a7 7 0 0 1 4 12.7V18H8v-2.3A7 7 0 0 1 12 3Z"/>',
        countKey: 'openDoubts'
      },

      {
        id: 'messages',
        label: 'Connect with Parents / Students',
        icon: '<path d="M4 5h16v10H9l-5 4V5Z"/>',
        countKey: 'unreadMessages'
      },

      {
        id: 'profile',
        label: 'Profile',
        icon: '<circle cx="12" cy="8" r="4"/>'
      }

    ]
  }

]


/* ============================================================
   VIEW TITLES
============================================================ */

const viewTitles = {

  dashboard: {
    prefix: 'Good evening, ',
    highlight: ''
  },

  schedule: {
    prefix: 'Your ',
    highlight: 'schedule'
  },

  students: {
    prefix: 'Your ',
    highlight: 'students'
  },

  attendance: {
    prefix: 'Take ',
    highlight: 'attendance'
  },

  assignments: {
    prefix: 'Assignments & ',
    highlight: 'quizzes'
  },

  materials: {
    prefix: 'Study ',
    highlight: 'materials'
  },

  qa: {
    prefix: 'Q&A ',
    highlight: 'board'
  },

  doubts: {
    prefix: 'Student ',
    highlight: 'doubts'
  },

  messages: {
    prefix: 'Connect with ',
    highlight: 'parents / students'
  },

  profile: {
    prefix: 'Tutor ',
    highlight: 'profile'
  }

}


const commandItems = []


/* ============================================================
   ROUTER
============================================================ */

const route = useRoute()

const router = useRouter()


/* ============================================================
   COMPOSABLES
============================================================ */

const {
  isDark,
  toggleTheme
} = useTheme()


const {
  logout
} = useLogout()


/* ============================================================
   UI STATE
============================================================ */

const mobileMenuOpen = ref(false)

const commandOpen = ref(false)

const notificationsOpen = ref(false)

const logoutModalOpen = ref(false)

const selectedStudent = ref(null)

const activeConversationId = ref('rao')

const activeKey = ref('dashboard-0')

const clockLabel = ref('')

const toasts = ref([])

const confirm = reactive({
  open: false,
  message: ''
})


/* ============================================================
   PERSISTENT TUTOR DATA
============================================================ */

const tutorUserState = ref({

  name: '',

  displayName: '',

  userId: null,

  subjects: [],

  languages: [],

  certificates: []

})


const dashboardStatsState = ref([])

const sessionsState = ref([])

const todayOverviewState = ref([])

const recentActivitiesState = ref([])

const upcomingDeadlinesState = ref([])

const aiSuggestionsState = ref([])

const upcomingMeetingsState = ref([])

const leaderboardState = ref([])

const achievementsState = ref([])

const scheduleRowsState = ref([])

const calendarEventsState = ref([])

const scheduleSubjectsState = ref([])

const studentsState = ref([])

const attendanceState = ref([])

const attendanceAnalyticsState = ref([])

const assignmentsState = ref([])

const studyResourcesState = ref([])

const notificationState = ref([])

const faqEntries = ref([])

const doubts = ref([])

const conversations = ref({})


/* ============================================================
   DOM / EFFECT STATE
============================================================ */

const mainRef = ref(null)

const ringRef = ref(null)

const dotRef = ref(null)

const reduceMotion = ref(false)

const hoverPointer = ref(false)


let clockTimer = 0
let meetingRefreshTimer = 0

let toastId = 0

let revealObserver = null

let cursorFrame = 0

let mx = 0

let my = 0

let rx = 0

let ry = 0


const chatTimers = new Set()


/* ============================================================
   ACTIVE VIEW
============================================================ */

const activeView = computed(
  () =>
    route.meta.tutorView ||
    'dashboard'
)


/* ============================================================
   GREETING
============================================================ */

const greeting = computed(() => {

  const hour =
    new Date().getHours()

  if (hour < 12) {
    return 'Good morning'
  }

  if (hour < 17) {
    return 'Good afternoon'
  }

  return 'Good evening'

})


/* ============================================================
   TITLE
============================================================ */

const activeTitle = computed(() => {

  if (
    activeView.value ===
    'dashboard'
  ) {

    return {

      prefix:
        `${greeting.value}, `,

      highlight:
        tutorUserState.value
          .displayName ||
        tutorUserState.value.name

    }

  }

  return (
    viewTitles[
      activeView.value
    ] ||
    viewTitles.dashboard
  )

})


/* ============================================================
   COUNTS
============================================================ */

const openDoubts = computed(() =>

  doubts.value.filter(
    doubt =>
      doubt.status === 'Open'
  ).length

)


const unreadMessages = computed(() =>

  notificationState.value.filter(
    n =>
      !n.isRead &&
      [
        'New Message',
        'Message',
        'Meeting Request',
        'Meeting Scheduled',
        'Meeting Approved',
        'Meeting Denied',
        'Session Updated',
        'Attendance Confirmation',
        'Class Completed'
      ].includes(
        n.type ||
        n.notification_type
      )
  ).length

)


/* ============================================================
   DRAWER DATA
============================================================ */

const selectedStudentScores =
  computed(() => [])


const selectedStudentSessions =
  computed(() => [])


/* ============================================================
   ROUTE PROPS
============================================================ */

const routeProps = computed(() => {

  const shared = {

    activeKey:
      activeKey.value,

    reduceMotion:
      reduceMotion.value

  }


  const propsByView = {

    dashboard: {

      stats:
        dashboardStatsState.value,

      sessions:
        sessionsState.value,

      overview:
        todayOverviewState.value,

      activities:
        recentActivitiesState.value,

      deadlines:
        upcomingDeadlinesState.value,

      suggestions:
        aiSuggestionsState.value,

      meetings:
        upcomingMeetingsState.value,

      leaderboard:
        leaderboardState.value,

      achievements:
        achievementsState.value,

      ...shared

    },


    schedule: {

      rows:
        scheduleRowsState.value,

      events:
        calendarEventsState.value,

      sessions:
        sessionsState.value,

      subjects:
        scheduleSubjectsState.value

    },


    students: {

      students:
        studentsState.value

    },


    attendance: {

      records:
        attendanceState.value,

      students:
        studentsState.value,

      analytics:
        attendanceAnalyticsState.value,

      sessions:
        sessionsState.value

    },


    assignments: {

      assignments:
        assignmentsState.value,

      sessions:
        sessionsState.value

    },


    materials: {

      resources:
        studyResourcesState.value,

      sessions:
        sessionsState.value

    },


    qa: {

      entries:
        faqEntries.value

    },


    doubts: {

      doubts:
        doubts.value,

      students:
        studentsState.value

    },


    messages: {

      conversations:
        conversations.value,

      activeConversationId:
        activeConversationId.value,

      students:
        studentsState.value

    },


    profile: {

      tutor:
        tutorUserState.value

    }

  }


  return (
    propsByView[
      activeView.value
    ] ||
    propsByView.dashboard
  )

})


/* ============================================================
   UPDATE SESSION STATE
============================================================ */

function updateSessionState(updatedSession) {

  if (!updatedSession) {
    return
  }

  if (updatedSession.removed) {
    const removedId = updatedSession.id ?? updatedSession.session_id
    sessionsState.value = sessionsState.value.filter(session => String(session.id ?? session.session_id) !== String(removedId))
    return
  }


  const updatedId =
    updatedSession.id ??
    updatedSession.session_id


  if (updatedId == null) {
    return
  }


  const index =
    sessionsState.value.findIndex(
      session =>
        String(
          session.id ??
          session.session_id
        ) ===
        String(updatedId)
    )


  if (index === -1) {

    sessionsState.value = [

      ...sessionsState.value,

      updatedSession

    ]

    return

  }


  sessionsState.value =
    sessionsState.value.map(
      (session, i) =>

        i === index
          ? {
              ...session,
              ...updatedSession
            }
          : session
    )

}


/* ============================================================
   BACKEND DATA
============================================================ */

async function fetchBackendData() {

  try {

    const [

      dashRes,
      schedRes,
      stRes,
      attRes,
      asgRes,
      matRes,
      qaRes,
      doubtRes,
      convRes,
      profRes,
      notifRes

    ] = await Promise.allSettled([

      tutorApi.getDashboard(),

      tutorApi.getSchedule(),

      tutorApi.getStudents(),

      tutorApi.getAttendance(),

      tutorApi.getAssignments(),

      tutorApi.getMaterials(),

      tutorApi.getQaEntries(),

      tutorApi.getDoubts(),

      tutorApi.getConversations(),

      tutorApi.getProfile(),

      tutorApi.getNotifications()

    ])


    /* ========================================================
       DASHBOARD
    ======================================================== */

    if (
      dashRes.status === 'fulfilled' &&
      dashRes.value.success
    ) {

      if (dashRes.value.stats) {
        dashboardStatsState.value =
          dashRes.value.stats
      }

      if (dashRes.value.sessions) {
        sessionsState.value =
          dashRes.value.sessions
      }

      if (dashRes.value.overview) {
        todayOverviewState.value =
          dashRes.value.overview
      }

      if (dashRes.value.activities) {
        recentActivitiesState.value =
          dashRes.value.activities
      }

      if (dashRes.value.deadlines) {
        upcomingDeadlinesState.value =
          dashRes.value.deadlines
      }

      if (dashRes.value.suggestions) {
        aiSuggestionsState.value =
          dashRes.value.suggestions
      }

      if (dashRes.value.meetings) {
        upcomingMeetingsState.value =
          dashRes.value.meetings
      }

      if (dashRes.value.leaderboard) {
        leaderboardState.value =
          dashRes.value.leaderboard
      }

      if (dashRes.value.achievements) {
        achievementsState.value =
          dashRes.value.achievements
      }

    }


    /* ========================================================
       SCHEDULE
    ======================================================== */

    if (
      schedRes.status === 'fulfilled' &&
      schedRes.value.success
    ) {

      if (schedRes.value.rows) {

        scheduleRowsState.value =
          schedRes.value.rows

      }


      if (schedRes.value.events) {

        calendarEventsState.value =
          schedRes.value.events

      }


      if (schedRes.value.sessions) {

        sessionsState.value =
          schedRes.value.sessions

      }


      if (schedRes.value.subjects) {

        scheduleSubjectsState.value =
          schedRes.value.subjects

      }

    }


    /* ========================================================
       STUDENTS
    ======================================================== */

    if (
      stRes.status === 'fulfilled' &&
      stRes.value.success
    ) {

      studentsState.value =
        stRes.value.students || []

    }


    /* ========================================================
       ATTENDANCE
    ======================================================== */

    if (
      attRes.status === 'fulfilled' &&
      attRes.value.success
    ) {

      if (attRes.value.records) {

        attendanceState.value =
          attRes.value.records

      }


      if (attRes.value.analytics) {

        attendanceAnalyticsState.value =
          attRes.value.analytics

      }

    }


    /* ========================================================
       ASSIGNMENTS
    ======================================================== */

    if (
      asgRes.status === 'fulfilled' &&
      asgRes.value.success
    ) {

      assignmentsState.value =
        asgRes.value.assignments || []

    }


    /* ========================================================
       MATERIALS
    ======================================================== */

    if (
      matRes.status === 'fulfilled' &&
      matRes.value.success
    ) {

      studyResourcesState.value =
        matRes.value.resources || []

    }


    /* ========================================================
       QA
    ======================================================== */

    if (
      qaRes.status === 'fulfilled' &&
      qaRes.value.success
    ) {

      faqEntries.value =
        qaRes.value.entries || []

    }


    /* ========================================================
       DOUBTS
    ======================================================== */

    if (
      doubtRes.status === 'fulfilled' &&
      doubtRes.value.success
    ) {

      doubts.value =
        doubtRes.value.doubts || []

    }


    /* ========================================================
       CONVERSATIONS
    ======================================================== */

    if (
      convRes.status === 'fulfilled' &&
      convRes.value.success
    ) {

      conversations.value =
        convRes.value.conversations || {}


      if (
        !activeConversationId.value &&
        Object.keys(
          conversations.value
        ).length
      ) {

        activeConversationId.value =
          Object.keys(
            conversations.value
          )[0]

      }

    }


    /* ========================================================
       PROFILE
    ======================================================== */

    if (
      profRes.status === 'fulfilled' &&
      profRes.value.success &&
      profRes.value.tutor
    ) {

      tutorUserState.value =
        profRes.value.tutor

    }


    /* ========================================================
       NOTIFICATIONS
    ======================================================== */

    if (
      notifRes.status === 'fulfilled' &&
      notifRes.value.success
    ) {

      notificationState.value =
        notifRes.value.notifications || []

    }

  }

  catch (error) {

    console.warn(
      'Backend loading warning:',
      error
    )

  }

}


/* ============================================================
   NAVIGATION
============================================================ */

async function refreshMeetingState() {

  try {
    const [scheduleRes, notificationRes] = await Promise.all([
      tutorApi.getSchedule(),
      tutorApi.getNotifications()
    ])

    if (scheduleRes?.success && Array.isArray(scheduleRes.sessions)) {
      sessionsState.value = scheduleRes.sessions
      scheduleRowsState.value = scheduleRes.rows || scheduleRowsState.value
      calendarEventsState.value = scheduleRes.events || calendarEventsState.value
      scheduleSubjectsState.value = scheduleRes.subjects || scheduleSubjectsState.value
    }

    if (notificationRes?.success) {
      notificationState.value = notificationRes.notifications || notificationState.value
    }
  } catch (error) {
    console.warn('Meeting refresh warning:', error)
  }
}


function navigate(view) {

  mobileMenuOpen.value = false

  notificationsOpen.value = false


  const targetName =
    `tutor-${view}`


  if (
    route.name ===
    targetName
  ) {
    return
  }


  router.push({
    name: targetName
  })

}


/* ============================================================
   TOAST
============================================================ */

function addToast(message) {

  const id =
    ++toastId


  toasts.value.push({

    id,

    message

  })


  const timer =
    window.setTimeout(
      () => {

        toasts.value =
          toasts.value.filter(
            toast =>
              toast.id !== id
          )

        chatTimers.delete(
          timer
        )

      },
      2600
    )


  chatTimers.add(timer)

}


/* ============================================================
   NOTIFICATIONS
============================================================ */

async function selectNotification(
  notification
) {

  notification.isRead = true

  notificationsOpen.value = false


  if (notification.id) {

    try {

      await tutorApi.markNotificationRead(
        notification.id
      )

    }

    catch (e) {}

  }


  navigate(
    (
      notification.go ||
      'dashboard'
    )
      .replace(
        '/tutor/',
        ''
      )
      .replace(
        '/student/',
        'dashboard'
      )
  )

}


/* ============================================================
   FAQ
============================================================ */

async function publishFaq(payload) {

  try {

    const res =
      await tutorApi.publishQaEntry(
        payload
      )


    if (
      res.success &&
      res.entry
    ) {

      faqEntries.value.unshift(
        res.entry
      )

      addToast(
        'Published to board · students notified'
      )

    }

    else {

      addToast(
        res.message ||
        'Could not publish to the Q&A board'
      )

    }

  }

  catch (e) {

    addToast(
      e.message ||
      'Could not publish to the Q&A board'
    )

  }

}


/* ============================================================
   DELETE FAQ
============================================================ */

async function deleteFaq(faqId) {

  const previous =
    faqEntries.value


  try {

    const res =
      await tutorApi.deleteQaEntry(
        faqId
      )


    if (res.success) {

      faqEntries.value =
        previous.filter(
          entry =>
            entry.faqId !== faqId
        )

      addToast(
        'Q&A entry deleted'
      )

    }

    else {

      addToast(
        res.message ||
        'Could not delete Q&A entry'
      )

    }

  }

  catch (e) {

    addToast(
      e.message ||
      'Could not delete Q&A entry'
    )

  }

}


/* ============================================================
   DOUBTS
============================================================ */

async function replyToDoubt(
  doubtId,
  replyText
) {

  const doubt =
    doubts.value.find(
      item =>
        item.doubtId === doubtId ||
        item.id === doubtId
    )


  if (doubt) {
    doubt.status = 'Answered'
  }


  try {

    const numericId =
      typeof doubtId === 'number'
        ? doubtId
        : parseInt(
            String(
              doubtId
            ).replace(
              'doubt-',
              ''
            )
          )


    if (!isNaN(numericId)) {

      await tutorApi.replyDoubt(
        numericId,
        replyText
      )

    }

  }

  catch (e) {}


  const student =
    studentsState.value.find(
      item =>
        item.studentId ===
        doubt?.studentId
    )


  addToast(
    `Reply sent to ${
      student?.name ||
      'student'
    }`
  )

}


/* ============================================================
   MESSAGES
============================================================ */

async function sendMessage(
  conversationId,
  message
) {

  const conversation =
    conversations.value[
      conversationId
    ]


  if (!conversation) {
    return
  }


  conversation.messages.push({

    messageId:
      `msg-${Date.now()}`,

    senderId:
      tutorUserState.value.userId,

    receiverId:
      conversationId,

    message,

    timestamp:
      new Date().toISOString(),

    status:
      'sent',

    w:
      'me'

  })


  try {

    await tutorApi.sendMessage({

      receiver_type:
        conversation.otherType,

      receiver_id:
        conversation.otherId,

      message

    })


    addToast(
      `Sent to ${conversation.participantName}`
    )

  }

  catch (e) {

    addToast(
      e.message ||
      'Message could not be sent'
    )

  }

}


/* ============================================================
   COMMAND
============================================================ */

function runCommand(item) {

  if (
    item?.a ===
    'open-command'
  ) {

    commandOpen.value = true

    return

  }


  commandOpen.value = false


  if (
    item?.a ===
    'theme'
  ) {

    toggleTheme()

  }


  if (item?.v) {

    navigate(
      item.v
    )

  }

}


/* ============================================================
   DRAWER
============================================================ */

function closeDrawer() {

  selectedStudent.value =
    null

}


/* ============================================================
   CONFIRM
============================================================ */

function requestConfirm(
  message
) {

  confirm.message =
    message

  confirm.open =
    true

}


function confirmAction() {

  confirm.open =
    false

  addToast(
    'Action confirmed'
  )

}


/* ============================================================
   LOGOUT
============================================================ */

async function confirmLogout() {

  logoutModalOpen.value =
    false

  await logout(
    '/login'
  )

}


/* ============================================================
   CLOCK
============================================================ */

function updateClock() {

  const dayNames = [

    'Sun',
    'Mon',
    'Tue',
    'Wed',
    'Thu',
    'Fri',
    'Sat'

  ]


  const monthNames = [

    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec'

  ]


  const date =
    new Date()


  const hour =
    date.getHours()


  const minute =
    date.getMinutes()


  const meridiem =
    hour < 12
      ? 'AM'
      : 'PM'


  const hour12 =
    (hour % 12) || 12


  clockLabel.value =
    `${dayNames[date.getDay()]} · ` +
    `${date.getDate()} ${monthNames[date.getMonth()]} · ` +
    `${hour12}:${minute < 10 ? '0' : ''}${minute} ${meridiem}`

}


/* ============================================================
   REVEAL
============================================================ */

function runReveal() {

  nextTick(() => {

    const elements = [

      ...document.querySelectorAll(
        '.tutor-portal .view.on .reveal:not(.in)'
      )

    ]


    elements.forEach(
      (
        element,
        index
      ) => {

        if (
          reduceMotion.value ||
          !revealObserver
        ) {

          element.classList.add(
            'in'
          )

          return

        }


        element.style.transitionDelay =
          `${index * 70}ms`


        revealObserver.observe(
          element
        )

      }
    )

  })

}


function setupReveal() {

  if (
    reduceMotion.value
  ) {
    return
  }


  revealObserver =
    new IntersectionObserver(

      entries => {

        entries.forEach(
          entry => {

            if (
              entry.isIntersecting
            ) {

              entry.target.classList.add(
                'in'
              )


              revealObserver.unobserve(
                entry.target
              )

            }

          }
        )

      },

      {
        threshold: 0.08
      }

    )

}


/* ============================================================
   CURSOR
============================================================ */

function setupCursor() {

  if (
    reduceMotion.value ||
    !hoverPointer.value
  ) {
    return
  }


  mx =
    window.innerWidth / 2

  my =
    window.innerHeight / 2

  rx =
    mx

  ry =
    my


  const loop = () => {

    rx +=
      (mx - rx) * 0.16

    ry +=
      (my - ry) * 0.16


    if (ringRef.value) {

      ringRef.value.style.transform =
        `translate(${rx}px,${ry}px)`

    }


    cursorFrame =
      requestAnimationFrame(
        loop
      )

  }


  cursorFrame =
    requestAnimationFrame(
      loop
    )

}


function onMouseMove(event) {

  mx =
    event.clientX

  my =
    event.clientY


  if (dotRef.value) {

    dotRef.value.style.transform =
      `translate(${mx}px,${my}px)`

  }


  if (
    reduceMotion.value
  ) {
    return
  }


  document
    .querySelectorAll(
      '.tutor-portal .magnetic'
    )
    .forEach(
      button => {

        const rect =
          button.getBoundingClientRect()


        const cx =
          rect.left +
          rect.width / 2


        const cy =
          rect.top +
          rect.height / 2


        const dx =
          event.clientX -
          cx


        const dy =
          event.clientY -
          cy


        button.style.transform =
          Math.abs(dx) < 90 &&
          Math.abs(dy) < 60
            ? `translate(${dx * 0.18}px,${dy * 0.22}px)`
            : ''

      }
    )

}


function onMouseOver(event) {

  if (
    !event.target.closest(
      '.tutor-portal'
    )
  ) {
    return
  }


  const selector =
    'a,button,.nav,.qact,.scard,.ci,.icbtn,.ava,.seg span,.toggle span,.lnk,.tt .cell.free,[data-cur],[data-go],[data-student]'


  if (
    event.target.closest(
      selector
    )
  ) {

    ringRef.value?.classList.add(
      'big'
    )

  }

}


function onMouseOut(event) {

  if (
    !event.target.closest(
      '.tutor-portal'
    )
  ) {
    return
  }


  const selector =
    'a,button,.nav,.qact,.scard,.ci,.icbtn,.ava,.seg span,.toggle span,.lnk,.tt .cell.free,[data-cur],[data-go],[data-student]'


  if (
    event.target.closest(
      selector
    )
  ) {

    ringRef.value?.classList.remove(
      'big'
    )

  }

}


/* ============================================================
   ESCAPE
============================================================ */

function onEscape(event) {

  if (
    event.key !==
    'Escape'
  ) {
    return
  }


  if (logoutModalOpen.value) {

    logoutModalOpen.value =
      false

  }

  else if (
    selectedStudent.value
  ) {

    closeDrawer()

  }

  else if (
    notificationsOpen.value
  ) {

    notificationsOpen.value =
      false

  }

  else if (
    commandOpen.value
  ) {

    commandOpen.value =
      false

  }

}


/* ============================================================
   VIEW WATCH
============================================================ */

watch(
  activeView,

  view => {

    activeKey.value =
      `${view}-${Date.now()}`


    mobileMenuOpen.value =
      false

    notificationsOpen.value =
      false


    nextTick(() => {

      runReveal()


      mainRef.value?.scrollTo({

        top: 0,

        behavior:
          reduceMotion.value
            ? 'auto'
            : 'smooth'

      })

    })

  }
)


/* ============================================================
   MOUNT
============================================================ */

onMounted(() => {

  fetchBackendData()
  meetingRefreshTimer = window.setInterval(refreshMeetingState, 15000)


  reduceMotion.value =
    window.matchMedia(
      '(prefers-reduced-motion: reduce)'
    ).matches


  hoverPointer.value =
    window.matchMedia(
      '(hover: hover)'
    ).matches


  updateClock()


  clockTimer =
    window.setInterval(
      updateClock,
      20000
    )


  setupReveal()

  setupCursor()

  runReveal()


  document.addEventListener(
    'mousemove',
    onMouseMove
  )

  document.addEventListener(
    'mouseover',
    onMouseOver
  )

  document.addEventListener(
    'mouseout',
    onMouseOut
  )

  document.addEventListener(
    'keydown',
    onEscape
  )

})


/* ============================================================
   UNMOUNT
============================================================ */

onUnmounted(() => {

  clearInterval(
    clockTimer
  )

  clearInterval(
    meetingRefreshTimer
  )


  revealObserver?.disconnect()


  cancelAnimationFrame(
    cursorFrame
  )


  chatTimers.forEach(
    timer =>
      clearTimeout(timer)
  )


  document.removeEventListener(
    'mousemove',
    onMouseMove
  )

  document.removeEventListener(
    'mouseover',
    onMouseOver
  )

  document.removeEventListener(
    'mouseout',
    onMouseOut
  )

  document.removeEventListener(
    'keydown',
    onEscape
  )

})

</script>