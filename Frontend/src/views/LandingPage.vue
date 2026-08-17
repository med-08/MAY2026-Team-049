<template>
  <div
    class="relative min-h-screen overflow-x-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950 transition-colors duration-500"
  >
    <!-- ================= BACKGROUND BLOBS ================= -->

    <div class="absolute inset-0 overflow-hidden pointer-events-none">

      <div
        class="absolute -top-32 -left-24 w-[420px] h-[420px] rounded-full bg-emerald-400/20 dark:bg-emerald-400/10 blur-[140px] animate-blob">
      </div>

      <div
        class="absolute top-32 right-0 w-[500px] h-[500px] rounded-full bg-blue-400/20 dark:bg-blue-400/10 blur-[160px] animate-blob animation-delay-2">
      </div>

      <div
        class="absolute bottom-0 left-1/3 w-[400px] h-[400px] rounded-full bg-purple-400/20 dark:bg-purple-400/10 blur-[150px] animate-blob animation-delay-4">
      </div>

    </div>

    <!-- ================= NAVBAR ================= -->

   <nav
        :class="[
        'fixed top-0 left-0 right-0 z-50 transition-all duration-300 backdrop-blur-xl',
        navbarShadow
        ? 'bg-white/90 dark:bg-slate-900/90 shadow-xl'
        : 'bg-white/60 dark:bg-slate-900/60'
        ]">

      <div
        class="max-w-7xl mx-auto h-20 px-6 lg:px-10 flex items-center justify-between">

        <!-- Logo -->

        <router-link
          to="/"
          class="flex items-center gap-4">

          <div
            class="w-12 h-12 rounded-xl bg-gradient-to-r from-emerald-500 via-blue-500 to-purple-500 flex items-center justify-center shadow-xl text-white text-2xl">

            🎓

          </div>

          <div>

            <h1
              class="text-2xl font-extrabold text-slate-900 dark:text-white">

              LearnAtHome

            </h1>

            <p
              class="text-xs text-slate-500 dark:text-slate-400">

              Coaching Management Platform

            </p>

          </div>

        </router-link>

        <!-- Desktop Menu -->

        <div
          class="hidden lg:flex items-center gap-8 text-slate-700 dark:text-slate-200 font-medium">

          <a href="#about" class="hover:text-emerald-500 dark:hover:text-emerald-400 transition">
            About
          </a>

          <a href="#features" class="hover:text-emerald-500 dark:hover:text-emerald-400 transition">
            Features
          </a>

          <a href="#roles" class="hover:text-emerald-500 dark:hover:text-emerald-400 transition">
            Roles
          </a>

          <a href="#workflow" class="hover:text-emerald-500 dark:hover:text-emerald-400 transition">
            How It Works
          </a>

        </div>

        <!-- Right Buttons -->

        <div class="flex items-center gap-4">

          <!-- Dark Mode Toggle Button -->
          <button
            @click="toggleDarkMode"
            class="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-yellow-400 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors duration-300"
            :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
          >
            <span v-if="!isDarkMode" class="text-xl">🌙</span>
            <span v-else class="text-xl">☀️</span>
          </button>

          <router-link
            to="/login"
            class="hidden sm:block px-5 py-2 rounded-xl border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition">

            Login

          </router-link>

          <router-link
            to="/register"
            class="px-6 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-blue-500 text-white shadow-xl hover:scale-105 transition duration-300">

            Register

          </router-link>

        </div>

      </div>

    </nav>

    <!-- ================= HERO ================= -->

    <section
      class="relative z-10 pt-40 pb-28">

      <div
        class="max-w-7xl mx-auto px-6 lg:px-10 grid lg:grid-cols-2 gap-16 items-center">

        <!-- LEFT CONTENT -->

        <div
          data-aos="fade-right">

          <div
            class="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-white dark:bg-slate-900 shadow-lg mb-8 border border-slate-200 dark:border-slate-700">

            <span class="text-emerald-500">
              ✨
            </span>

            <span
              class="font-semibold text-slate-700 dark:text-slate-200">

              Smart Learning Starts Here

            </span>

          </div>

          <h1
            class="text-5xl lg:text-7xl font-black leading-tight text-slate-900 dark:text-white">

            Learn.

            <br>

            <span
              class="bg-gradient-to-r from-emerald-500 via-blue-500 to-purple-500 bg-clip-text text-transparent">

              Teach.

            </span>

            <br>

            Grow Together.

          </h1>

          <p
            class="mt-8 text-lg leading-8 text-slate-600 dark:text-slate-300 max-w-xl">

            LearnAtHome is a complete coaching management platform
            designed to connect Students, Tutors, Parents and
            Administrators under one intelligent learning ecosystem.

          </p>

          <div
            class="mt-10 flex flex-wrap gap-5">

            <router-link
              to="/register"
              class="px-8 py-4 rounded-2xl bg-gradient-to-r from-emerald-500 to-blue-500 text-white font-semibold shadow-2xl hover:scale-105 transition">

              Get Started

            </router-link>

            <router-link
              to="/login"
              class="px-8 py-4 rounded-2xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-white hover:shadow-xl dark:hover:bg-slate-800 transition">

              Login

            </router-link>

          </div>

          <!-- Mini Feature Chips -->

          <div
            class="mt-12 flex flex-wrap gap-4">

            <div
              class="glass-chip">

              📚 Study Material

            </div>

            <div
              class="glass-chip">

              📅 Smart Scheduling

            </div>

            <div
              class="glass-chip">

              📈 Progress Tracking

            </div>

          </div>

        </div>

        <!-- RIGHT CONTENT -->

        <div
          data-aos="fade-left"
          class="relative flex justify-center">

          <!-- Floating Cards -->

          <div
            class="glass-card absolute top-4 left-0 animate-float">

            👨‍🏫 Tutors

          </div>

          <div
            class="glass-card absolute top-36 right-0 animate-float2">

            👨‍🎓 Students

          </div>

          <div
            class="glass-card absolute bottom-16 left-10 animate-float3">

            👨‍👩‍👧 Parents

          </div>

          <div
            class="glass-card absolute bottom-0 right-12 animate-float">

            📅 Timetable

          </div>

          <!-- Main Illustration -->

          <img
            src="@/assets/illustrations/education.svg"
            alt="Education Illustration"
            class="relative z-10 w-full max-w-xl animate-main-float drop-shadow-2xl"
          />

        </div>

      </div>

    </section>

    <!-- ================= ABOUT ================= -->

    <section
      id="about"
      class="relative py-24">

      <div
        class="max-w-6xl mx-auto px-6">

        <div
          data-aos="fade-up"
          class="text-center">

          <h2
            class="text-4xl lg:text-5xl font-bold text-slate-900 dark:text-white">

            Why LearnAtHome?

          </h2>

          <p
            class="mt-8 text-lg leading-9 max-w-4xl mx-auto text-slate-600 dark:text-slate-300">

            LearnAtHome is designed to simplify coaching management by
            bringing Students, Tutors, Parents and Administrators onto
            one collaborative platform. From scheduling classes and
            sharing study materials to monitoring attendance and tracking
            academic progress, every feature is built to create a more
            organized, transparent and engaging learning experience.

          </p>

        </div>

      </div>

    </section>

        <!-- ================= FEATURES ================= -->

    <section
      id="features"
      class="relative py-24">

      <div class="max-w-7xl mx-auto px-6">

        <div
          data-aos="fade-up"
          class="text-center">

          <h2
            class="text-4xl lg:text-5xl font-bold text-slate-900 dark:text-white">

            Everything You Need
            <br>

            For Better Learning

          </h2>

          <p
            class="mt-6 text-lg text-slate-600 dark:text-slate-300 max-w-3xl mx-auto">

            LearnAtHome provides all the essential tools required to
            efficiently manage coaching institutes, improve collaboration,
            and create a better learning experience.

          </p>

        </div>

        <div
          class="mt-20 grid md:grid-cols-2 lg:grid-cols-3 gap-8">

          <div
            v-for="feature in features"
            :key="feature.title"
            class="group relative rounded-3xl p-[2px] overflow-hidden">

            <!-- Gradient Border -->

            <div
              class="absolute inset-0 rounded-3xl bg-gradient-to-r from-emerald-500 via-blue-500 to-purple-500 opacity-0 group-hover:opacity-100 transition duration-500 blur-sm">
            </div>

            <!-- Card -->

            <div
              class="relative h-full rounded-3xl bg-white dark:bg-slate-900 backdrop-blur-xl border border-white/30 dark:border-slate-700/50 p-8 shadow-xl hover:-translate-y-4 transition-all duration-500">

              <div
                class="w-16 h-16 rounded-2xl bg-gradient-to-r from-emerald-500 to-blue-500 flex items-center justify-center text-white shadow-lg">

                <component
                  :is="feature.icon"
                  class="w-8 h-8"/>

              </div>

              <h3
                class="mt-8 text-2xl font-bold text-slate-900 dark:text-white">

                {{ feature.title }}

              </h3>

              <p
                class="mt-5 leading-8 text-slate-600 dark:text-slate-300">

                {{ feature.desc }}

              </p>

            </div>

          </div>

        </div>

      </div>

    </section>





    <!-- ================= ROLE SECTION ================= -->

    <section
      id="roles"
      class="relative py-24">

      <div class="max-w-7xl mx-auto px-6">

        <div
          data-aos="fade-up"
          class="text-center">

          <h2
            class="text-4xl lg:text-5xl font-bold text-slate-900 dark:text-white">

            Built For Everyone

          </h2>

          <p
            class="mt-6 text-lg text-slate-600 dark:text-slate-300 max-w-2xl mx-auto">

            Every user gets a dedicated dashboard designed specifically
            for their responsibilities.

          </p>

        </div>



        <div
          class="mt-20 grid md:grid-cols-2 lg:grid-cols-4 gap-8">

          <div
            v-for="role in roles"
            :key="role.title"
            class="group relative overflow-hidden rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 shadow-xl p-8 hover:-translate-y-4 transition duration-500">

            <!-- Background Circle -->

            <div
              class="absolute -right-10 -top-10 w-40 h-40 rounded-full bg-gradient-to-r opacity-10 dark:opacity-10 group-hover:scale-125 transition duration-700"
              :class="role.color">
            </div>

            <!-- Emoji -->

            <div
              class="relative w-20 h-20 rounded-full flex items-center justify-center text-5xl shadow-xl bg-gradient-to-r"
              :class="role.color">

              {{ role.emoji }}

            </div>

            <h3
              class="mt-8 text-2xl font-bold text-slate-900 dark:text-white">

              {{ role.title }}

            </h3>

            <p
              class="mt-5 leading-8 text-slate-600 dark:text-slate-300">

              {{ role.desc }}

            </p>

            <button
              class="mt-8 text-emerald-600 dark:text-emerald-400 font-semibold group-hover:translate-x-2 transition">



            </button>

          </div>

        </div>

      </div>

    </section>





    <!-- ================= WAVE DIVIDER ================= -->

    <div class="relative">

      <svg
        viewBox="0 0 1440 120"
        class="w-full fill-white dark:fill-slate-900">

        <path
          d="M0,64L80,69.3C160,75,320,85,480,90.7C640,96,800,96,960,85.3C1120,75,1280,53,1360,42.7L1440,32V120H1360C1280,120,1120,120,960,120C800,120,640,120,480,120C320,120,160,120,80,120H0Z">
        </path>

      </svg>

    </div>

        <!-- ================= HOW IT WORKS ================= -->

    <section
      id="workflow"
      class="relative py-28 bg-white dark:bg-slate-900">

      <div class="max-w-7xl mx-auto px-6">

        <div
          class="text-center mb-20"
          data-aos="fade-up">

          <span
            class="inline-block px-5 py-2 rounded-full bg-emerald-100 dark:bg-emerald-900/40 text-emerald-600 dark:text-emerald-400 font-semibold">

            How It Works

          </span>

          <h2
            class="mt-6 text-4xl lg:text-5xl font-bold text-slate-900 dark:text-white">

            A Simple Learning Workflow

          </h2>

          <p
            class="mt-6 max-w-3xl mx-auto text-lg leading-8 text-slate-600 dark:text-slate-300">

            LearnAtHome creates a smooth connection between students,
            tutors, parents and administrators to ensure learning
            becomes more organized and transparent.

          </p>

        </div>

        <div class="relative">

          <!-- Connecting Line -->

          <div
            class="hidden lg:block absolute top-16 left-0 w-full h-1 bg-gradient-to-r from-emerald-500 via-blue-500 to-purple-500 rounded-full opacity-30">
          </div>

          <div
            class="grid lg:grid-cols-4 md:grid-cols-2 gap-10 relative z-10">

            <div
              v-for="(role,index) in roles"
              :key="index"
              class="text-center">

              <div
                class="mx-auto w-24 h-24 rounded-full flex items-center justify-center text-5xl bg-white dark:bg-slate-800 shadow-xl border border-slate-200 dark:border-slate-700 hover:scale-110 transition duration-500">

                {{ role.emoji }}

              </div>

              <div
                class="mt-6 w-10 h-10 rounded-full mx-auto flex items-center justify-center bg-gradient-to-r from-emerald-500 to-blue-500 text-white font-bold">

                {{ index+1 }}

              </div>

              <h3
                class="mt-6 text-2xl font-bold text-slate-900 dark:text-white">

                {{ role.title }}

              </h3>

              <p
                class="mt-4 text-slate-600 dark:text-slate-300 leading-7">

                {{ role.desc }}

              </p>

            </div>

          </div>

        </div>

      </div>

    </section>





    <!-- ================= CTA ================= -->

    <section
      class="relative py-28 overflow-hidden">

      <div class="max-w-6xl mx-auto px-6">

        <div
          class="relative overflow-hidden rounded-[40px] bg-gradient-to-r from-emerald-500 via-blue-500 to-purple-600 shadow-2xl">

          <!-- Floating Circles -->

          <div
            class="absolute -top-20 -left-20 w-72 h-72 rounded-full bg-white/20 blur-3xl">
          </div>

          <div
            class="absolute bottom-0 right-0 w-80 h-80 rounded-full bg-white/20 blur-3xl">
          </div>

          <div
            class="relative z-10 px-10 py-24 text-center">

            <h2
              class="text-5xl font-bold text-white">

              Ready to Begin Your Journey?

            </h2>

            <p
              class="mt-6 text-lg text-white/90 max-w-2xl mx-auto leading-8">

              Join LearnAtHome and experience an easier way to
              manage learning, coaching and communication.

            </p>

            <div
              class="mt-12 flex justify-center gap-6 flex-wrap">

              <router-link
                to="/login"
                class="px-10 py-4 rounded-2xl bg-white text-emerald-600 font-semibold shadow-xl hover:scale-105 transition">

                Login

              </router-link>

              <router-link
                to="/register"
                class="px-10 py-4 rounded-2xl border border-white text-white hover:bg-white hover:text-emerald-600 transition">

                Register

              </router-link>

            </div>

          </div>

        </div>

      </div>

    </section>





    <!-- ================= FOOTER ================= -->

    <footer
      class="bg-slate-900 dark:bg-slate-950 text-white pt-20 pb-10">

      <div
        class="max-w-7xl mx-auto px-6">

        <div
          class="grid lg:grid-cols-4 md:grid-cols-2 gap-10">

          <!-- Logo -->

          <div>

            <h2
              class="text-3xl font-bold">

              🎓 LearnAtHome

            </h2>

            <p
              class="mt-5 text-slate-400 leading-8">

              A modern coaching management platform built for
              students, tutors, parents and administrators.

            </p>

          </div>

          <!-- Quick Links -->

          <div>

            <h3 class="font-bold text-lg">

              Quick Links

            </h3>

            <ul class="space-y-4 mt-6 text-slate-400">

              <li><a href="#about" class="hover:text-white transition">About</a></li>

              <li><a href="#features" class="hover:text-white transition">Features</a></li>

              <li><a href="#workflow" class="hover:text-white transition">Workflow</a></li>

            </ul>

          </div>

          <!-- Roles -->

          <div>

            <h3 class="font-bold text-lg">

              User Roles

            </h3>

            <ul class="space-y-4 mt-6 text-slate-400">

              <li>Student</li>

              <li>Tutor</li>

              <li>Parent</li>

              <li>Administrator</li>

            </ul>

          </div>

          <!-- Contact -->

          <div>

            <h3 class="font-bold text-lg">

              Get Started

            </h3>

            <p
              class="mt-5 text-slate-400">

              Create an account or login to access your personalized dashboard.

            </p>

            <router-link
              to="/register"
              class="inline-block mt-8 px-6 py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-blue-500 hover:scale-105 transition">

              Join Now

            </router-link>

          </div>

        </div>

        <div
          class="mt-16 border-t border-slate-800 pt-8 text-center text-slate-500">

          © 2026 LearnAtHome • Built with Vue 3 & Tailwind CSS

        </div>

      </div>

    </footer>

  </div>

