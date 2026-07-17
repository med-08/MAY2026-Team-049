// Mock relational data store.
// Table shapes below are taken directly from the finalized
// "LearnAtHome Database Design" doc (Team-049) — Roles, Tutor, Parent, Student,
// Subject, StudentSubject, Session, SessionUpdate, Assignment, AssignmentSubmission,
// LearningProgress, StudyTip, StudyResource, TeachingPlan, Quiz, QuizAttempt,
// WeeklySummary, SessionBooking, MeetingRequest, Message, Notification.
// The older "rough schema" draft (topic_name on LearningProgress, quizzes keyed to
// session_id, sessions keyed directly to student_id, etc.) is NOT used here.

import { reactive } from 'vue'

// ---------------------------------------------------------------------------
// Table 3.1 Roles / 3.3 Tutor / 3.4 Parent / 3.5 Student
// ---------------------------------------------------------------------------
export const roles = reactive([
  { role_id: 1, role_name: 'Admin' },
  { role_id: 2, role_name: 'Tutor' },
  { role_id: 3, role_name: 'Parent' },
  { role_id: 4, role_name: 'Student' }
])

export const tutors = reactive([
  {
    tutor_id: 1,
    role_id: 2,
    tutor_name: 'Dr. Sarah Bennett',
    email: 'sarah.bennett@learnathome.com',
    phone_no: '+1 202 555 0134',
    experience_years: 8
  }
])

export const parents = reactive([
  {
    parent_id: 1,
    role_id: 3,
    parent_name: 'Rajesh Mehta',
    email: 'rajesh.mehta@parentmail.com',
    phone_no: '+1 201 555 3849'
  }
])

export const students = reactive([
  {
    student_id: 1,
    role_id: 4,
    parent_id: 1,
    student_name: 'Aarav Mehta',
    email: 'aarav.mehta@studentmail.com',
    school: 'Greenfield High School'
  },
  {
    student_id: 2,
    role_id: 4,
    parent_id: 1,
    student_name: 'Diya Mehta',
    email: 'diya.mehta@studentmail.com',
    school: 'Greenfield High School'
  }
])

// ---------------------------------------------------------------------------
// Table 4.1 Subject / 4.2 StudentSubject
// ---------------------------------------------------------------------------
export const subjects = reactive([
  { subject_id: 1, subject_name: 'Mathematics' },
  { subject_id: 2, subject_name: 'Science' },
  { subject_id: 3, subject_name: 'English' }
])

export const studentSubjects = reactive([
  { student_subject_id: 1, student_id: 1, subject_id: 1 },
  { student_subject_id: 2, student_id: 1, subject_id: 2 },
  { student_subject_id: 3, student_id: 2, subject_id: 3 }
])

// ---------------------------------------------------------------------------
// Table 4.3 Session / 4.4 SessionUpdate / 7.1 SessionBooking
// ---------------------------------------------------------------------------
export const sessions = reactive([
  { session_id: 1, tutor_id: 1, subject_id: 1, session_date: '2026-07-08', start_time: '17:00', end_time: '18:00', session_type: 'Regular', status: 'Completed' },
  { session_id: 2, tutor_id: 1, subject_id: 2, session_date: '2026-07-10', start_time: '17:00', end_time: '18:00', session_type: 'Regular', status: 'Completed' },
  { session_id: 3, tutor_id: 1, subject_id: 3, session_date: '2026-07-09', start_time: '16:00', end_time: '17:00', session_type: 'One-to-One', status: 'Completed' },
  { session_id: 4, tutor_id: 1, subject_id: 1, session_date: '2026-07-16', start_time: '17:00', end_time: '18:00', session_type: 'Regular', status: 'Scheduled' },
  { session_id: 5, tutor_id: 1, subject_id: 3, session_date: '2026-07-17', start_time: '16:00', end_time: '17:00', session_type: 'One-to-One', status: 'Scheduled' }
])

export const sessionBookings = reactive([
  { booking_id: 1, session_id: 1, student_id: 1, booking_date: '2026-07-01T10:00:00', booking_status: 'Confirmed' },
  { booking_id: 2, session_id: 2, student_id: 1, booking_date: '2026-07-01T10:02:00', booking_status: 'Confirmed' },
  { booking_id: 3, session_id: 3, student_id: 2, booking_date: '2026-07-01T10:05:00', booking_status: 'Confirmed' },
  { booking_id: 4, session_id: 4, student_id: 1, booking_date: '2026-07-10T09:00:00', booking_status: 'Confirmed' },
  { booking_id: 5, session_id: 5, student_id: 2, booking_date: '2026-07-10T09:04:00', booking_status: 'Confirmed' }
])

