<script setup>
import { CalendarIcon, ClockIcon, UserIcon, BookOpenIcon, FlagIcon, TagIcon } from "@heroicons/vue/24/outline"

defineProps({
  session: Object,
})
</script>

<template>
  <div class="card overflow-hidden">
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
          <p class="text-sm font-semibold">{{ session.topics.join(", ") }}</p>
        </div>
      </div>
     
    </div>
  </div>
</template>