</template>

<script setup>
import {
  AcademicCapIcon,
  CalendarDaysIcon,
  ChartBarIcon,
  UserGroupIcon,
  BookOpenIcon,
  ClipboardDocumentListIcon
} from "@heroicons/vue/24/outline"

import { ref, onMounted, onUnmounted } from "vue"

const isDarkMode = ref(false)

const features = [
  {
    title: "Student Management",
    icon: AcademicCapIcon,
    desc: "Maintain student profiles, attendance, assignments and academic progress with ease."
  },
  {
    title: "Tutor Dashboard",
    icon: UserGroupIcon,
    desc: "Manage classes, upload notes, interact with students and monitor performance."
  },
  {
    title: "Parent Portal",
    icon: ClipboardDocumentListIcon,
    desc: "Parents can monitor attendance, results and communicate directly with tutors."
  },
  {
    title: "Class Scheduling",
    icon: CalendarDaysIcon,
    desc: "Create weekly schedules and organize coaching sessions effortlessly."
  },
  {
    title: "Study Materials",
    icon: BookOpenIcon,
    desc: "Upload notes, assignments, quizzes and learning resources for students."
  },
  {
    title: "Analytics",
    icon: ChartBarIcon,
    desc: "Track attendance, academic performance and institute growth through analytics."
  }
]