export const sessionUpdates = reactive([
  { update_id: 1, session_id: 1, topics_covered: 'Quadratic Equations \u2014 factorization method', homework_assigned: '2 worksheets on factorization', next_session_date: '2026-07-16', notification_time: '2026-07-08T18:20:00' },
  { update_id: 2, session_id: 2, topics_covered: 'Chemical Bonding \u2014 ionic vs covalent', homework_assigned: 'Lab-note assignment on bonding types', next_session_date: '2026-07-16', notification_time: '2026-07-10T18:25:00' },
  { update_id: 3, session_id: 3, topics_covered: 'Poetry Analysis \u2014 imagery & metaphor', homework_assigned: 'Poem analysis worksheet', next_session_date: '2026-07-17', notification_time: '2026-07-09T17:15:00' }
])

// ---------------------------------------------------------------------------
// Table 5.1 Assignment / 5.2 AssignmentSubmission
// ---------------------------------------------------------------------------
export const assignments = reactive([
  { assignment_id: 1, session_id: 1, title: 'Factorization Practice Set', description: '10 quadratic factorization problems', due_date: '2026-07-14' },
  { assignment_id: 2, session_id: 2, title: 'Bonding Types Worksheet', description: 'Classify 15 compounds as ionic or covalent', due_date: '2026-07-15' },
  { assignment_id: 3, session_id: 3, title: 'Poem Analysis Draft', description: 'Analyze imagery in the assigned poem', due_date: '2026-07-14' }
])

export const assignmentSubmissions = reactive([
  { submission_id: 1, assignment_id: 1, student_id: 1, submission_date: '2026-07-13T19:00:00', status: 'Submitted', tutor_feedback: 'Good work, minor sign errors in Q7 and Q9.' },
  { submission_id: 2, assignment_id: 2, student_id: 1, submission_date: null, status: 'Pending', tutor_feedback: null },
  { submission_id: 3, assignment_id: 3, student_id: 2, submission_date: '2026-07-13T20:30:00', status: 'Late', tutor_feedback: 'Submitted a day late but solid analysis of imagery.' }
])

// ---------------------------------------------------------------------------
// Table 5.3 LearningProgress (per session, per student — no topic-level column
// in the finalized design; the tutor's remarks capture topic-specific notes)
// ---------------------------------------------------------------------------
export const learningProgress = reactive([
  { progress_id: 1, session_id: 1, student_id: 1, session_completion_status: 'Completed', learning_pace: 'Fast', tutor_remarks: 'Grasped factorization quickly, ready to move to coordinate geometry.' },
  { progress_id: 2, session_id: 2, student_id: 1, session_completion_status: 'Partially Completed', learning_pace: 'Needs Practice', tutor_remarks: 'Struggling with ionic vs covalent bonds, revisiting next session.' },
  { progress_id: 3, session_id: 3, student_id: 2, session_completion_status: 'Completed', learning_pace: 'Fast', tutor_remarks: 'Excellent grasp of literary devices, encourage independent reading.' }
])

// ---------------------------------------------------------------------------
// Table 5.4 StudyTip / 5.5 StudyResource / 5.6 TeachingPlan
// ---------------------------------------------------------------------------
export const studyTips = reactive([
  { tip_id: 1, session_id: 1, student_id: 1, tip_text: 'Try the "box method" for factorizing longer quadratics \u2014 it reduces sign errors.', created_at: '2026-07-08T19:00:00' },
  { tip_id: 2, session_id: 2, student_id: 1, tip_text: 'Make a two-column chart of ionic vs covalent examples and review it for 5 minutes daily.', created_at: '2026-07-10T19:00:00' },
  { tip_id: 3, session_id: 3, student_id: 2, tip_text: 'Underline imagery-related words first before analyzing tone \u2014 speeds up the whole process.', created_at: '2026-07-09T18:00:00' }
])

export const studyResources = reactive([
  { resource_id: 1, session_id: 1, resource_title: 'Factorization Method Walkthrough', resource_type: 'Video', resource_link: 'https://resources.learnathome.com/math/factorization-walkthrough' },
  { resource_id: 2, session_id: 2, resource_title: 'Ionic vs Covalent Bonds \u2014 Notes', resource_type: 'PDF', resource_link: 'https://resources.learnathome.com/science/bonding-notes.pdf' },
  { resource_id: 3, session_id: 3, resource_title: 'Imagery & Metaphor Practice Sheet', resource_type: 'Practice Sheet', resource_link: 'https://resources.learnathome.com/english/imagery-practice' }
])

