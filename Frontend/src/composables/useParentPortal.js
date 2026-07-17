import { computed } from 'vue'
import {
  tutors, parents, students, subjects, studentSubjects,
  sessions, sessionBookings, sessionUpdates,
  assignments, assignmentSubmissions,
  learningProgress, studyTips, studyResources, teachingPlans,
  quizzes, quizAttempts, weeklySummaries,
  meetingRequests, messages, notifications,
  addMessage
} from '../data/parentMockData'

// Everything here is joined off session_id / student_id / subject_id / parent_id
// the way it would be if these came back from real API endpoints hitting the
// tables in the LearnAtHome Database Design doc.

export function useParentPortal(parentId) {
  const parent = computed(() => parents.find((p) => p.parent_id === parentId))

  const children = computed(() =>
    students
      .filter((s) => s.parent_id === parentId)
      .map((s) => ({
        ...s,
        subjects: studentSubjects
          .filter((ss) => ss.student_id === s.student_id)
          .map((ss) => subjects.find((sub) => sub.subject_id === ss.subject_id))
      }))
  )

  function subjectName(subjectId) {
    return subjects.find((s) => s.subject_id === subjectId)?.subject_name ?? 'Unknown Subject'
  }

  function tutorName(tutorId) {
    return tutors.find((t) => t.tutor_id === tutorId)?.tutor_name ?? 'Tutor'
  }

  function bookedSessionIds(studentId) {
    return sessionBookings
      .filter((b) => b.student_id === studentId && b.booking_status !== 'Cancelled')
      .map((b) => b.session_id)
  }

  function joinedSession(s) {
    return {
      ...s,
      subjectName: subjectName(s.subject_id),
      tutorName: tutorName(s.tutor_id)
    }
  }

  function upcomingSession(studentId) {
    return upcomingSessionsList(studentId)[0] || null
  }

  function upcomingSessionsList(studentId) {
    const ids = bookedSessionIds(studentId)
    return sessions
      .filter((s) => ids.includes(s.session_id) && s.status === 'Scheduled')
      .sort((a, b) => new Date(`${a.session_date}T${a.start_time}`) - new Date(`${b.session_date}T${b.start_time}`))
      .map(joinedSession)
  }

  function completedSessions(studentId) {
    const ids = bookedSessionIds(studentId)
    return sessions
      .filter((s) => ids.includes(s.session_id) && s.status === 'Completed')
      .sort((a, b) => new Date(b.session_date) - new Date(a.session_date))
      .map((s) => ({
        ...s,
        subjectName: subjectName(s.subject_id),
        tutorName: tutorName(s.tutor_id),
        update: sessionUpdates.find((u) => u.session_id === s.session_id) || null,
        progress: learningProgress.find((p) => p.session_id === s.session_id && p.student_id === studentId) || null,
        tips: studyTips.filter((t) => t.session_id === s.session_id && t.student_id === studentId),
        resources: studyResources.filter((r) => r.session_id === s.session_id)
      }))
  }

  function assignmentsFor(studentId) {
    const ids = bookedSessionIds(studentId)
    return assignments
      .filter((a) => ids.includes(a.session_id))
      .map((a) => ({
        ...a,
        sessionSubject: subjectName(sessions.find((s) => s.session_id === a.session_id)?.subject_id),
        submission: assignmentSubmissions.find((sub) => sub.assignment_id === a.assignment_id && sub.student_id === studentId) || null
      }))
      .sort((a, b) => new Date(a.due_date) - new Date(b.due_date))
  }

  function teachingPlanFor(studentId) {
    const child = children.value.find((c) => c.student_id === studentId)
    const subjectIds = (child?.subjects || []).map((s) => s.subject_id)
    return teachingPlans
      .filter((p) => subjectIds.includes(p.subject_id))
      .map((p) => ({ ...p, subjectName: subjectName(p.subject_id) }))
      .sort((a, b) => new Date(a.planned_date) - new Date(b.planned_date))
  }

  function quizTrend(studentId) {
    return quizAttempts
      .filter((a) => a.student_id === studentId)
      .map((a) => ({ ...a, quiz: quizzes.find((q) => q.quiz_id === a.quiz_id) }))
      .sort((a, b) => (a.quiz?.week_number ?? 0) - (b.quiz?.week_number ?? 0))
      .map((a) => ({ week: `Wk ${a.quiz?.week_number}`, score: a.score, subject: subjectName(a.quiz?.subject_id) }))
  }

  function quizHistory(studentId) {
    return quizAttempts
      .filter((a) => a.student_id === studentId)
      .map((a) => ({ ...a, quiz: quizzes.find((q) => q.quiz_id === a.quiz_id) }))
      .sort((a, b) => new Date(b.attempted_at) - new Date(a.attempted_at))
      .map((a) => ({
        attempt_id: a.attempt_id,
        title: a.quiz?.title,
        subjectName: subjectName(a.quiz?.subject_id),
        week_number: a.quiz?.week_number,
        score: a.score,
        attempted_at: a.attempted_at
      }))
  }

  function latestWeeklySummary(studentId) {
    return weeklySummaries
      .filter((w) => w.student_id === studentId)
      .sort((a, b) => new Date(b.week_end) - new Date(a.week_end))[0] || null
  }

  function weeklySummariesFor(studentId) {
    return weeklySummaries
      .filter((w) => w.student_id === studentId)
      .sort((a, b) => new Date(b.week_end) - new Date(a.week_end))
  }

  const parentMeetingRequests = computed(() =>
    meetingRequests
      .filter((m) => m.parent_id === parentId || children.value.some((c) => c.student_id === m.student_id))
      .sort((a, b) => new Date(a.meeting_date) - new Date(b.meeting_date))
  )

  const parentMessages = computed(() =>
    messages
      .filter(
        (m) =>
          (m.sender_type === 'Parent' && m.sender_id === parentId) ||
          (m.receiver_type === 'Parent' && m.receiver_id === parentId)
      )
      .sort((a, b) => new Date(b.sent_at) - new Date(a.sent_at))
  )

  const parentNotifications = computed(() =>
    notifications
      .filter((n) => n.recipient_type === 'Parent' && n.recipient_id === parentId)
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  )

  const unreadNotificationCount = computed(
    () => parentNotifications.value.filter((n) => !n.is_read).length
  )

  function markNotificationRead(notificationId) {
    const n = notifications.find((x) => x.notification_id === notificationId)
    if (n) n.is_read = true
  }

  function markAllNotificationsRead() {
    parentNotifications.value.forEach((n) => { n.is_read = true })
  }

  function sendMessageToTutor(subject, message) {
    addMessage({ subject, message })
  }

  function replyExistingMessage(messageId, text) {
    const msg = messages.find((m) => m.message_id === messageId)
    if (msg) {
      msg.reply_message = text
      msg.replied_at = new Date().toISOString()
    }
  }

  return {
    parent,
    children,
    upcomingSession,
    upcomingSessionsList,
    completedSessions,
    assignmentsFor,
    teachingPlanFor,
    quizTrend,
    quizHistory,
    latestWeeklySummary,
    weeklySummariesFor,
    parentMeetingRequests,
    parentMessages,
    parentNotifications,
    unreadNotificationCount,
    markNotificationRead,
    markAllNotificationsRead,
    sendMessageToTutor,
    replyExistingMessage
  }
}
