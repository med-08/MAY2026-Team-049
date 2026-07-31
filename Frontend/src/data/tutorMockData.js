export const tutorUser = {
  userId: 'user-tutor-001',
  tutorId: 'tutor-001',
  name: 'Anjali Mehta',
  displayName: 'Anjali',
  initials: 'AM',
  bio: 'Home tuition specialist focused on Maths and Physics foundations for Classes 9-11.',
  experience: '7 years',
  subjects: ['Mathematics', 'Physics', 'Algebra', 'Trigonometry'],
  education: 'M.Sc. Mathematics, B.Ed.',
  hourlyRate: '₹500/hr',
  availability: 'Mon-Sat · 4:00-8:00 PM',
  languages: ['English', 'Hindi', 'Tamil'],
  certificates: ['Advanced Pedagogy', 'Child Learning Psychology', 'STEM Mentor']
}

export const navGroups = [
  {
    label: 'Teaching',
    items: [
      { id: 'dashboard', label: 'Dashboard', icon: '<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/>' },
      { id: 'schedule', label: 'Schedule', icon: '<rect x="3" y="4.5" width="18" height="16" rx="2"/><path d="M3 9h18M8 2.5v4M16 2.5v4"/>' },
      { id: 'students', label: 'Students', icon: '<circle cx="9" cy="8" r="3.2"/><path d="M3.5 19c0-3 2.5-5 5.5-5s5.5 2 5.5 5"/><path d="M16 6.5a3 3 0 0 1 0 5.6M18 19c0-2-.7-3.4-2-4.4"/>' },
      { id: 'attendance', label: 'Attendance', icon: '<path d="M9 11.5 11 13.5l4-4.5"/><rect x="3.5" y="4" width="17" height="17" rx="2.5"/>' }
    ]
  },
  {
    label: 'Content',
    items: [
      { id: 'assignments', label: 'Assignments', icon: '<path d="M8 3h8l3 3v14a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z"/><path d="M9 12h6M9 16h4"/>' },
      { id: 'materials', label: 'Materials', icon: '<path d="M4 6a2 2 0 0 1 2-2h4l2 2h6a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2Z"/>' },
      { id: 'qa', label: 'Q&A board', icon: '<path d="M4 5h16v11H8l-4 3.5V5Z"/><path d="M12 8.5a1.6 1.6 0 0 1 1.6 1.6c0 1-1.6 1.2-1.6 2.4M12 14.6h.01"/>' }
    ]
  },
  {
    label: 'You',
    items: [
      { id: 'doubts', label: 'Doubts', icon: '<path d="M12 3a7 7 0 0 1 4 12.7V18H8v-2.3A7 7 0 0 1 12 3ZM9 21h6"/>', countKey: 'openDoubts' },
      { id: 'messages', label: 'Messages', icon: '<path d="M4 5h16v10H9l-5 4V5Z"/>', count: 2 },
      { id: 'earnings', label: 'Earnings', icon: '<path d="M4 19V5M4 18h16M8 15l3-4 3 2.5L20 7"/>' },
      { id: 'profile', label: 'Profile', icon: '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.5-7 8-7s8 3 8 7"/>' }
    ]
  }
]

export const viewTitles = {
  dashboard: { prefix: 'Good evening, ', highlight: 'Anjali' },
  schedule: { prefix: 'Your ', highlight: 'schedule' },
  students: { prefix: 'Your ', highlight: 'students' },
  attendance: { prefix: 'Take ', highlight: 'attendance' },
  assignments: { prefix: 'Assignments & ', highlight: 'quizzes' },
  materials: { prefix: 'Study ', highlight: 'materials' },
  qa: { prefix: 'Q&A ', highlight: 'board' },
  doubts: { prefix: 'Student ', highlight: 'doubts' },
  messages: { prefix: 'Your ', highlight: 'messages' },
  earnings: { prefix: 'Your ', highlight: 'earnings' },
  profile: { prefix: 'Tutor ', highlight: 'profile' }
}

