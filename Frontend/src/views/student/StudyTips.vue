<script setup>
import PageHeader from "../../components/student/PageHeader.vue"
import { LightBulbIcon } from "@heroicons/vue/24/outline"
import { studyTips } from "../../data/studentMockData"
</script>

<template>
  <div>
    <PageHeader title="Personalized Study Tips" subtitle="Recommendations from your tutor, based on your recent performance." />

    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      <div v-for="t in studyTips" :key="t.id" class="card card-hover p-5">
        <div class="w-10 h-10 rounded-xl bg-amber/10 text-amber-600 dark:text-amber flex items-center justify-center mb-3">
          <LightBulbIcon class="w-5 h-5" />
        </div>
        <p class="text-xs font-semibold text-brand-blue mb-1.5">{{ t.subject }}</p>
        <p class="text-sm">{{ t.tip }}</p>
      </div>
    </div>
  </div>
</template>
