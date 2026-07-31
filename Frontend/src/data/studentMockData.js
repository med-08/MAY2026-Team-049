// Central mock data store for LearnAtHome. No backend — everything here is static sample data.

export const student = {
  name: "Ananya Rao",
  email: "ananya.rao@example.com",
  school: "Greenfield Public School",
  subjects: ["Mathematics", "Science", "English"],
  parentName: "Sunil Rao",
  initials: "AR",
}

export const tutors = [
  { id: "t1", name: "Mrs. Kavitha Iyer", subject: "Mathematics, Science & English", initials: "KI" },
]

export const summaryStats = [
  { key: "upcoming", label: "Upcoming Sessions", value: 4, subtitle: "Next 7 days", icon: "CalendarDaysIcon", tone: "blue" },
  { key: "completed", label: "Completed Sessions", value: 28, subtitle: "This term", icon: "CheckCircleIcon", tone: "green" },
  { key: "quizAvg", label: "Quiz Average", value: "82%", subtitle: "Last 6 weeks", icon: "ChartBarIcon", tone: "green" },
  { key: "homework", label: "Homework Pending", value: 2, subtitle: "1 overdue", icon: "ClipboardDocumentListIcon", tone: "amber" },
]

export const weeklyQuizProgress = {
  labels: ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5", "Week 6"],
  data: [62, 68, 71, 75, 79, 82],
}

export const subjectQuizScores = {
  labels: ["Mathematics", "Science", "English"],
  data: [78, 85, 88],
}

export const nextSession = {
  subject: "Mathematics",
  tutor: "Mrs. Kavitha Iyer",
  type: "One-to-One",
  date: "Today, 14 July 2026",
  time: "5:00 PM",
  duration: "60 minutes",
  topics: ["Quadratic Equations", "Factorisation Methods"],
  status: "Upcoming",
}

export const todaysTasks = [
  { id: "tt1", subject: "Mathematics", task: "Assignment: Quadratic Equations Practice Set", time: "Due Today, 8:00 PM", status: "Pending" },
  { id: "tt2", subject: "Science", task: "Homework: Chapter 4 — Force & Motion Questions", time: "Due Today, 6:00 PM", status: "Pending" },
  { id: "tt3", subject: "Mathematics", task: "One-to-One Tuition Session", time: "Today at 5:00 PM", status: "Upcoming" },
]

export const sessions = {
  upcoming: [
    { id: "s1", subject: "Mathematics", tutor: "Mrs. Kavitha Iyer", type: "One-to-One", date: "14 Jul 2026", time: "5:00 PM", duration: "60 min", status: "Upcoming" },
    { id: "s2", subject: "Science", tutor: "Mrs. Kavitha Iyer", type: "Regular", date: "15 Jul 2026", time: "4:00 PM", duration: "45 min", status: "Upcoming" },
    { id: "s3", subject: "English", tutor: "Mrs. Kavitha Iyer", type: "Regular", date: "16 Jul 2026", time: "5:30 PM", duration: "45 min", status: "Upcoming" },
  ],
  completed: [
    { id: "s5", subject: "Mathematics", tutor: "Mrs. Kavitha Iyer", type: "One-to-One", date: "11 Jul 2026", time: "5:00 PM", duration: "60 min", topics: "Linear Equations, Word Problems", status: "Completed" },
    { id: "s6", subject: "Science", tutor: "Mrs. Kavitha Iyer", type: "Regular", date: "10 Jul 2026", time: "4:00 PM", duration: "45 min", topics: "Newton's Laws of Motion", status: "Completed" },
    { id: "s7", subject: "English", tutor: "Mrs. Kavitha Iyer", type: "Regular", date: "9 Jul 2026", time: "5:30 PM", duration: "45 min", topics: "Active & Passive Voice", status: "Completed" },
  ],
}

export const bookingSlots = {
  regular: [
    { id: "b1", date: "17 Jul 2026", time: "4:00 PM", tutor: "Mrs. Kavitha Iyer", subject: "Science", seats: 3, booked: false },
    { id: "b2", date: "17 Jul 2026", time: "5:30 PM", tutor: "Mrs. Kavitha Iyer", subject: "English", seats: 0, booked: true },
    { id: "b4", date: "20 Jul 2026", time: "6:00 PM", tutor: "Mrs. Kavitha Iyer", subject: "Mathematics", seats: 2, booked: false },
  ],
  oneToOne: [
    { id: "b5", date: "18 Jul 2026", time: "5:00 PM", tutor: "Mrs. Kavitha Iyer", subject: "Mathematics", seats: 1, booked: false },
    { id: "b6", date: "19 Jul 2026", time: "6:00 PM", tutor: "Mrs. Kavitha Iyer", subject: "Science", seats: 0, booked: true },
    { id: "b7", date: "21 Jul 2026", time: "5:00 PM", tutor: "Mrs. Kavitha Iyer", subject: "English", seats: 1, booked: false },
  ],
}

