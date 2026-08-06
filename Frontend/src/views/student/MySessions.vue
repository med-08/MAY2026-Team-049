<script setup>
import PageHeader from "../../components/student/PageHeader.vue"
import StatusBadge from "../../components/student/StatusBadge.vue"
import { CalendarIcon, ClockIcon, UserIcon, TagIcon, BookOpenIcon } from "@heroicons/vue/24/outline"
import { sessions } from "../../data/studentMockData"
</script>

<template>
  <div>
    <PageHeader title="My Sessions" subtitle="All your offline tuition sessions, upcoming and completed." />

    <section class="mb-8">
      <h3 class="font-display font-bold mb-3">Upcoming Sessions</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        <div v-for="s in sessions.upcoming" :key="s.id" class="card card-hover p-5">
          <div class="flex items-start justify-between mb-3">
            <h4 class="font-display font-bold">{{ s.subject }}</h4>
            <StatusBadge :status="s.status" />
          </div>
          <div class="space-y-2 text-sm">
            <p class="flex items-center gap-2 text-ink-soft dark:text-slate-300"><UserIcon class="w-4 h-4 shrink-0" /> {{ s.tutor }}</p>
            <p class="flex items-center gap-2 text-ink-soft dark:text-slate-300"><TagIcon class="w-4 h-4 shrink-0" /> {{ s.type }}</p>
            <p class="flex items-center gap-2 text-ink-soft dark:text-slate-300"><CalendarIcon class="w-4 h-4 shrink-0" /> {{ s.date }}</p>
            <p class="flex items-center gap-2 text-ink-soft dark:text-slate-300"><ClockIcon class="w-4 h-4 shrink-0" /> {{ s.time }} · {{ s.duration }}</p>
          </div>
        </div>
      </div>
    </section>

    <section>
      <h3 class="font-display font-bold mb-3">Completed Sessions</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        <div v-for="s in sessions.completed" :key="s.id" class="card card-hover p-5 opacity-90">
          <div class="flex items-start justify-between mb-3">
            <h4 class="font-display font-bold">{{ s.subject }}</h4>
            <StatusBadge :status="s.status" />
          </div>
          <div class="space-y-2 text-sm">
            <p class="flex items-center gap-2 text-ink-soft dark:text-slate-300"><UserIcon class="w-4 h-4 shrink-0" /> {{ s.tutor }}</p>
            <p class="flex items-center gap-2 text-ink-soft dark:text-slate-300"><TagIcon class="w-4 h-4 shrink-0" /> {{ s.type }}</p>
            <p class="flex items-center gap-2 text-ink-soft dark:text-slate-300"><CalendarIcon class="w-4 h-4 shrink-0" /> {{ s.date }}</p>
            <p class="flex items-center gap-2 text-ink-soft dark:text-slate-300"><ClockIcon class="w-4 h-4 shrink-0" /> {{ s.time }} · {{ s.duration }}</p>
            <p class="flex items-start gap-2 text-ink-soft dark:text-slate-300"><BookOpenIcon class="w-4 h-4 shrink-0 mt-0.5" /> {{ s.topics }}</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