export const todayOverview = [
  { id: 'doubts', label: 'Doubts requiring replies', value: 2, tone: 'coral', go: 'doubts' },
  { id: 'grading', label: 'Assignments pending grading', value: 5, tone: 'amber', go: 'assignments' },
  { id: 'classes', label: 'Classes scheduled today', value: 3, tone: 'lime', go: 'schedule' },
  { id: 'meeting', label: 'Parent meeting tomorrow', value: 1, tone: 'blue', go: 'messages' },
  { id: 'homework', label: 'Homework pending review', value: 4, tone: 'purple', go: 'assignments' }
]

export const recentActivities = [
  { activityId: 'act-001', title: 'Diya submitted assignment', meta: 'Maths · 6m ago', tone: 'var(--lime)' },
  { activityId: 'act-002', title: 'Kabir asked a doubt', meta: 'Physics · 8m ago', tone: 'var(--coral)' },
  { activityId: 'act-003', title: 'Attendance updated', meta: 'Class 10 · 35m ago', tone: 'var(--g2)' },
  { activityId: 'act-004', title: 'Material uploaded', meta: 'Quadratics notes · 1h ago', tone: 'var(--g1)' },
  { activityId: 'act-005', title: 'Parent meeting confirmed', meta: 'Aarav review · Tomorrow', tone: 'var(--amber)' },
  { activityId: 'act-006', title: 'Recent quiz graded', meta: 'Motion · 2h ago', tone: 'var(--lime)' }
]

export const upcomingDeadlines = [
  { deadlineId: 'dead-001', day: 'Tomorrow', title: 'Quiz', meta: 'Class 10 · Quadratics', badge: 'live' },
  { deadlineId: 'dead-002', day: 'Friday', title: 'Assignment Due', meta: 'Exercise 4.2', badge: 'warn' },
  { deadlineId: 'dead-003', day: 'Saturday', title: 'Meeting', meta: 'Student Review · 11:30 AM', badge: '' },
  { deadlineId: 'dead-004', day: 'Sunday', title: 'Progress Report', meta: 'Weekly summary', badge: 'done' }
]

export const aiSuggestions = [
  { suggestionId: 'ai-001', title: 'Kabir is struggling in Algebra.', action: 'Recommend extra practice worksheet.' },
  { suggestionId: 'ai-002', title: 'Diya has improved significantly.', action: 'Recommend advanced problems.' }
]

export const upcomingMeetings = [
  { meetingId: 'meet-001', day: 'Tomorrow', title: 'Parent Meeting', time: '11:30 AM', meta: 'Student Review' },
  { meetingId: 'meet-002', day: 'Saturday', title: 'Progress Check', time: '5:00 PM', meta: 'Aarav Sharma' }
]

export const leaderboard = [
  { rank: 1, studentId: 'student-001', name: 'Aarav Sharma', score: 92, trend: '+8%' },
  { rank: 2, studentId: 'student-002', name: 'Diya Rao', score: 86, trend: '+14%' },
  { rank: 3, studentId: 'student-003', name: 'Kabir Joshi', score: 72, trend: '+4%' }
]

export const achievements = [
  { achievementId: 'ach-001', studentId: 'student-001', label: 'Perfect Attendance' },
  { achievementId: 'ach-002', studentId: 'student-002', label: 'Most Improved' },
  { achievementId: 'ach-003', studentId: 'student-001', label: 'Top Quiz Performer' },
  { achievementId: 'ach-004', studentId: 'student-002', label: 'Homework Hero' },
  { achievementId: 'ach-005', studentId: 'student-003', label: 'Fast Learner' }
]

export const dashboardStats = [
  { id: 'classes', value: 3, label: 'Classes today', icon: '<rect x="3" y="4.5" width="18" height="16" rx="2"/><path d="M3 9h18"/>', spark: [40, 70, 55, 90] },
  { id: 'students', value: 18, label: 'Active students', icon: '<circle cx="9" cy="8" r="3"/><path d="M4 19c0-3 2-5 5-5s5 2 5 5"/>' },
  { id: 'grade', value: 5, label: 'To grade', icon: '<path d="M8 3h8l3 3v14H5V4Z"/><path d="M9 12h6"/>' },
  { id: 'unread', value: 2, label: 'Unread messages', icon: '<path d="M4 5h16v10H9l-5 4V5Z"/>' }
]

