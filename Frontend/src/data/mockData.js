import { reactive } from 'vue'

export const subjects = ['Mathematics', 'Science', 'English']

const schools = [
  'Greenfield High School',
  'Riverside International School',
  'Maple Grove Academy',
  'Sunrise Public School',
  'Oakwood Secondary School',
  'Bluebell Global School'
]

const studentNames = [
  'Aarav Mehta', 'Isha Kapoor', 'Liam Johnson', 'Sofia Rossi', 'Noah Williams',
  'Ananya Rao', 'Ethan Brown', 'Maya Fernandes', 'Lucas Silva', 'Priya Nair',
  'Oliver Smith', 'Zara Khan', 'Daniel Kim', 'Emma Davis', 'Rohan Verma'
]

const parentFirstNames = [
  'Rajesh', 'Sunita', 'Michael', 'Elena', 'David', 'Kavita', 'James', 'Fatima',
  'Carlos', 'Meera', 'Robert', 'Aisha', 'Thomas', 'Laura', 'Vikram', 'Grace',
  'Peter', 'Nadia', 'Samuel', 'Ritu', 'Henry', 'Chloe', 'Arjun', 'Olivia', 'Marcus'
]

const parentLastNames = [
  'Mehta', 'Kapoor', 'Johnson', 'Rossi', 'Williams', 'Rao', 'Brown', 'Fernandes',
  'Silva', 'Nair', 'Smith', 'Khan', 'Kim', 'Davis', 'Verma', 'Adams', 'Clark',
  'Hussain', 'Diaz', 'Sharma', 'Bennett', 'Foster', 'Malhotra', 'Reed', 'Cole'
]

function emailFrom(name, domain = 'mail.com') {
  return name.toLowerCase().replace(/[^a-z\s]/g, '').trim().replace(/\s+/g, '.') + '@' + domain
}

function phoneNumber(seed) {
  return `+1 (${String(200 + (seed % 7)).padStart(3, '0')}) 555-${String(1000 + seed * 37).slice(-4)}`
}

export const students = reactive(
  studentNames.map((name, i) => {
    const subject = subjects[i % subjects.length]
    const parentIndex = i
    return {
      id: `STU-${1001 + i}`,
      name,
      email: emailFrom(name, 'learnmail.com'),
      school: schools[i % schools.length],
      subject,
      parentName: `${parentFirstNames[parentIndex]} ${parentLastNames[parentIndex]}`,
      status: [3, 7, 10, 13].includes(i) ? 'Blocked' : 'Active'
    }
  })
)

export const parents = reactive(
  Array.from({ length: 25 }, (_, i) => {
    const name = `${parentFirstNames[i]} ${parentLastNames[i]}`
    const linkedStudent = studentNames[i % studentNames.length]
    return {
      id: `PAR-${2001 + i}`,
      name,
      studentName: linkedStudent,
      email: emailFrom(name, 'parentmail.com'),
      phone: phoneNumber(i + 5),
      status: [4, 12, 19].includes(i) ? 'Blocked' : 'Active'
    }
  })
)

export const tutors = reactive([
  {
    id: 'TUT-3001',
    name: 'Dr. Sarah Bennett',
    email: 'sarah.bennett@tutormail.com',
    experience: '8 years',
    phone: phoneNumber(21),
    subjects: ['Mathematics', 'Science']
  }
])

export const pendingApprovals = reactive([
  { id: 'APR-4001', name: 'Nathan Cole', email: 'nathan.cole@mail.com', role: 'Tutor', registrationDate: '2026-06-28', status: 'Pending' },
  { id: 'APR-4002', name: 'Priyanka Iyer', email: 'priyanka.iyer@mail.com', role: 'Parent', registrationDate: '2026-06-30', status: 'Pending' },
  { id: 'APR-4003', name: 'Jack Turner', email: 'jack.turner@mail.com', role: 'Student', registrationDate: '2026-07-01', status: 'Pending' },
  { id: 'APR-4004', name: 'Divya Menon', email: 'divya.menon@mail.com', role: 'Tutor', registrationDate: '2026-07-02', status: 'Pending' },
  { id: 'APR-4005', name: 'Ryan Walsh', email: 'ryan.walsh@mail.com', role: 'Parent', registrationDate: '2026-07-04', status: 'Pending' },
  { id: 'APR-4006', name: 'Ava Mitchell', email: 'ava.mitchell@mail.com', role: 'Student', registrationDate: '2026-07-06', status: 'Pending' },
  { id: 'APR-4007', name: 'Karan Chopra', email: 'karan.chopra@mail.com', role: 'Tutor', registrationDate: '2026-07-08', status: 'Pending' }
])

export const monthlyRegistrations = [
  { month: 'Jan', count: 6 }, { month: 'Feb', count: 9 }, { month: 'Mar', count: 7 },
  { month: 'Apr', count: 12 }, { month: 'May', count: 10 }, { month: 'Jun', count: 15 },
  { month: 'Jul', count: 8 }
]

export const adminProfile = reactive({
  name: 'Admin User',
  email: 'admin@learnathome.com',
  role: 'Super Administrator',
  lastLoggedIn: '10 Jul 2026, 9:14 AM'
})

export function studentsPerSubject() {
  return subjects.map((s) => ({
    subject: s,
    count: students.filter((st) => st.subject === s).length
  }))
}
