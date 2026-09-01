<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue"
import { useRoute } from "vue-router"
import {
  Squares2X2Icon,
  CalendarDaysIcon,
  ClipboardDocumentCheckIcon,
  TableCellsIcon,
  PuzzlePieceIcon,
  ClipboardDocumentListIcon,
  BookOpenIcon,
  LightBulbIcon,
  RectangleStackIcon,
  QuestionMarkCircleIcon,
  ChatBubbleLeftRightIcon,
  UserCircleIcon,
  ArrowRightOnRectangleIcon,
  XMarkIcon,
  AcademicCapIcon,
} from "@heroicons/vue/24/outline"
import { studentApi } from "../../services/studentApi"

defineProps({ open: Boolean })
const emit = defineEmits(["close", "logout"])
const route = useRoute()
const notifications = ref([])
const bookableSessionIds = ref(new Set())
let bookingBadgeTimer = null

const newSessionCount = computed(() => {
  if (route.path === "/student/booking") return 0
  return notifications.value.filter(n => {
    if (n.isRead || n.type !== "Session Available") return false
    const match = String(n.actionUrl || '').match(/session_id=(\d+)/)
    return !match || bookableSessionIds.value.has(Number(match[1]))
  }).length
})

async function loadBookingBadge() {
  try {
    const [notificationRes, bookingRes] = await Promise.all([
      studentApi.getNotifications(),
      studentApi.getBookingSlots(),
    ])
    notifications.value = notificationRes?.data?.notifications || []
    const allSlots = [
      ...(bookingRes?.data?.bookingSlots?.regular || []),
      ...(bookingRes?.data?.bookingSlots?.oneToOne || []),
    ]
    bookableSessionIds.value = new Set(
      allSlots.filter(s => !s.booked).map(s => Number(s.id))
    )
  } catch {
    // Preserve the last known badge state during transient network failures.
  }
}

const navItems = [
  { name: "Dashboard", to: "/student/dashboard", icon: Squares2X2Icon },
  { name: "My Sessions", to: "/student/sessions", icon: CalendarDaysIcon },
  { name: "Session Booking", to: "/student/booking", icon: ClipboardDocumentCheckIcon, bookingBadge: true },
  { name: "Timetable", to: "/student/timetable", icon: TableCellsIcon },
  { name: "Weekly Quiz", to: "/student/quiz", icon: PuzzlePieceIcon },
  { name: "Homework", to: "/student/homework", icon: ClipboardDocumentListIcon },
  { name: "Study Resources", to: "/student/resources", icon: BookOpenIcon },
  { name: "Performance Insights", to: "/student/study-tips", icon: LightBulbIcon },
  { name: "Flashcards", to: "/student/flashcards", icon: RectangleStackIcon },
  { name: "FAQ", to: "/student/faq", icon: QuestionMarkCircleIcon },
  { name: "Ask Doubt", to: "/student/ask-doubt", icon: ChatBubbleLeftRightIcon },
  { name: "Messages", to: "/student/messages", icon: ChatBubbleLeftRightIcon },
  { name: "Profile", to: "/student/profile", icon: UserCircleIcon },
]
onMounted(async () => {
  await loadBookingBadge()
  bookingBadgeTimer = window.setInterval(loadBookingBadge, 15000)
})

onUnmounted(() => {
  if (bookingBadgeTimer) window.clearInterval(bookingBadgeTimer)
})

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
        <span class="min-w-0 flex-1 truncate">{{ item.name }}</span>
        <span
          v-if="item.bookingBadge && newSessionCount > 0"
          class="inline-flex min-w-5 items-center justify-center rounded-full bg-red-500 px-1.5 py-0.5 text-[10px] font-extrabold leading-none text-white shadow-sm"
        >
          {{ newSessionCount > 9 ? '9+' : newSessionCount }}
        </span>
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