export const sessions = [
  { sessionId: 'sess-001', subject: 'Maths', classLevel: 'Class 9', time: '2:30', summary: '5 present · update sent', status: 'done', badge: 'Done' },
  { sessionId: 'sess-002', subject: 'Maths', classLevel: 'Class 10', time: '4:00', summary: '6 students · Aarav, Diya, +4', status: 'live', action: 'Start class' },
  { sessionId: 'sess-003', subject: 'Physics', classLevel: 'Class 10', time: '5:30', summary: '4 students', badge: 'In 90m' },
  { sessionId: 'sess-004', subject: 'One-on-one', classLevel: 'Aarav', time: '7:00', summary: 'Revision — quadratics', badge: 'Upcoming' }
]

export const scheduleRows = [
  { time: '4:00', days: [{ t: 'Maths', s: 'Cl 10 · 6' }, null, { t: 'Maths', s: 'Cl 9 · 5' }, null, { t: 'Maths', s: 'Cl 10 · 6' }, null] },
  { time: '5:30', days: [{ t: 'Physics', s: 'Cl 10 · 4' }, { t: 'Physics', s: 'Cl 9 · 3' }, null, { t: 'Physics', s: 'Cl 10 · 4' }, null, { t: 'Maths', s: 'Cl 9 · 5' }] },
  { time: '7:00', days: [{ t: '1-on-1', s: 'Aarav' }, null, null, { t: '1-on-1', s: 'Diya' }, null, null] }
]

export const students = [
  {
    studentId: 'student-001',
    userId: 'user-student-001',
    parentId: 'parent-001',
    name: 'Aarav Sharma',
    initials: 'AS',
    classLevel: 'Class 10',
    subjects: 'Maths, Physics',
    parent: { name: 'Mr. Sharma', phone: '+91 98765 12001', email: 'sharma.parent@example.com', preferredContact: 'WhatsApp' },
    weeklyScores: [64, 68, 73, 82],
    progress: { progressId: 'progress-001', completedTopics: 70, weeklyScore: 7, learningPace: 'Fast', tutorRemarks: 'Strong on algebra; revise trigonometry basics.', updatedAt: '2026-07-08' },
    gradient: 'linear-gradient(135deg,var(--g1),var(--g2))',
    accent: 'var(--g1)'
  },
  {
    studentId: 'student-002',
    userId: 'user-student-002',
    parentId: 'parent-002',
    name: 'Diya Rao',
    initials: 'DR',
    classLevel: 'Class 9',
    subjects: 'Physics',
    parent: { name: 'Mrs. Rao', phone: '+91 98765 12002', email: 'rao.parent@example.com', preferredContact: 'Email' },
    weeklyScores: [50, 58, 66, 78],
    progress: { progressId: 'progress-002', completedTopics: 55, weeklyScore: 6, learningPace: 'Average', tutorRemarks: 'Improving steadily; needs extra trigonometry practice.', updatedAt: '2026-07-08' },
    gradient: 'linear-gradient(135deg,var(--g2),var(--lime))',
    accent: 'var(--g2)'
  },
  {
    studentId: 'student-003',
    userId: 'user-student-003',
    parentId: 'parent-003',
    name: 'Kabir Joshi',
    initials: 'KJ',
    classLevel: 'Class 11',
    subjects: 'Maths',
    parent: { name: 'Mrs. Joshi', phone: '+91 98765 12003', email: 'joshi.parent@example.com', preferredContact: 'Phone' },
    weeklyScores: [38, 42, 48, 55],
    progress: { progressId: 'progress-003', completedTopics: 40, weeklyScore: 5, learningPace: 'Needs practice', tutorRemarks: 'Focus on foundations and weekly revision problems.', updatedAt: '2026-07-08' },
    gradient: 'linear-gradient(135deg,var(--coral),var(--g1))',
    accent: 'var(--coral)'
  }
]

