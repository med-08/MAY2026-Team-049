<script setup>
import { ref } from "vue"
import { useRoute } from "vue-router"
import {
  Squares2X2Icon,
  CalendarDaysIcon,
  ClipboardDocumentCheckIcon,
  TableCellsIcon,
  PuzzlePieceIcon,
  PencilSquareIcon,
  ClipboardDocumentListIcon,
  BookOpenIcon,
  LightBulbIcon,
  QuestionMarkCircleIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  XMarkIcon,
  AcademicCapIcon,
} from "@heroicons/vue/24/outline"

defineProps({ open: Boolean })
const emit = defineEmits(["close", "logout"])
const route = useRoute()

const navItems = [
  { name: "Dashboard", to: "/student/dashboard", icon: Squares2X2Icon },
  { name: "My Sessions", to: "/student/sessions", icon: CalendarDaysIcon },
  { name: "Session Booking", to: "/student/booking", icon: ClipboardDocumentCheckIcon },
  { name: "Timetable", to: "/student/timetable", icon: TableCellsIcon },
  { name: "Weekly Quiz", to: "/student/quiz", icon: PuzzlePieceIcon },
  { name: "Interactive Assignments", to: "/student/assignments", icon: PencilSquareIcon },
  { name: "Homework", to: "/student/homework", icon: ClipboardDocumentListIcon },
  { name: "Study Resources", to: "/student/resources", icon: BookOpenIcon },
  { name: "Study Tips", to: "/student/study-tips", icon: LightBulbIcon },
  { name: "FAQ", to: "/student/faq", icon: QuestionMarkCircleIcon },
  { name: "Profile", to: "/student/profile", icon: UserCircleIcon },
]
</script>

<template>
  <!-- Mobile overlay -->
  <Transition name="fade">
    <div v-if="open" class="fixed inset-0 bg-slate-900/50 z-40 lg:hidden" @click="emit('close')"></div>
  </Transition>

  <aside
    class="fixed top-0 left-0 h-full w-72 bg-white dark:bg-card-dark border-r border-slate-100 dark:border-border-dark z-50 flex flex-col transition-transform duration-300 lg:translate-x-0"
    :class="open ? 'translate-x-0' : '-translate-x-full'"
  >
    <div class="flex items-center justify-between px-6 h-20 shrink-0">
      <div class="flex items-center gap-2.5">
        <div class="w-10 h-10 rounded-xl brand-gradient flex items-center justify-center shrink-0">
          <AcademicCapIcon class="w-6 h-6 text-white" />
        </div>
        <div>
          <p class="font-display font-bold leading-tight">LearnAtHome</p>
          
        </div>
      </div>
      <button class="lg:hidden text-ink-soft" @click="emit('close')">
        <XMarkIcon class="w-6 h-6" />
      </button>
    </div>

    <nav class="flex-1 overflow-y-auto px-3 py-2 space-y-1">
      <router-link
        v-for="item in navItems"
        :key="item.to"
        :to="item.to"
        class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition group"
        :class="route.path === item.to
          ? 'brand-gradient text-white shadow-sm'
          : 'text-ink-soft dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-white/5 hover:text-ink dark:hover:text-white'"
        @click="emit('close')"
      >
        <component :is="item.icon" class="w-5 h-5 shrink-0" />
        <span class="truncate">{{ item.name }}</span>
      </router-link>
    </nav>

    <div class="p-3 border-t border-slate-100 dark:border-border-dark">
      <button
        class="w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium text-danger hover:bg-danger/10 transition"
        @click="emit('logout')"
      >
        <ArrowRightOnRectangleIcon class="w-5 h-5 shrink-0" />
        Logout
      </button>
    </div>
  </aside>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity .2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
