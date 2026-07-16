<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  Squares2X2Icon, UserGroupIcon, AcademicCapIcon, UsersIcon,
  ClockIcon, ChartBarIcon, UserCircleIcon, ArrowLeftOnRectangleIcon,
  ChevronDownIcon, XMarkIcon
} from '@heroicons/vue/24/outline'

defineProps({ mobileOpen: { type: Boolean, default: false } })
const emit = defineEmits(['close'])

const route = useRoute()
const usersOpen = ref(true)

const isActive = (name) => route.name === name
const usersGroupActive = ['students', 'tutors', 'parents'].includes(route.name)

const links = [
  { name: 'students', label: 'Students' },
  { name: 'tutors', label: 'Tutors' },
  { name: 'parents', label: 'Parents' }
]
</script>

<template>
  <transition name="fade">
    <div v-if="mobileOpen" class="fixed inset-0 bg-slate-900/50 z-40 lg:hidden" @click="emit('close')" />
  </transition>

  <aside
    class="fixed top-0 left-0 h-screen w-64 bg-grad-sidebar-light dark:bg-grad-sidebar-dark border-r border-slate-200 dark:border-white/10 z-50 flex flex-col transition-transform transition-colors duration-300 lg:translate-x-0"
    :class="mobileOpen ? 'translate-x-0' : '-translate-x-full'"
  >
    <div class="flex items-center justify-between px-5 h-16 border-b border-slate-200 dark:border-white/10">
      <router-link to="/admin" class="flex items-center gap-2 text-slate-900 dark:text-white font-display font-bold text-lg">
        <span>✷</span>
        <span>LearnAtHome</span>
      </router-link>
      <button class="lg:hidden text-slate-400 hover:text-slate-900 dark:hover:text-white" @click="emit('close')">
        <XMarkIcon class="w-5 h-5" />
      </button>
    </div>

    <nav class="flex-1 overflow-y-auto px-3 py-5 space-y-1">
      <router-link
        to="/admin"
        class="nav-link"
        :class="isActive('dashboard') ? 'nav-link-active' : ''"
      >
        <Squares2X2Icon class="w-5 h-5" />
        <span>Dashboard</span>
      </router-link>

      <button
        class="nav-link w-full justify-between"
        :class="usersGroupActive ? 'text-slate-900 dark:text-white' : ''"
        @click="usersOpen = !usersOpen"
      >
        <span class="flex items-center gap-3">
          <UserGroupIcon class="w-5 h-5" />
          <span>Users</span>
        </span>
        <ChevronDownIcon class="w-4 h-4 transition-transform duration-200" :class="usersOpen ? 'rotate-180' : ''" />
      </button>
      <div v-show="usersOpen" class="pl-4 space-y-1">
        <router-link
          v-for="l in links"
          :key="l.name"
          :to="`/admin/${l.name}`"
          class="nav-link text-sm"
          :class="isActive(l.name) ? 'nav-link-active' : ''"
        >
          <component :is="l.name === 'students' ? AcademicCapIcon : l.name === 'tutors' ? UserCircleIcon : UsersIcon" class="w-4.5 h-4.5" style="width:1.1rem;height:1.1rem" />
          <span>{{ l.label }}</span>
        </router-link>
      </div>

      <router-link to="/admin/pending-approvals" class="nav-link" :class="isActive('pending-approvals') ? 'nav-link-active' : ''">
        <ClockIcon class="w-5 h-5" />
        <span>Pending Approvals</span>
      </router-link>

      <router-link to="/admin/analytics" class="nav-link" :class="isActive('analytics') ? 'nav-link-active' : ''">
        <ChartBarIcon class="w-5 h-5" />
        <span>Analytics</span>
      </router-link>

      <router-link to="/admin/profile" class="nav-link" :class="isActive('profile') ? 'nav-link-active' : ''">
        <UserCircleIcon class="w-5 h-5" />
        <span>Admin Profile</span>
      </router-link>
    </nav>

    <div class="px-3 pb-5">
      <button class="nav-link w-full !text-rose-600 dark:!text-rose-300 hover:!text-rose-700 dark:hover:!text-rose-200 hover:bg-rose-500/10">
        <ArrowLeftOnRectangleIcon class="w-5 h-5" />
        <span>Logout</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.nav-link {
  @apply flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-900/5 dark:hover:bg-white/5 hover:text-slate-900 dark:hover:text-white transition-colors duration-200;
}
.nav-link-active {
  @apply bg-gradient-to-r from-brand-green-500 to-brand-blue-500 !text-white shadow-soft;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
