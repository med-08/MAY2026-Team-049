<script setup>
import PageHeader from "../../components/student/PageHeader.vue"
import { CalendarDaysIcon, TrophyIcon } from "@heroicons/vue/24/outline"
import { weeklyQuizzes } from "../../data/studentMockData"
</script>

<template>
  <div>
    <PageHeader
      title="Weekly Quiz"
      subtitle="Attempt your weekly quizzes and track your previous performance."
    />

    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">

      <div
        v-for="q in weeklyQuizzes"
        :key="q.quiz_id"
        class="card card-hover p-5 flex flex-col"
      >

        <!-- Subject -->
        <p class="text-sm font-semibold text-brand-blue mb-2">
          {{ q.subject }}
        </p>

        <!-- Quiz Title -->
        <h3 class="text-lg font-display font-bold mb-4">
          {{ q.title }}
        </h3>

        <!-- Week -->
        <div
          class="flex items-center gap-2 text-sm text-ink-soft dark:text-slate-300 mb-3"
        >
          <CalendarDaysIcon class="w-5 h-5" />
          <span>Week {{ q.weekNumber }}</span>
        </div>

        <!-- Last Attempt -->
        <div
          class="flex justify-between text-sm border-b border-slate-200 dark:border-border-dark pb-3 mb-3"
        >
          <span class="text-ink-soft dark:text-slate-400">
            Last Attempt
          </span>

          <span class="font-medium">
            {{ q.lastAttempt || "Not Attempted" }}
          </span>
        </div>

        <!-- Previous Score -->
        <div
          class="flex justify-between text-sm mb-5"
        >
          <span class="text-ink-soft dark:text-slate-400">
            Previous Score
          </span>

          <span class="font-semibold flex items-center gap-1">
            <TrophyIcon class="w-4 h-4 text-yellow-500" />

            {{ q.score !== null ? q.score + "%" : "--" }}
          </span>
        </div>

        <!-- Button -->
        <RouterLink
          :to="`/student/quiz/${q.quiz_id}`"
          class="mt-auto w-full py-2.5 rounded-xl font-semibold text-sm text-center bg-cyan-100 text-cyan-700 hover:bg-cyan-200 dark:bg-cyan-500/15 dark:text-cyan-300 dark:hover:bg-cyan-500/25 transition"
        >
          {{ q.score !== null ? "Retake Quiz" : "Take Quiz" }}
        </RouterLink>

      </div>

    </div>
  </div>
</template>