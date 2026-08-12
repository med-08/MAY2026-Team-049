import { createRouter, createWebHistory } from 'vue-router'
import { globalSearch } from '../composables/useSearch'

// Public Pages
import LandingPage from '../views/LandingPage.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'

// Admin Layout
import AppLayout from '../components/layout/AppLayout.vue'

// Admin Pages
import Dashboard from '../views/admin/Dashboard.vue'
import Students from '../views/admin/Students.vue'
import Tutors from '../views/admin/Tutors.vue'
import Parents from '../views/admin/Parents.vue'
import PendingApprovals from '../views/admin/PendingApprovals.vue'
import Analytics from '../views/admin/Analytics.vue'
import AdminProfile from '../views/admin/AdminProfile.vue'

// Student Layout
import StudentLayout from '../components/layout/StudentLayout.vue'

// Student Pages
import StudentDashboard from '../views/student/Dashboard.vue'
import StudentMySessions from '../views/student/MySessions.vue'
import StudentSessionBooking from '../views/student/SessionBooking.vue'
import StudentTimetable from '../views/student/Timetable.vue'
import StudentWeeklyQuiz from '../views/student/WeeklyQuiz.vue'
import StudentQuizAttempt from '../views/student/QuizAttempt.vue'
import StudentAssignments from '../views/student/Assignments.vue'
import StudentHomework from '../views/student/Homework.vue'
import StudentStudyResources from '../views/student/StudyResources.vue'
import StudentStudyTips from '../views/student/StudyTips.vue'
import StudentFAQ from '../views/student/FAQ.vue'
import StudentAskDoubt from '../views/student/AskDoubt.vue'
import StudentProfile from '../views/student/Profile.vue'

// Parent Layout
import ParentLayout from '../components/layout/ParentLayout.vue'

// Parent Pages
import ParentDashboard from '../views/parent/Dashboard.vue'
import ParentProgress from '../views/parent/Progress.vue'
import ParentCurriculum from '../views/parent/Curriculum.vue'
import ParentSchedule from '../views/parent/Schedule.vue'
import ParentMessages from '../views/parent/Messages.vue'
import ParentMeetings from '../views/parent/Meetings.vue'
import ParentProfile from '../views/parent/Profile.vue'

// Tutor Layout
import TutorLayout from '../components/layout/TutorLayout.vue'

// Tutor Pages
import TutorDashboard from '../views/tutor/Dashboard.vue'
import TutorSchedule from '../views/tutor/Schedule.vue'
import TutorStudents from '../views/tutor/Students.vue'
import TutorAttendance from '../views/tutor/Attendance.vue'
import TutorAssignments from '../views/tutor/Assignments.vue'
import TutorMaterials from '../views/tutor/Materials.vue'
import TutorQaBoard from '../views/tutor/QaBoard.vue'
import TutorDoubts from '../views/tutor/Doubts.vue'
import TutorMessages from '../views/tutor/Messages.vue'
import TutorEarnings from '../views/tutor/Earnings.vue'
import TutorProfile from '../views/tutor/Profile.vue'