const roles = [
  {
    title: "Student",
    emoji: "🎓",
    color: "from-emerald-500 to-green-400",
    desc: "Access study material, attend classes, submit assignments and monitor your progress."
  },
  {
    title: "Tutor",
    emoji: "👩‍🏫",
    color: "from-blue-500 to-cyan-400",
    desc: "Manage students, create schedules, upload learning resources and conduct classes."
  },
  {
    title: "Parent",
    emoji: "👨‍👩‍👧",
    color: "from-purple-500 to-pink-500",
    desc: "Stay informed about attendance, marks, performance and upcoming schedules."
  },
  {
    title: "Admin",
    emoji: "⚙️",
    color: "from-orange-500 to-amber-400",
    desc: "Control the complete coaching platform including tutors, students and parents."
  }
]

const navbarShadow = ref(false)

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  document.documentElement.classList.toggle('dark', isDarkMode.value)
  localStorage.setItem('darkMode', isDarkMode.value)
}

const onScroll = () => {
  navbarShadow.value = window.scrollY > 40
}

onMounted(() => {
  const savedDarkMode = localStorage.getItem('darkMode') === 'true'
  isDarkMode.value = savedDarkMode
  document.documentElement.classList.toggle('dark', savedDarkMode)
  window.addEventListener("scroll", onScroll)
})

