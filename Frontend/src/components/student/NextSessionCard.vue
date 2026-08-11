<script setup>
import { computed } from "vue"
import { CalendarIcon, ClockIcon, UserIcon, BookOpenIcon, FlagIcon, TagIcon } from "@heroicons/vue/24/outline"

const props = defineProps({
  session: { type: Object, default: () => ({}) },
})

// The backend returns an empty object ({}) when the student has no
// upcoming session booked, so we can't rely on any single field being
// present. Treat "no id/subject" as "nothing booked".
const hasSession = computed(() => !!(props.session && props.session.session_id))
const topicsText = computed(() => {
  const topics = props.session?.topics
  return Array.isArray(topics) && topics.length ? topics.join(", ") : "—"
})
</script>

<template>
  <div v-if="!hasSession" class="card flex flex-col items-center justify-center text-center py-10 px-6">
    <CalendarIcon class="w-10 h-10 text-brand-blue mb-2" />
    <h3 class="font-display font-bold mb-1">No Upcoming Session</h3>
    <p class="text-sm text-ink-soft dark:text-slate-400">
      You don't have any session booked yet. Head to Session Booking to schedule one.
    </p>
  </div>

  <div v-else class="card overflow-hidden">
    <div class="brand-gradient px-6 py-4 flex items-center justify-between">
      <div>
        <p class="text-white/80 text-xs font-semibold tracking-wide uppercase">Next Session</p>
        <h3 class="text-white font-display font-bold text-lg">{{ session.subject }}</h3>
      </div>
      <span class="bg-white/20 text-white text-xs font-semibold px-3 py-1 rounded-full">{{ session.status }}</span>
    </div>

    <div class="relative ticket-stub" style="--stub-y: 0">
      <div class="ticket-notch left" style="--stub-y: 0"></div>
      <div class="ticket-notch right" style="--stub-y: 0"></div>
    </div>

    <div class="px-6 py-5 grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-4">
      <div class="flex items-start gap-2">
        <UserIcon class="w-5 h-5 text-brand-blue shrink-0 mt-0.5" />
        <div>
          <p class="text-xs text-ink-soft dark:text-slate-400">Tutor</p>
          <p class="text-sm font-semibold">{{ session.tutor }}</p>
        </div>
      </div>
      <div class="flex items-start gap-2">
        <TagIcon class="w-5 h-5 text-brand-blue shrink-0 mt-0.5" />
        <div>
          <p class="text-xs text-ink-soft dark:text-slate-400">Session Type</p>
          <p class="text-sm font-semibold">{{ session.type }}</p>
        </div>
      </div>
      <div class="flex items-start gap-2">
        <CalendarIcon class="w-5 h-5 text-brand-blue shrink-0 mt-0.5" />
        <div>
          <p class="text-xs text-ink-soft dark:text-slate-400">Date</p>
          <p class="text-sm font-semibold">{{ session.date }}</p>
        </div>
      </div>
      <div class="flex items-start gap-2">
        <ClockIcon class="w-5 h-5 text-brand-blue shrink-0 mt-0.5" />
        <div>
          <p class="text-xs text-ink-soft dark:text-slate-400">Time & Duration</p>
          <p class="text-sm font-semibold">{{ session.time }} · {{ session.duration }}</p>
        </div>
      </div>
      <div class="flex items-start gap-2 col-span-2 sm:col-span-1">
        <BookOpenIcon class="w-5 h-5 text-brand-blue shrink-0 mt-0.5" />
        <div>
          <p class="text-xs text-ink-soft dark:text-slate-400">Topics to be Covered</p>
          <p class="text-sm font-semibold">{{ topicsText }}</p>
        </div>
      </div>
     
    </div>

      <div v-if="session.meeting_url || session.meetingUrl" class="px-6 pb-6">
        <a
          :href="session.meeting_url || session.meetingUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl px-5 py-3 bg-brand-blue text-white font-semibold shadow-sm hover:opacity-90 transition"
        >
          Join Google Meet
        </a>
      </div>
  </div>
</template>
