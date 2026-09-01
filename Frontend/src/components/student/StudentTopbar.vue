<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue"
import { useRouter } from "vue-router"
import {
  Bars3Icon,
  MagnifyingGlassIcon,
  SunIcon,
  MoonIcon,
  BellIcon,
} from "@heroicons/vue/24/outline"
import { useTheme } from "../../composables/useTheme"
import { studentApi } from "../../services/studentApi"
import InitialsAvatar from "./InitialsAvatar.vue"

const emit = defineEmits(["toggle-sidebar"])
const { isDark, toggleTheme } = useTheme()
const search = ref("")
const clockLabel = ref("")
let clockTimer = null
const searchFocused = ref(false)
const router = useRouter()

const student = ref({
  name: "",
  initials: "ST"
})

const assignments = ref([])
const homeworkList = ref([])
const weeklyQuizzes = ref([])
const studyResources = ref([])
const studyTips = ref([])
const faqs = ref([])

// Real, backend-driven notifications (e.g. a tutor replying to a doubt).
// Polled so the student notices a reply without needing to refresh.
const notifications = ref([])
const notificationsOpen = ref(false)
let notificationsTimer = null
const unreadCount = computed(() => notifications.value.filter((n) => !n.isRead).length)

async function loadNotifications() {
  try {
    const res = await studentApi.getNotifications()
    notifications.value = res?.data?.notifications || []
  } catch {
    // keep last known state on transient failure
  }
}

async function openNotification(n) {
  if (!n.isRead) {
    try {
      await studentApi.markNotificationRead(n.id)
      n.isRead = true
    } catch {
      // ignore - non-critical
    }
  }
  notificationsOpen.value = false
  if (n.actionUrl) {
    router.push(n.actionUrl)
  } else if (n.type === "Doubt") {
    router.push("/student/ask-doubt")
  } else if (["Class Started", "Meeting Scheduled", "Meeting Updated", "Class Completed", "Session Completed"].includes(n.type)) {
    router.push("/student/sessions")
  }
}

function toggleNotifications() {
  notificationsOpen.value = !notificationsOpen.value
}

function closeNotifications() {
  setTimeout(() => { notificationsOpen.value = false }, 150)
}