export const timetable = {
  days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
  classes: {
    Monday: [{ subject: "Mathematics", time: "5:00 – 6:00 PM", tutor: "Mrs. Kavitha Iyer", color: "blue" }],
    Tuesday: [{ subject: "Science", time: "4:00 – 4:45 PM", tutor: "Mrs. Kavitha Iyer", color: "green" }],
    Wednesday: [{ subject: "English", time: "5:30 – 6:15 PM", tutor: "Mrs. Kavitha Iyer", color: "amber" }],
    Thursday: [],
    Friday: [],
    Saturday: [{ subject: "Mathematics", time: "10:00 – 11:00 AM", tutor: "Mrs. Kavitha Iyer", color: "blue" }],
    Sunday: [],
  },
}

export const weeklyQuizzes = [
  {
    quiz_id: 1,
    subject: "Mathematics",
    title: "Algebra and Linear Equations",
    weekNumber: 5,
    lastAttempt: "12 Jul 2026",
    score: 88
  },
  {
    quiz_id: 2,
    subject: "Science",
    title: "Human Digestive System",
    weekNumber: 5,
    lastAttempt: "10 Jul 2026",
    score: 81
  },
  {
    quiz_id: 3,
    subject: "English",
    title: "Grammar and Reading Comprehension",
    weekNumber: 5,
    lastAttempt: null,
    score: null
  }
]

export const quizQuestions = {
  1: [
    {
      id: 1,
      question: "Solve for x: 2x + 6 = 14",
      options: ["x = 3", "x = 4", "x = 8", "x = 10"],
      correctIndex: 1,
    },
    {
      id: 2,
      question: "Which of the following is a linear equation?",
      options: ["y = x^2 + 1", "y = 3x - 5", "y = 1/x", "y = sqrt(x)"],
      correctIndex: 1,
    },
  ],
  2: [
    {
      id: 1,
      question: "Which organ produces bile to help digest fats?",
      options: ["Stomach", "Liver", "Pancreas", "Small Intestine"],
      correctIndex: 1,
    },
    {
      id: 2,
      question: "Where does most nutrient absorption occur?",
      options: ["Esophagus", "Large Intestine", "Small Intestine", "Stomach"],
      correctIndex: 2,
    },
  ],
  3: [
    {
      id: 1,
      question: "Choose the correctly punctuated sentence.",
      options: [
        "Its a beautiful day outside.",
        "It's a beautiful day outside.",
        "Its' a beautiful day outside.",
        "It is' a beautiful day outside.",
      ],
      correctIndex: 1,
    },
    {
      id: 2,
      question: "Identify the noun in the sentence: 'The dog barked loudly.'",
      options: ["The", "Dog", "Barked", "Loudly"],
      correctIndex: 1,
    },
  ],
}

export const assignments = [
  {
    id: 1,
    title: "Fractions & Decimals",
    subject: "Mathematics",
    description: "Practice fractions, decimals, and simple word problems through interactive activities.",
    status: "In Progress",
    dueDate: "22 Jul 2026",
    estimatedTime: "20 mins",
    progress: 55,
    aiEnabled: true,
  },
  {
    id: 2,
    title: "Geometry Basics",
    subject: "Mathematics",
    description: "Identify shapes, angles, and solve basic geometry problems.",
    status: "Not Started",
    dueDate: "25 Jul 2026",
    estimatedTime: "25 mins",
    progress: 0,
    aiEnabled: true,
  },
  {
    id: 3,
    title: "Forces & Motion",
    subject: "Science",
    description: "Learn about force, motion, and their real-world applications.",
    status: "In Progress",
    dueDate: "24 Jul 2026",
    estimatedTime: "20 mins",
    progress: 40,
    aiEnabled: true,
  },
  {
    id: 4,
    title: "Living Organisms",
    subject: "Science",
    description: "Explore the characteristics and classification of living organisms.",
    status: "Completed",
    dueDate: "18 Jul 2026",
    estimatedTime: "15 mins",
    progress: 100,
    aiEnabled: false,
  },
  {
    id: 5,
    title: "Reading Comprehension",
    subject: "English",
    description: "Read a passage and answer interactive comprehension questions.",
    status: "Not Started",
    dueDate: "26 Jul 2026",
    estimatedTime: "20 mins",
    progress: 0,
    aiEnabled: true,
  },
  {
    id: 6,
    title: "Grammar Practice",
    subject: "English",
    description: "Improve grammar skills by identifying and correcting sentence errors.",
    status: "Completed",
    dueDate: "19 Jul 2026",
    estimatedTime: "15 mins",
    progress: 100,
    aiEnabled: false,
  },
];
 

