import { createRouter, createWebHistory } from 'vue-router'


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



const routes = [


  // =====================
  // Public Routes
  // =====================


  {
    path: '/',
    name: 'landing',
    component: LandingPage,
    meta:{
      title:"LearnAtHome"
    }
  },



  {
    path:'/login',
    name:'login',
    component:LoginView,
    meta:{
      title:"Login"
    }
  },



  {
    path:'/register',
    name:'register',
    component:RegisterView,
    meta:{
      title:"Register"
    }
  },





  // =====================
  // Admin Panel
  // =====================


  {
    path:'/admin',

    component:AppLayout,

    children:[


      {
        path:'',
        name:'dashboard',
        component:Dashboard,
        meta:{
          title:'Dashboard'
        }
      },


      {
        path:'students',
        name:'students',
        component:Students,
        meta:{
          title:'Students'
        }
      },


      {
        path:'tutors',
        name:'tutors',
        component:Tutors,
        meta:{
          title:'Tutors'
        }
      },


      {
        path:'parents',
        name:'parents',
        component:Parents,
        meta:{
          title:'Parents'
        }
      },


      {
        path:'pending-approvals',
        name:'pending-approvals',
        component:PendingApprovals,
        meta:{
          title:'Pending Approvals'
        }
      },


      {
        path:'analytics',
        name:'analytics',
        component:Analytics,
        meta:{
          title:'Analytics'
        }
      },


      {
        path:'profile',
        name:'profile',
        component:AdminProfile,
        meta:{
          title:'Admin Profile'
        }
      }


    ]

  },


  // =====================
  // Student Panel
  // =====================


  {
    path:'/student',

    component:StudentLayout,

    children:[


      {
        path:'',
        redirect:'/student/dashboard'
      },


      {
        path:'dashboard',
        name:'student-dashboard',
        component:StudentDashboard,
        meta:{
          title:'Dashboard'
        }
      },


      {
        path:'sessions',
        name:'student-my-sessions',
        component:StudentMySessions,
        meta:{
          title:'My Sessions'
        }
      },


      {
        path:'booking',
        name:'student-session-booking',
        component:StudentSessionBooking,
        meta:{
          title:'Session Booking'
        }
      },


      {
        path:'timetable',
        name:'student-timetable',
        component:StudentTimetable,
        meta:{
          title:'Timetable'
        }
      },


      {
        path:'quiz',
        name:'student-weekly-quiz',
        component:StudentWeeklyQuiz,
        meta:{
          title:'Weekly Quiz'
        }
      },


      {
        path:'quiz/:id',
        name:'student-quiz-attempt',
        component:StudentQuizAttempt,
        meta:{
          title:'Take Quiz'
        }
      },


      {
        path:'assignments',
        name:'student-assignments',
        component:StudentAssignments,
        meta:{
          title:'Interactive Assignments'
        }
      },


      {
        path:'homework',
        name:'student-homework',
        component:StudentHomework,
        meta:{
          title:'Homework'
        }
      },


      {
        path:'resources',
        name:'student-study-resources',
        component:StudentStudyResources,
        meta:{
          title:'Study Resources'
        }
      },


      {
        path:'study-tips',
        name:'student-study-tips',
        component:StudentStudyTips,
        meta:{
          title:'Study Tips'
        }
      },


      {
        path:'faq',
        name:'student-faq',
        component:StudentFAQ,
        meta:{
          title:'FAQ'
        }
      },


      {
        path:'profile',
        name:'student-profile',
        component:StudentProfile,
        meta:{
          title:'Student Profile'
        }
      }


    ]

  },



  // =====================
  // Parent Panel
  // =====================


  {
    path:'/parent',

    component:ParentLayout,

    children:[


      {
        path:'',
        name:'parent-dashboard',
        component:ParentDashboard,
        meta:{
          title:'Dashboard'
        }
      },


      {
        path:'progress',
        name:'parent-progress',
        component:ParentProgress,
        meta:{
          title:'Child Progress'
        }
      },


      {
        path:'curriculum',
        name:'parent-curriculum',
        component:ParentCurriculum,
        meta:{
          title:'Curriculum Plan'
        }
      },


      {
        path:'schedule',
        name:'parent-schedule',
        component:ParentSchedule,
        meta:{
          title:'Schedule'
        }
      },


      {
        path:'messages',
        name:'parent-messages',
        component:ParentMessages,
        meta:{
          title:'Messages'
        }
      },


      {
        path:'meetings',
        name:'parent-meetings',
        component:ParentMeetings,
        meta:{
          title:'Meeting Requests'
        }
      },


      {
        path:'profile',
        name:'parent-profile',
        component:ParentProfile,
        meta:{
          title:'Parent Profile'
        }
      }


    ]

  },




  // Catch Unknown Routes

  {
    path:'/:pathMatch(.*)*',
    redirect:'/'
  }


]




const router = createRouter({

  history:createWebHistory(),

  routes,


  scrollBehavior(){

    return {
      top:0
    }

  }

})



export default router