const routes = [
  // Public
  {
    path: '/',
    name: 'landing',
    component: LandingPage,
    meta: { title: 'LearnAtHome' }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { title: 'Login' }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { title: 'Register' }
  },

  // Admin
  {
    path: '/admin',
    component: AppLayout,
    children: [
      { path: '', name: 'dashboard', component: Dashboard, meta: { title: 'Dashboard' } },
      { path: 'students', name: 'students', component: Students, meta: { title: 'Students' } },
      { path: 'tutors', name: 'tutors', component: Tutors, meta: { title: 'Tutors' } },
      { path: 'parents', name: 'parents', component: Parents, meta: { title: 'Parents' } },
      { path: 'pending-approvals', name: 'pending-approvals', component: PendingApprovals, meta: { title: 'Pending Approvals' } },
      { path: 'analytics', name: 'analytics', component: Analytics, meta: { title: 'Analytics' } },
      { path: 'profile', name: 'profile', component: AdminProfile, meta: { title: 'Admin Profile' } }
    ]
  },

  // Student
  {
    path: '/student',
    component: StudentLayout,
    children: [
      { path: '', redirect: '/student/dashboard' },
      { path: 'dashboard', name: 'student-dashboard', component: StudentDashboard, meta: { title: 'Dashboard' } },
      { path: 'sessions', name: 'student-my-sessions', component: StudentMySessions, meta: { title: 'My Sessions' } },
      { path: 'booking', name: 'student-session-booking', component: StudentSessionBooking, meta: { title: 'Session Booking' } },
      { path: 'timetable', name: 'student-timetable', component: StudentTimetable, meta: { title: 'Timetable' } },
      { path: 'quiz', name: 'student-weekly-quiz', component: StudentWeeklyQuiz, meta: { title: 'Weekly Quiz' } },
      { path: 'quiz/:id', name: 'student-quiz-attempt', component: StudentQuizAttempt, meta: { title: 'Take Quiz' } },
      { path: 'assignments', name: 'student-assignments', component: StudentAssignments, meta: { title: 'Interactive Assignments' } },
      { path: 'homework', name: 'student-homework', component: StudentHomework, meta: { title: 'Homework' } },
      { path: 'resources', name: 'student-study-resources', component: StudentStudyResources, meta: { title: 'Study Resources' } },
      { path: 'study-tips', name: 'student-study-tips', component: StudentStudyTips, meta: { title: 'Study Tips' } },
      { path: 'faq', name: 'student-faq', component: StudentFAQ, meta: { title: 'FAQ' } },
      { path: 'ask-doubt', name: 'student-ask-doubt', component: StudentAskDoubt, meta: { title: 'Ask Doubt' } },
      { path: 'profile', name: 'student-profile', component: StudentProfile, meta: { title: 'Student Profile' } }
    ]
  },

  // Parent
  {
    path: '/parent',
    component: ParentLayout,
    children: [
      { path: '', name: 'parent-dashboard', component: ParentDashboard, meta: { title: 'Dashboard' } },
      { path: 'progress', name: 'parent-progress', component: ParentProgress, meta: { title: 'Child Progress' } },
      { path: 'curriculum', name: 'parent-curriculum', component: ParentCurriculum, meta: { title: 'Curriculum Plan' } },
      { path: 'schedule', name: 'parent-schedule', component: ParentSchedule, meta: { title: 'Schedule' } },
      { path: 'messages', name: 'parent-messages', component: ParentMessages, meta: { title: 'Messages' } },
      { path: 'meetings', name: 'parent-meetings', component: ParentMeetings, meta: { title: 'Meeting Requests' } },
      { path: 'profile', name: 'parent-profile', component: ParentProfile, meta: { title: 'Parent Profile' } }
    ]
  },

  // Tutor
  {
    path: '/tutor',
    component: TutorLayout,
    children: [
      { path: '', redirect: '/tutor/dashboard' },
      { path: 'dashboard', name: 'tutor-dashboard', component: TutorDashboard, meta: { title: 'Tutor Dashboard', tutorView: 'dashboard' } },
      { path: 'schedule', name: 'tutor-schedule', component: TutorSchedule, meta: { title: 'Tutor Schedule', tutorView: 'schedule' } },
      { path: 'students', name: 'tutor-students', component: TutorStudents, meta: { title: 'Tutor Students', tutorView: 'students' } },
      { path: 'attendance', name: 'tutor-attendance', component: TutorAttendance, meta: { title: 'Tutor Attendance', tutorView: 'attendance' } },
      { path: 'assignments', name: 'tutor-assignments', component: TutorAssignments, meta: { title: 'Tutor Assignments', tutorView: 'assignments' } },
      { path: 'materials', name: 'tutor-materials', component: TutorMaterials, meta: { title: 'Tutor Materials', tutorView: 'materials' } },
      { path: 'qa', name: 'tutor-qa', component: TutorQaBoard, meta: { title: 'Tutor Q&A Board', tutorView: 'qa' } },
      { path: 'doubts', name: 'tutor-doubts', component: TutorDoubts, meta: { title: 'Student Doubts', tutorView: 'doubts' } },
      { path: 'messages', name: 'tutor-messages', component: TutorMessages, meta: { title: 'Tutor Messages', tutorView: 'messages' } },
      { path: 'earnings', name: 'tutor-earnings', component: TutorEarnings, meta: { title: 'Tutor Earnings', tutorView: 'earnings' } },
      { path: 'profile', name: 'tutor-profile', component: TutorProfile, meta: { title: 'Tutor Profile', tutorView: 'profile' } }
    ]
  },

  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to, from, next) => {
  let user = null

  try {
    user = JSON.parse(localStorage.getItem('user') || 'null')
  } catch {
    user = null
  }

  if (!user) {
    const role = localStorage.getItem('role')
    const username = localStorage.getItem('username')
    const token = localStorage.getItem('token')
    const user_id = localStorage.getItem('user_id')
    const parent_id = localStorage.getItem('parent_id')
    const student_id = localStorage.getItem('student_id')
    const tutor_id = localStorage.getItem('tutor_id')

    if (role) {
      user = { role, username, token, user_id, parent_id, student_id, tutor_id }
    }
  }

  const path = to.path.toLowerCase()

  if (path.startsWith('/admin')) {
    if (!user || user.role !== 'Admin') {
      return next('/login')
    }
  }

  if (path.startsWith('/tutor')) {
    if (!user || user.role !== 'Tutor') {
      return next('/login')
    }
  }

  if (path.startsWith('/student')) {
    if (!user || user.role !== 'Student') {
      return next('/login')
    }
  }

  if (path.startsWith('/parent')) {
    if (!user || user.role !== 'Parent') {
      return next('/login')
    }
  }

  globalSearch.value = typeof to.query.q === 'string' ? to.query.q : ''
  next()
})

router.afterEach((to) => {
  document.title = to.meta?.title ? `${to.meta.title} | LearnAtHome` : 'LearnAtHome'
})

export default router