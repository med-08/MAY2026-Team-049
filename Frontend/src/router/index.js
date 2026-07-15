import { createRouter, createWebHistory } from 'vue-router'


// Public Pages
import LandingPage from '../views/LandingPage.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'


// Admin Layout
import AppLayout from '../components/layout/AppLayout.vue'


// Admin Pages
import Dashboard from '../views/Dashboard.vue'
import Students from '../views/Students.vue'
import Tutors from '../views/Tutors.vue'
import Parents from '../views/Parents.vue'
import PendingApprovals from '../views/PendingApprovals.vue'
import Analytics from '../views/Analytics.vue'
import AdminProfile from '../views/AdminProfile.vue'



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