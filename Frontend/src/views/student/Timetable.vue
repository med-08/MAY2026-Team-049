<script setup>
import PageHeader from "../../components/student/PageHeader.vue"
import { timetable } from "../../data/studentMockData"

const colorMap = {
  blue: "bg-brand-blue/10 text-brand-blue border-brand-blue/20",
  green: "bg-brand-green/10 text-brand-green-dark dark:text-brand-green border-brand-green/20",
  amber: "bg-amber/10 text-amber-600 dark:text-amber border-amber/20",
  purple: "bg-violet-500/10 text-violet-600 dark:text-violet-400 border-violet-500/20",
}
</script>

<template>
  <div>
    <PageHeader title="Timetable" subtitle="Your weekly offline tuition schedule at a glance." />

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-4">
      <div v-for="day in timetable.days" :key="day" class="card p-4 min-h-[160px]">
        <h4 class="font-display font-bold text-sm mb-3 text-ink-soft dark:text-slate-300">{{ day }}</h4>

        <div v-if="timetable.classes[day].length" class="space-y-2.5">
          <div
            v-for="(cls, i) in timetable.classes[day]"
            :key="i"
            class="rounded-xl border px-3 py-2.5"
            :class="colorMap[cls.color]"
          >
            <p class="text-sm font-semibold">{{ cls.subject }}</p>
            <p class="text-xs mt-0.5">{{ cls.time }}</p>
            <p class="text-xs opacity-80">{{ cls.tutor }}</p>
          </div>
        </div>
        <p v-else class="text-xs text-ink-soft/60 dark:text-slate-500 mt-2">No class scheduled</p>
      </div>
    </div>
  </div>
</template>