onUnmounted(() => {
  window.removeEventListener("scroll", onScroll)
})
</script>


<style scoped>

/* -------------------------------
   Smooth Scrolling
-------------------------------- */

html{
  scroll-behavior:smooth;
}

/* -------------------------------
   Glass Cards
-------------------------------- */

.glass-card{

  background:rgba(255,255,255,.72);

  backdrop-filter:blur(18px);

  border:1px solid rgba(255,255,255,.25);

  padding:16px 22px;

  border-radius:18px;

  font-weight:600;

  box-shadow:0 12px 35px rgba(0,0,0,.08);

}

.dark .glass-card{

  background:rgba(15,23,42,.75);

  border:1px solid rgba(255,255,255,.08);

}

/* -------------------------------
   Feature Chips
-------------------------------- */

.glass-chip{

  background:rgba(255,255,255,.75);

  backdrop-filter:blur(16px);

  border-radius:9999px;

  padding:12px 22px;

  font-size:.9rem;

  font-weight:600;

  box-shadow:0 8px 25px rgba(0,0,0,.08);

  border:1px solid rgba(255,255,255,.5);

  color:#1e293b;

}

.dark .glass-chip{

  background:rgba(15,23,42,.75);

  color:white;

  border:1px solid rgba(255,255,255,.1);

}

