<script setup>
import { ref, computed } from "vue"
import { useRouter } from "vue-router"
import {
  Bars3Icon,
  MagnifyingGlassIcon,
  SunIcon,
  MoonIcon,
} from "@heroicons/vue/24/outline"
import { useTheme } from "../../composables/useTheme"
import {
  student,
  assignments,
  homeworkList,
  weeklyQuizzes,
  studyResources,
  studyTips,
  faqs,
} from "../../data/studentMockData"
import InitialsAvatar from "./InitialsAvatar.vue"

defineProps({})
const emit = defineEmits(["toggle-sidebar"])
const { isDark, toggleTheme } = useTheme()
const search = ref("")
const searchFocused = ref(false)
const router = useRouter()

// Flatten every searchable student data source into one list of
// { type, title, subtitle, to } entries so the topbar search can match
// across assignments, homework, quizzes, resources, tips and FAQs.
const searchIndex = computed(() => [
  ...assignments.map((a) => ({
    type: "Assignment",
    title: a.title,
    subtitle: a.subject,
    to: "/student/assignments",
  })),
  ...homeworkList.map((h) => ({
    type: "Homework",
    title: h.title,
    subtitle: h.session,
    to: "/student/homework",
  })),
  ...weeklyQuizzes.map((q) => ({
    type: "Quiz",
    title: q.title,
    subtitle: q.subject,
    to: `/student/quiz/${q.quiz_id}`,
  })),
  ...studyResources.map((r) => ({
    type: "Resource",
    title: r.resource_title,
    subtitle: r.resource_type,
    to: "/student/resources",
  })),
  ...studyTips.map((t) => ({
    type: "Study Tip",
    title: t.tip,
    subtitle: t.subject,
    to: "/student/study-tips",
  })),
  ...faqs.map((f) => ({
    type: "FAQ",
    title: f.q,
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
  // Delay so a click on a result registers before the dropdown closes
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
      <h2 class="font-display font-bold text-lg leading-tight truncate">Welcome back, {{ student.name.split(" ")[0] }} 🎓</h2>
      <p class="text-xs text-ink-soft dark:text-slate-400 truncate">Great achievements begin with small, consistent efforts.</p>
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
      <button class="w-10 h-10 rounded-xl flex items-center justify-center text-ink-soft hover:bg-slate-100 dark:hover:bg-white/5 transition" @click="toggleTheme">
        <SunIcon v-if="isDark" class="w-5.5 h-5.5" />
        <MoonIcon v-else class="w-5.5 h-5.5" />
      </button>

      <router-link to="/student/profile" class="flex items-center gap-2.5 pl-2 border-l border-slate-200 dark:border-border-dark">
        <InitialsAvatar :initials="student.initials" size="sm" />
        <span class="hidden md:block text-sm font-semibold">{{ student.name }}</span>
      </router-link>
    </div>
  </header>
</template>
