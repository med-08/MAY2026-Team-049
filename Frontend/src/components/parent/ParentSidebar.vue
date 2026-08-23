<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  Squares2X2Icon,
  ChartBarIcon,
  BookOpenIcon,
  CalendarDaysIcon,
  ChatBubbleLeftRightIcon,
  VideoCameraIcon,
  UserCircleIcon,
  ArrowLeftOnRectangleIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
import ConfirmModal from '../ui/ConfirmModal.vue'
import { useLogout } from '../../composables/useLogout'

defineProps({ mobileOpen: { type: Boolean, default: false } })
const emit = defineEmits(['close'])

const route = useRoute()
const logoutOpen = ref(false)
const { logout } = useLogout()

const isActive = (name) => route.name === name

const navItems = [
  { name: 'parent-dashboard', to: '/parent', label: 'Dashboard', icon: Squares2X2Icon },
  { name: 'parent-progress', to: '/parent/progress', label: 'Child Progress', icon: ChartBarIcon },
  { name: 'parent-curriculum', to: '/parent/curriculum', label: 'Curriculum Plan', icon: BookOpenIcon },
  { name: 'parent-schedule', to: '/parent/schedule', label: 'Connect with Your Child', icon: CalendarDaysIcon },
  { name: 'parent-meetings', to: '/parent/meetings', label: 'Connect with Tutor', icon: VideoCameraIcon },
  { name: 'parent-all-meetings', to: '/parent/all-meetings', label: 'All Meetings', icon: CalendarDaysIcon },
  { name: 'parent-messages', to: '/parent/messages', label: 'Messages', icon: ChatBubbleLeftRightIcon }
]

async function confirmLogout() {
  logoutOpen.value = false
  emit('close')
  await logout('/login')
}
</script>

<template>
  <transition name="fade">
    <div
      v-if="mobileOpen"
      class="fixed inset-0 bg-slate-900/50 z-40 lg:hidden"
      @click="emit('close')"
    />
  </transition>

  <aside
    class="fixed top-0 left-0 h-screen w-64 bg-grad-sidebar-light dark:bg-grad-sidebar-dark border-r border-slate-200 dark:border-white/10 z-50 flex flex-col transition-transform transition-colors duration-300 lg:translate-x-0"
    :class="mobileOpen ? 'translate-x-0' : '-translate-x-full'"
  >
    <div class="flex items-center justify-between px-5 h-16 border-b border-slate-200 dark:border-white/10">
      <router-link to="/parent" class="flex items-center gap-2 text-slate-900 dark:text-white font-display font-bold text-lg">
        <span>✷</span>
        <span>LearnAtHome</span>
      </router-link>
      <button class="lg:hidden text-slate-400 hover:text-slate-900 dark:hover:text-white" @click="emit('close')">
        <XMarkIcon class="w-5 h-5" />
      </button>
    </div>

    <nav class="flex-1 overflow-y-auto px-3 py-5 space-y-1">
      <router-link
        v-for="item in navItems"
        :key="item.name"
        :to="item.to"
        class="nav-link"
        :class="isActive(item.name) ? 'nav-link-active' : ''"
        @click="emit('close')"
      >
        <component :is="item.icon" class="w-5 h-5" />
        <span>{{ item.label }}</span>
      </router-link>

      <router-link
        to="/parent/profile"
        class="nav-link"
        :class="isActive('parent-profile') ? 'nav-link-active' : ''"
        @click="emit('close')"
      >
        <UserCircleIcon class="w-5 h-5" />
        <span>Parent Profile</span>
      </router-link>
    </nav>

    <div class="px-3 pb-5">
      <button
        class="nav-link w-full !text-rose-600 dark:!text-rose-300 hover:!text-rose-700 dark:hover:!text-rose-200 hover:bg-rose-500/10"
        @click="logoutOpen = true"
      >
        <ArrowLeftOnRectangleIcon class="w-5 h-5" />
        <span>Logout</span>
      </button>
    </div>
  </aside>

  <ConfirmModal
    :open="logoutOpen"
    title="Log out of LearnAtHome?"
    message="You'll need to sign in again to access the parent dashboard."
    confirm-label="Logout"
    @cancel="logoutOpen = false"
    @confirm="confirmLogout"
  />
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