export const homeworkList = [
  {
    assignmentId: 101,
    session: "Mathematics - Algebra",
    title: "Linear Equations Worksheet",
    description:
      "Solve the given linear equations and show all calculation steps.",
    dueDate: "20 Jul 2026",
    submissionDate: "",
    status: "Pending",
    feedback: ""
  },

  {
    assignmentId: 102,
    session: "Science - Physics",
    title: "Forces and Motion Activity",
    description:
      "Answer conceptual questions based on Newton's Laws discussed during class.",
    dueDate: "18 Jul 2026",
    submissionDate: "",
    status: "Late",
    feedback: ""
  },

  {
    assignmentId: 103,
    session: "English",
    title: "Essay Writing",
    description:
      "Write a 300-word essay on 'The Importance of Reading'.",
    dueDate: "15 Jul 2026",
    submissionDate: "15 Jul 2026",
    status: "Submitted",
    feedback:
      "Well-structured essay. Improve paragraph transitions and grammar."
  },

  {
    assignmentId: 104,
    session: "Mathematics - Geometry",
    title: "Triangles Practice",
    description:
      "Complete all questions related to triangle properties and congruence.",
    dueDate: "23 Jul 2026",
    submissionDate: "",
    status: "Pending",
    feedback: ""
  },

  {
    assignmentId: 105,
    session: "Science - Biology",
    title: "Plant Cell Diagram",
    description:
      "Draw and label a plant cell neatly with all major organelles.",
    dueDate: "24 Jul 2026",
    submissionDate: "",
    status: "Pending",
    feedback: ""
  },

  {
    assignmentId: 106,
    session: "English",
    title: "Grammar Practice",
    description:
      "Complete the worksheet on tenses and subject-verb agreement.",
    dueDate: "14 Jul 2026",
    submissionDate: "14 Jul 2026",
    status: "Submitted",
    feedback:
      "Excellent work. All answers are correct."
  }
]

export const studyResources = [
  {
    resource_id: 1,
    session_id: 1,
    resource_title: "Algebra Basics Notes",
    resource_type: "PDF",
    resource_link: "#",
  },
  {
    resource_id: 2,
    session_id: 1,
    resource_title: "Linear Equations Practice Sheet",
    resource_type: "Practice Sheet",
    resource_link: "#",
  },
  {
    resource_id: 3,
    session_id: 2,
    resource_title: "Introduction to Fractions",
    resource_type: "Video",
    resource_link: "#",
  },
  {
    resource_id: 4,
    session_id: 2,
    resource_title: "Fractions Reference Notes",
    resource_type: "Notes",
    resource_link: "#",
  },
  {
    resource_id: 5,
    session_id: 3,
    resource_title: "Decimals Interactive Website",
    resource_type: "Website",
    resource_link: "#",
  },
  {
    resource_id: 6,
    session_id: 4,
    resource_title: "Geometry Formula Sheet",
    resource_type: "PDF",
    resource_link: "#",
  },
]

export const studyTips = [
  { id: "st1", subject: "Mathematics", tip: "Practice Algebra for 20 minutes daily to build calculation speed." },
  { id: "st2", subject: "Science", tip: "Revise last week's Science concepts before Tuesday's session." },
  { id: "st3", subject: "English", tip: "Improve Grammar before the next quiz — focus on tenses." },
  { id: "st4", subject: "Mathematics", tip: "Solve 5 extra Mathematics problems from the practice worksheet pack." },
]

export const faqs = [
  { id: "f1", q: "How do I book a tuition session?", a: "Go to Session Booking, choose Regular or One-to-One, and tap Book Slot on any available slot." },
  { id: "f2", q: "How do I reschedule a booked session?", a: "On Session Booking, open your booked slot and tap Reschedule — this is only available when another slot is open." },
  { id: "f3", q: "How are weekly quizzes conducted?", a: "Quizzes are subject-wise, contain 5 questions, and are based on the previous week's topics." },
  { id: "f4", q: "Where can I access study resources?", a: "All notes, worksheets, question banks, reference books, and videos are available on the Study Resources page." },
  { id: "f5", q: "How do I mark homework as completed?", a: "Open the Homework page and tap Mark as Completed next to the relevant item." },
  { id: "f6", q: "How are assignments evaluated?", a: "Your tutor reviews each assignment during your next session and shares feedback in person." },
  { id: "f7", q: "What happens if I miss a tuition session?", a: "Contact your tutor or the LearnAtHome administrator to arrange a makeup session where possible." },
  { id: "f8", q: "How do I contact the LearnAtHome administrator?", a: "Reach out via the email address listed on your Profile page." },
]