export const sessionHistory = {
  'student-001': [
    { sessionHistoryId: 'sh-001', date: '8 Jul', topic: 'Quadratics', status: 'Attended', homework: 'Homework Submitted', badge: 'done' },
    { sessionHistoryId: 'sh-002', date: '6 Jul', topic: 'Algebra', status: 'Attended', homework: 'Homework Submitted', badge: 'done' },
    { sessionHistoryId: 'sh-003', date: '4 Jul', topic: 'Trigonometry', status: 'Late', homework: 'Homework Pending', badge: 'warn' },
    { sessionHistoryId: 'sh-004', date: '2 Jul', topic: 'Revision', status: 'Attended', homework: 'Homework Submitted', badge: 'done' },
    { sessionHistoryId: 'sh-005', date: '30 Jun', topic: 'Formulae', status: 'Missed', homework: 'Homework Pending', badge: 'warn' }
  ],
  'student-002': [
    { sessionHistoryId: 'sh-006', date: '8 Jul', topic: 'Motion', status: 'Attended', homework: 'Homework Submitted', badge: 'done' },
    { sessionHistoryId: 'sh-007', date: '5 Jul', topic: 'Forces', status: 'Attended', homework: 'Homework Pending', badge: 'warn' },
    { sessionHistoryId: 'sh-008', date: '3 Jul', topic: 'Practice', status: 'Late', homework: 'Homework Submitted', badge: '' }
  ],
  'student-003': [
    { sessionHistoryId: 'sh-009', date: '8 Jul', topic: 'Discriminant', status: 'Missed', homework: 'Homework Pending', badge: 'warn' },
    { sessionHistoryId: 'sh-010', date: '6 Jul', topic: 'Algebra', status: 'Attended', homework: 'Homework Submitted', badge: 'done' },
    { sessionHistoryId: 'sh-011', date: '4 Jul', topic: 'Basics', status: 'Late', homework: 'Homework Pending', badge: 'warn' }
  ]
}

export const calendarEvents = [
  { eventId: 'cal-001', date: '2026-07-10', title: 'Maths · Class 10', type: 'Class' },
  { eventId: 'cal-002', date: '2026-07-11', title: 'Parent Review', type: 'Meeting' },
  { eventId: 'cal-003', date: '2026-07-14', title: 'Unit Test', type: 'Exam' },
  { eventId: 'cal-004', date: '2026-07-18', title: 'Cancelled Physics', type: 'Cancelled Class' },
  { eventId: 'cal-005', date: '2026-07-20', title: 'Holiday', type: 'Holiday' },
  { eventId: 'cal-006', date: '2026-07-25', title: 'Doubt Clearing', type: 'Class' }
]

export const quizScores = {
  'student-001': [
    { quizId: 'quiz-001', studentId: 'student-001', sessionId: 'sess-002', title: 'Algebra', score: '8/10', feedback: 'Good accuracy', quizDate: '2026-07-02', badge: 'done' },
    { quizId: 'quiz-002', studentId: 'student-001', sessionId: 'sess-002', title: 'Quadratics', score: '7/10', feedback: 'Revise formulas', quizDate: '2026-07-04', badge: '' },
    { quizId: 'quiz-003', studentId: 'student-001', sessionId: 'sess-002', title: 'Trigonometry', score: '5/10', feedback: 'Needs practice', quizDate: '2026-07-07', badge: 'warn' }
  ],
  'student-002': [
    { quizId: 'quiz-004', studentId: 'student-002', sessionId: 'sess-003', title: 'Motion', score: '6/10', feedback: 'Steady', quizDate: '2026-07-05', badge: '' },
    { quizId: 'quiz-005', studentId: 'student-002', sessionId: 'sess-003', title: 'Trigonometry', score: '5/10', feedback: 'More practice', quizDate: '2026-07-07', badge: 'warn' }
  ],
  'student-003': [
    { quizId: 'quiz-006', studentId: 'student-003', sessionId: 'sess-004', title: 'Discriminant', score: '4/10', feedback: 'Revisit concept', quizDate: '2026-07-08', badge: 'warn' },
    { quizId: 'quiz-007', studentId: 'student-003', sessionId: 'sess-004', title: 'Algebra', score: '6/10', feedback: 'Improving', quizDate: '2026-07-06', badge: '' }
  ]
}