/* -------------------------------
   Floating Background
-------------------------------- */

@keyframes blob{

0%{

transform:translate(0,0) scale(1);

}

25%{

transform:translate(30px,-30px) scale(1.08);

}

50%{

transform:translate(-20px,30px) scale(.95);

}

75%{

transform:translate(20px,-15px) scale(1.05);

}

100%{

transform:translate(0,0) scale(1);

}

}

.animate-blob{

animation:blob 14s infinite ease-in-out;

}

.animation-delay-2{

animation-delay:2s;

}

.animation-delay-4{

animation-delay:4s;

}

/* -------------------------------
   Floating Cards
-------------------------------- */

@keyframes float{

0%,100%{

transform:translateY(0);

}

50%{

transform:translateY(-15px);

}

}

.animate-float{

animation:float 4s ease-in-out infinite;

}

.animate-float2{

animation:float 5s ease-in-out infinite;

}

.animate-float3{

animation:float 6s ease-in-out infinite;

}

.animate-main-float{

animation:float 5s ease-in-out infinite;

}

/* -------------------------------
   Gradient Animation
-------------------------------- */

@keyframes gradientMove{

0%{

background-position:0% 50%;

}

50%{

background-position:100% 50%;

}

100%{

background-position:0% 50%;

}

}

.bg-gradient-to-r{

background-size:220% 220%;

animation:gradientMove 12s linear infinite;

}