export const teachingPlans = reactive([
  { plan_id: 1, tutor_id: 1, subject_id: 1, month: 'July 2026', topic_name: 'Coordinate Geometry', planned_date: '2026-07-20' },
  { plan_id: 2, tutor_id: 1, subject_id: 2, month: 'July 2026', topic_name: 'States of Matter', planned_date: '2026-07-23' },
  { plan_id: 3, tutor_id: 1, subject_id: 1, month: 'August 2026', topic_name: 'Probability', planned_date: '2026-08-04' },
  { plan_id: 4, tutor_id: 1, subject_id: 3, month: 'July 2026', topic_name: 'Narrative Writing', planned_date: '2026-07-21' },
  { plan_id: 5, tutor_id: 1, subject_id: 3, month: 'August 2026', topic_name: 'Comprehension Techniques', planned_date: '2026-08-05' }
])

// ---------------------------------------------------------------------------
// Table 6.1 Quiz / 6.3 QuizAttempt / 6.4 WeeklySummary
// ---------------------------------------------------------------------------
export const quizzes = reactive([
  { quiz_id: 1, tutor_id: 1, subject_id: 1, title: 'Algebra Weekly Quiz 1', week_number: 1, created_at: '2026-06-08T09:00:00' },
  { quiz_id: 2, tutor_id: 1, subject_id: 1, title: 'Algebra Weekly Quiz 2', week_number: 2, created_at: '2026-06-15T09:00:00' },
  { quiz_id: 3, tutor_id: 1, subject_id: 1, title: 'Algebra Weekly Quiz 3', week_number: 3, created_at: '2026-06-22T09:00:00' },
  { quiz_id: 4, tutor_id: 1, subject_id: 1, title: 'Algebra Weekly Quiz 4', week_number: 4, created_at: '2026-06-29T09:00:00' },
  { quiz_id: 5, tutor_id: 1, subject_id: 1, title: 'Algebra Weekly Quiz 5', week_number: 5, created_at: '2026-07-06T09:00:00' },
  { quiz_id: 6, tutor_id: 1, subject_id: 1, title: 'Algebra Weekly Quiz 6', week_number: 6, created_at: '2026-07-13T09:00:00' },
  { quiz_id: 7, tutor_id: 1, subject_id: 3, title: 'English Weekly Quiz 1', week_number: 1, created_at: '2026-06-08T09:00:00' },
  { quiz_id: 8, tutor_id: 1, subject_id: 3, title: 'English Weekly Quiz 2', week_number: 2, created_at: '2026-06-15T09:00:00' },
  { quiz_id: 9, tutor_id: 1, subject_id: 3, title: 'English Weekly Quiz 3', week_number: 3, created_at: '2026-06-22T09:00:00' },
  { quiz_id: 10, tutor_id: 1, subject_id: 3, title: 'English Weekly Quiz 4', week_number: 4, created_at: '2026-06-29T09:00:00' },
  { quiz_id: 11, tutor_id: 1, subject_id: 3, title: 'English Weekly Quiz 5', week_number: 5, created_at: '2026-07-06T09:00:00' },
  { quiz_id: 12, tutor_id: 1, subject_id: 3, title: 'English Weekly Quiz 6', week_number: 6, created_at: '2026-07-13T09:00:00' }
])

export const quizAttempts = reactive([
  { attempt_id: 1, quiz_id: 1, student_id: 1, score: 62, attempted_at: '2026-06-09T18:00:00' },
  { attempt_id: 2, quiz_id: 2, student_id: 1, score: 68, attempted_at: '2026-06-16T18:00:00' },
  { attempt_id: 3, quiz_id: 3, student_id: 1, score: 74, attempted_at: '2026-06-23T18:00:00' },
  { attempt_id: 4, quiz_id: 4, student_id: 1, score: 71, attempted_at: '2026-06-30T18:00:00' },
  { attempt_id: 5, quiz_id: 5, student_id: 1, score: 82, attempted_at: '2026-07-07T18:00:00' },
  { attempt_id: 6, quiz_id: 6, student_id: 1, score: 88, attempted_at: '2026-07-14T18:00:00' },
  { attempt_id: 7, quiz_id: 7, student_id: 2, score: 70, attempted_at: '2026-06-09T18:00:00' },
  { attempt_id: 8, quiz_id: 8, student_id: 2, score: 75, attempted_at: '2026-06-16T18:00:00' },
  { attempt_id: 9, quiz_id: 9, student_id: 2, score: 73, attempted_at: '2026-06-23T18:00:00' },
  { attempt_id: 10, quiz_id: 10, student_id: 2, score: 80, attempted_at: '2026-06-30T18:00:00' },
  { attempt_id: 11, quiz_id: 11, student_id: 2, score: 84, attempted_at: '2026-07-07T18:00:00' },
  { attempt_id: 12, quiz_id: 12, student_id: 2, score: 90, attempted_at: '2026-07-14T18:00:00' }
])