export const attendanceRecords = [
  { attendanceId: 'att-001', studentId: 'student-001', sessionId: 'sess-002', status: 'Present' },
  { attendanceId: 'att-002', studentId: 'student-002', sessionId: 'sess-002', status: 'Present' },
  { attendanceId: 'att-003', studentId: 'student-003', sessionId: 'sess-002', status: 'Absent' }
]

export const assignments = [
  { assignmentId: 'asg-001', title: 'Weekly quiz · Quadratics', classLevel: 'Class 10', submissions: '6 submissions', type: 'quiz', homeworkStatus: 'Submitted' },
  { assignmentId: 'asg-002', title: 'Assignment · Exercise 4.2', classLevel: 'Class 10', submissions: '5 submissions', type: 'assignment', homeworkStatus: 'Pending' },
  { assignmentId: 'asg-003', title: 'Weekly quiz · Motion', classLevel: 'Physics', submissions: '4 submissions', type: 'quiz', homeworkStatus: 'Late' },
  { assignmentId: 'asg-004', title: 'Worksheet · Algebra basics', classLevel: 'Class 9', submissions: '2 submissions', type: 'assignment', homeworkStatus: 'Missing' }
]

export const studyResources = [
  { resourceId: 'res-001', sessionId: 'sess-002', title: 'Quadratics — Notes.pdf', description: 'Maths · Class 10 · 2 Jul', resourceLink: '#', uploadedAt: '2026-07-02', icon: '<path d="M8 3h8l3 3v14H5V4Z"/>', gradient: 'linear-gradient(135deg,var(--g1),var(--g2))' },
  { resourceId: 'res-002', sessionId: 'sess-003', title: 'Motion — Walkthrough.mp4', description: 'Physics · Class 10 · 1 Jul', resourceLink: '#', uploadedAt: '2026-07-01', icon: '<path d="m9 8 7 4-7 4V8Z"/>', gradient: 'linear-gradient(135deg,var(--g2),var(--lime))' },
  { resourceId: 'res-003', sessionId: 'sess-001', title: 'Algebra — Puzzle set', description: 'Maths · Class 9 · 30 Jun', resourceLink: '#', uploadedAt: '2026-06-30', icon: '<path d="M4 6h16M4 12h16M4 18h10"/>', gradient: 'linear-gradient(135deg,var(--coral),var(--g1))' }
]

export const attendanceAnalytics = [
  { label: 'Present', value: 76, color: 'var(--lime)' },
  { label: 'Absent', value: 14, color: 'var(--coral)' },
  { label: 'Late', value: 10, color: 'var(--amber)' }
]

export const faqEntriesSeed = [
  { faqId: 'faq-001', question: 'Why factor before using the formula?', answer: 'Factoring often gives a faster path when roots are simple.', createdBy: tutorUser.userId, meta: 'Answered · 24 students saw this' },
  { faqId: 'faq-002', question: 'How to check number of roots?', answer: 'Use the discriminant to identify real, equal, or imaginary roots.', createdBy: tutorUser.userId, meta: 'Answered · pinned' }
]

export const doubtsSeed = [
  { doubtId: 'doubt-001', studentId: 'student-003', subject: 'Physics', question: "Sir, I didn't understand the discriminant part.", askedAt: '8m ago', status: 'Open' },
  { doubtId: 'doubt-002', studentId: 'student-002', subject: 'Maths', question: 'Can I get more practice on trigonometry?', askedAt: '40m ago', status: 'Open' }
]