/* -------------------------------
   Cards Hover
-------------------------------- */

.group{

transition:.45s;

}

.group:hover{

transform:translateY(-10px);

}

/* -------------------------------
   Buttons
-------------------------------- */

button,
a{

transition:.3s ease;

}

button:hover,
a:hover{

transform:translateY(-2px);

}

/* -------------------------------
   Images
-------------------------------- */

img{

user-select:none;

pointer-events:none;

}

/* -------------------------------
   Section Padding
-------------------------------- */

section{

position:relative;

z-index:5;

}

/* -------------------------------
   Footer Links
-------------------------------- */

footer a{

transition:.3s;

}

footer a:hover{

color:white;

padding-left:5px;

}

/* -------------------------------
   Scrollbar
-------------------------------- */

::-webkit-scrollbar{

width:10px;

}

::-webkit-scrollbar-track{

background:#f1f5f9;

}

::-webkit-scrollbar-thumb{

background:linear-gradient(#10b981,#3b82f6);

border-radius:20px;

}

.dark ::-webkit-scrollbar-track{

background:#0f172a;

}

.dark ::-webkit-scrollbar-thumb{

background:linear-gradient(#10b981,#3b82f6);

}

/* -------------------------------
   Mobile
-------------------------------- */

@media(max-width:1024px){

.glass-card{

display:none;

}

}

@media(max-width:768px){

h1{

font-size:3rem!important;

}

h2{

font-size:2.2rem!important;

}

section{

padding-top:80px;

padding-bottom:80px;

}

}

@media(max-width:640px){

.glass-chip{

font-size:.8rem;

padding:10px 16px;

}

}

/* -------------------------------
   Glow Effect
-------------------------------- */

.group:hover{

box-shadow:0 25px 60px rgba(16,185,129,.15);

}

/* -------------------------------
   CTA Animation
-------------------------------- */

@keyframes pulseGlow{

0%{

box-shadow:0 0 0 rgba(59,130,246,.25);

}

50%{

box-shadow:0 0 40px rgba(59,130,246,.35);

}

100%{

box-shadow:0 0 0 rgba(59,130,246,.25);

}

}

section:last-of-type .rounded-\[40px\]{

animation:pulseGlow 5s infinite;

}

</style>