function makeInitials(name) {
  if (!name) return "ST"
  return name
    .split(" ")
    .map(part => part[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
}

onMounted(async () => {
  const updateClock = () => { clockLabel.value = new Date().toLocaleString("en-IN", { weekday: "short", day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit", hour12: true }) }
  updateClock()
  clockTimer = window.setInterval(updateClock, 1000)
  try {
    const profileRes = await studentApi.getProfile()
    if (profileRes.success && profileRes.data?.student) {
      const s = profileRes.data.student
      student.value = {
        name: s.name || "",
        initials: makeInitials(s.name || "")
      }
    }
  } catch (err) {
    console.error("Topbar profile fetch error:", err)
  }

  try {
    const assignmentsRes = await studentApi.getAssignments()
    assignments.value = assignmentsRes?.data?.assignments || []
  } catch {
    assignments.value = []
  }

  try {
    const quizzesRes = await studentApi.getQuizzes()
    weeklyQuizzes.value = quizzesRes?.data?.quizzes || []
  } catch {
    weeklyQuizzes.value = []
  }

  try {
    const resourcesRes = await studentApi.getResources()
    studyResources.value = resourcesRes?.data?.studyResources || []
  } catch {
    studyResources.value = []
  }

  try {
    const tipsRes = await studentApi.getStudyTips()
    studyTips.value = tipsRes?.data?.studyTips || []
  } catch {
    studyTips.value = []
  }

  try {
    const faqRes = await studentApi.getFaqs()
    faqs.value = faqRes?.data?.faqs || []
  } catch {
    faqs.value = []
  }

  // homework endpoint not clearly separate in current API
  homeworkList.value = assignments.value

  await loadNotifications()
  notificationsTimer = window.setInterval(loadNotifications, 30000)
})

onUnmounted(() => {
  if (clockTimer) window.clearInterval(clockTimer)
  if (notificationsTimer) window.clearInterval(notificationsTimer)
})

const searchIndex = computed(() => [
  ...homeworkList.value.map((h) => ({
    type: "Homework",
    title: h.title || "",
    subtitle: h.subject || h.session || "",
    to: "/student/homework",
  })),
  ...weeklyQuizzes.value.map((q) => ({
    type: "Quiz",
    title: q.title || "",
    subtitle: q.subject || "",
    to: q.quiz_id ? `/student/quiz/${q.quiz_id}` : "/student/quiz",
  })),
  ...studyResources.value.map((r) => ({
    type: "Resource",
    title: r.resource_title || r.title || "",
    subtitle: r.resource_type || "",
    to: "/student/resources",
  })),
  ...studyTips.value.map((t) => ({
    type: "Study Tip",
    title: t.tip || "",
    subtitle: t.subject || "",
    to: "/student/study-tips",
  })),
  ...faqs.value.map((f) => ({
    type: "FAQ",
    title: f.q || "",
    subtitle: "Frequently Asked Questions",
    to: "/student/faq",
  })),
])

const searchResults = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return []
  return searchIndex.value
    .filter(
      (item) =>
        item.title.toLowerCase().includes(q) ||
        item.subtitle.toLowerCase().includes(q)
    )
    .slice(0, 8)
})

function goToResult(result) {
  router.push(result.to)
  search.value = ""
  searchFocused.value = false
}

function handleBlur() {
  setTimeout(() => {
    searchFocused.value = false
  }, 150)
}
</script>

<template>
  <header class="sticky top-0 z-30 h-20 flex items-center gap-4 px-4 md:px-8 bg-white/80 dark:bg-surface-dark/80 backdrop-blur border-b border-slate-100 dark:border-border-dark">
    <button class="lg:hidden text-ink-soft shrink-0" @click="emit('toggle-sidebar')">
      <Bars3Icon class="w-6 h-6" />
    </button>

    <div class="min-w-0 shrink-0 hidden sm:block">
      <p class="text-[11px] font-semibold text-brand-blue">{{ clockLabel }}</p>
      <h2 class="font-display font-bold text-lg leading-tight truncate">
        Welcome back, {{ student.name ? student.name.split(" ")[0] : "Student" }} 🎓
      </h2>
      <p class="text-xs text-ink-soft dark:text-slate-400 truncate">
        Great achievements begin with small, consistent efforts.
      </p>
    </div>

    <div class="flex-1 max-w-md mx-auto hidden md:block">
      <div class="relative">
        <MagnifyingGlassIcon class="w-4.5 h-4.5 text-ink-soft absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          v-model="search"
          type="text"
          placeholder="Search assignments, quizzes, homework, resources..."
          class="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-100 dark:bg-white/5 text-sm placeholder:text-ink-soft/60 dark:placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-brand-blue/40"
          @focus="searchFocused = true"
          @blur="handleBlur"
          @keydown.esc="search = ''; searchFocused = false"
          @keydown.enter="searchResults.length && goToResult(searchResults[0])"
        />

        <div
          v-if="searchFocused && search.trim()"
          class="card absolute left-0 right-0 top-full mt-2 py-2 max-h-80 overflow-y-auto z-40"
        >
          <button
            v-for="result in searchResults"
            :key="result.type + result.title"
            class="w-full flex items-start gap-3 px-4 py-2.5 text-left hover:bg-slate-100 dark:hover:bg-white/5 transition"
            @click="goToResult(result)"
          >
            <span class="shrink-0 mt-0.5 text-[10px] font-semibold uppercase tracking-wide text-brand-blue bg-brand-blue/10 rounded-full px-2 py-0.5">
              {{ result.type }}
            </span>
            <span class="min-w-0">
              <span class="block text-sm font-medium truncate">{{ result.title }}</span>
              <span class="block text-xs text-ink-soft dark:text-slate-400 truncate">{{ result.subtitle }}</span>
            </span>
          </button>

          <p v-if="searchResults.length === 0" class="px-4 py-2.5 text-sm text-ink-soft dark:text-slate-400">
            No results for "{{ search }}"
          </p>
        </div>
      </div>
    </div>

    <div class="flex items-center gap-2 md:gap-3 ml-auto shrink-0">
      <div class="relative">
        <button
          class="relative w-10 h-10 rounded-xl flex items-center justify-center text-ink-soft hover:bg-slate-100 dark:hover:bg-white/5 transition"
          @click="toggleNotifications"
          @blur="closeNotifications"
        >
          <BellIcon class="w-5.5 h-5.5" />
          <span
            v-if="unreadCount"
            class="absolute top-1.5 right-1.5 min-w-[16px] h-4 px-1 rounded-full bg-danger text-white text-[10px] font-bold flex items-center justify-center leading-none"
          >
            {{ unreadCount > 9 ? '9+' : unreadCount }}
          </span>
        </button>

        <div
          v-if="notificationsOpen"
          class="card absolute right-0 top-full mt-2 w-80 max-h-96 overflow-y-auto py-2 z-40"
        >
          <p class="px-4 py-2 text-xs font-semibold uppercase tracking-wide text-ink-soft dark:text-slate-400">
            Notifications
          </p>
          <p v-if="!notifications.length" class="px-4 py-4 text-sm text-ink-soft dark:text-slate-400">
            No notifications yet.
          </p>
          <button
            v-for="n in notifications"
            :key="n.id"
            class="w-full text-left px-4 py-2.5 hover:bg-slate-100 dark:hover:bg-white/5 transition flex items-start gap-2"
            @mousedown.prevent="openNotification(n)"
          >
            <span
              class="mt-1.5 w-2 h-2 rounded-full shrink-0"
              :class="n.isRead ? 'bg-transparent' : 'bg-brand-blue'"
            />
            <span class="min-w-0">
              <span class="block text-sm font-semibold truncate">{{ n.title }}</span>
              <span class="block text-xs text-ink-soft dark:text-slate-400 line-clamp-2">{{ n.message }}</span>
            </span>
          </button>
        </div>
      </div>

      <button class="w-10 h-10 rounded-xl flex items-center justify-center text-ink-soft hover:bg-slate-100 dark:hover:bg-white/5 transition" @click="toggleTheme">
        <SunIcon v-if="isDark" class="w-5.5 h-5.5" />
        <MoonIcon v-else class="w-5.5 h-5.5" />
      </button>

      <router-link to="/student/profile" class="flex items-center gap-2.5 pl-2 border-l border-slate-200 dark:border-border-dark">
        <InitialsAvatar :initials="student.initials" size="sm" />
        <span class="hidden md:block text-sm font-semibold">
          {{ student.name || "Student" }}
        </span>
      </router-link>
    </div>
  </header>
</template>