export const conversationsSeed = {
  rao: {
    id: 'rao',
    participantName: 'Mrs. Rao',
    subtitle: 'Parent · Diya',
    initials: 'SR',
    gradient: 'linear-gradient(135deg,var(--g1),var(--g2))',
    messages: [
      { messageId: 'msg-001', senderId: 'parent-002', receiverId: tutorUser.userId, message: 'Will there be extra classes before the test?', timestamp: '2026-07-08T10:00:00+05:30', status: 'read', w: 'them' },
      { messageId: 'msg-002', senderId: tutorUser.userId, receiverId: 'parent-002', message: 'Yes — added a revision slot Saturday 5:30 PM.', timestamp: '2026-07-08T10:05:00+05:30', status: 'sent', w: 'me' },
      { messageId: 'msg-003', senderId: 'parent-002', receiverId: tutorUser.userId, message: 'Thank you! Diya will join.', timestamp: '2026-07-08T10:08:00+05:30', status: 'read', w: 'them' }
    ]
  },
  sharma: {
    id: 'sharma',
    participantName: 'Mr. Sharma',
    subtitle: 'Parent · Aarav',
    initials: 'SS',
    gradient: 'linear-gradient(135deg,var(--g2),var(--lime))',
    messages: [
      { messageId: 'msg-004', senderId: 'parent-001', receiverId: tutorUser.userId, message: "Could you share today's notes?", timestamp: '2026-07-08T09:00:00+05:30', status: 'read', w: 'them' },
      { messageId: 'msg-005', senderId: tutorUser.userId, receiverId: 'parent-001', message: 'Just uploaded them under Materials.', timestamp: '2026-07-08T09:05:00+05:30', status: 'sent', w: 'me' }
    ]
  },
  kabir: {
    id: 'kabir',
    participantName: 'Kabir Joshi',
    subtitle: 'Student',
    initials: 'KJ',
    gradient: 'linear-gradient(135deg,var(--coral),var(--g1))',
    messages: [
      { messageId: 'msg-006', senderId: 'student-003', receiverId: tutorUser.userId, message: "Sir, I didn't understand the discriminant part.", timestamp: '2026-07-08T08:50:00+05:30', status: 'read', w: 'them' }
    ]
  }
}

export const notifications = [
  { notificationId: 'not-001', userId: tutorUser.userId, title: 'New doubt from Kabir', message: 'Physics · 8m ago', type: 'doubt', isRead: false, createdAt: '2026-07-08T08:52:00+05:30', go: 'doubts', color: 'var(--coral)' },
  { notificationId: 'not-002', userId: tutorUser.userId, title: 'Diya submitted the weekly quiz', message: 'Maths · 1h ago', type: 'quiz', isRead: false, createdAt: '2026-07-08T08:00:00+05:30', go: 'assignments', color: 'var(--g1)' },
  { notificationId: 'not-003', userId: tutorUser.userId, title: 'Mrs. Rao replied to you', message: 'Message · 2h ago', type: 'message', isRead: false, createdAt: '2026-07-08T07:00:00+05:30', go: 'messages', color: 'var(--lime)' }
]

export const earningsHistory = [
  { month: 'June 2026', sessions: 48, amount: '₹24,000', status: 'Paid' },
  { month: 'May 2026', sessions: 44, amount: '₹22,000', status: 'Paid' },
  { month: 'April 2026', sessions: 40, amount: '₹20,000', status: 'Paid' }
]

export const commandItems = [
  { l: 'Dashboard', v: 'dashboard' },
  { l: 'Schedule', v: 'schedule' },
  { l: 'Students', v: 'students' },
  { l: 'Attendance', v: 'attendance' },
  { l: 'Assignments & quizzes', v: 'assignments' },
  { l: 'Study materials', v: 'materials' },
  { l: 'Q&A board', v: 'qa' },
  { l: 'Doubts', v: 'doubts' },
  { l: 'Messages', v: 'messages' },
  { l: 'Earnings', v: 'earnings' },
  { l: 'Profile', v: 'profile' },
  { l: 'Toggle light / dark', a: 'theme' }
]