export const weeklySummaries = reactive([
  {
    summary_id: 1,
    tutor_id: 1,
    student_id: 1,
    week_start: '2026-07-06',
    week_end: '2026-07-12',
    topics_taught: 'Quadratic Equations, Chemical Bonding basics',
    homework_summary: '2 worksheets on factorization and 1 lab-note assignment on bonding types',
    areas_for_improvement: 'Needs more practice distinguishing ionic vs covalent bonds',
    created_at: '2026-07-12T20:00:00'
  },
  {
    summary_id: 2,
    tutor_id: 1,
    student_id: 2,
    week_start: '2026-07-06',
    week_end: '2026-07-12',
    topics_taught: 'Poetry Analysis (imagery & metaphor)',
    homework_summary: '1 poem analysis worksheet',
    areas_for_improvement: 'Focus on clearer thesis statements in written analysis',
    created_at: '2026-07-12T20:05:00'
  }
])

// ---------------------------------------------------------------------------
// Table 7.2 MeetingRequest
// ---------------------------------------------------------------------------
export const meetingRequests = reactive([
  {
    meeting_id: 1,
    tutor_id: 1,
    student_id: null,
    parent_id: 1,
    meeting_date: '2026-07-18T18:00:00',
    meeting_link: 'https://meet.learnathome.com/room/mehta-checkin',
    meeting_reason: "Discuss Aarav's Science performance",
    status: 'Scheduled'
  }
])

// ---------------------------------------------------------------------------
// Table 8.1 Message (sender/receiver identified by type + id, per design doc)
// ---------------------------------------------------------------------------
export const messages = reactive([
  {
    message_id: 1,
    sender_type: 'Parent',
    sender_id: 1,
    receiver_type: 'Tutor',
    receiver_id: 1,
    subject: "Aarav's progress in Science",
    message: 'Could you share how Aarav is doing with the chemical bonding topic? He mentioned finding it tricky.',
    reply_message: "He's a little behind on ionic vs covalent bonds \u2014 we're revisiting it in Thursday's session, should be sorted by next week.",
    sent_at: '2026-07-11T10:15:00',
    replied_at: '2026-07-11T14:02:00'
  },
  {
    message_id: 2,
    sender_type: 'Parent',
    sender_id: 1,
    receiver_type: 'Tutor',
    receiver_id: 1,
    subject: 'Fee receipt request',
    message: "Could you resend the receipt for last month's sessions?",
    reply_message: null,
    sent_at: '2026-07-13T09:30:00',
    replied_at: null
  }
])

// ---------------------------------------------------------------------------
// Table 8.3 Notification (recipient identified by type + id)
// ---------------------------------------------------------------------------
export const notifications = reactive([
  { notification_id: 1, recipient_type: 'Parent', recipient_id: 1, title: 'Session update shared', message: "Topics covered and homework for Aarav's Mathematics session are ready.", notification_type: 'Session Update', is_read: false, created_at: '2026-07-08T19:05:00' },
  { notification_id: 2, recipient_type: 'Parent', recipient_id: 1, title: 'Weekly summary available', message: "Diya's weekly summary for Jul 6\u201312 has been posted.", notification_type: 'Weekly Summary', is_read: false, created_at: '2026-07-12T20:10:00' },
  { notification_id: 3, recipient_type: 'Parent', recipient_id: 1, title: 'Upcoming session reminder', message: 'Aarav has a Mathematics session tomorrow at 5:00 PM.', notification_type: 'Reminder', is_read: true, created_at: '2026-07-15T09:00:00' }
])

let messageSeq = messages.length + 1
export function addMessage({ subject, message }) {
  messages.unshift({
    message_id: messageSeq++,
    sender_type: 'Parent',
    sender_id: 1,
    receiver_type: 'Tutor',
    receiver_id: 1,
    subject,
    message,
    reply_message: null,
    sent_at: new Date().toISOString(),
    replied_at: null
  })
}
