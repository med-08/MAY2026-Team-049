<script setup>
import { ref, computed } from "vue"
import PageHeader from "../../components/student/PageHeader.vue"
import { ArrowTopRightOnSquareIcon } from "@heroicons/vue/24/outline"
import { studyResources } from "../../data/studentMockData"

const categories = [
  "All",
  "PDF",
  "Video",
  "Website",
  "Notes",
  "Practice Sheet",
]

const active = ref("All")

const filtered = computed(() =>
  active.value === "All"
    ? studyResources
    : studyResources.filter(
        (resource) => resource.resource_type === active.value
      )
)
</script>

<template>
  <div>
    <PageHeader
      title="Study Resources"
      subtitle="Access learning materials shared by your tutor."
    />

    <!-- Description -->
    <div
      class="card p-4 mb-6"
    >
      <p class="text-sm text-ink-soft dark:text-slate-300 leading-relaxed">
        Browse resources shared for each session, including PDFs, videos,
        notes, websites, and practice sheets. Use the filters below to quickly
        find the material you need.
      </p>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap gap-2 mb-6">
      <button
        v-for="category in categories"
        :key="category"
        @click="active = category"
        class="px-4 py-2 rounded-full text-xs font-semibold transition"
        :class="
          active === category
            ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300'
            : 'bg-slate-100 dark:bg-white/5 text-ink-soft dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-white/10'
        "
      >
        {{ category }}
      </button>
    </div>

    <!-- Resources -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
      <div
        v-for="resource in filtered"
        :key="resource.resource_id"
        class="card card-hover p-5 flex flex-col"
      >
        <!-- Header -->
        <div class="flex items-center justify-between mb-4">
          <span
            class="inline-flex items-center px-3 py-1 rounded-full text-[11px] font-semibold bg-brand-blue/10 text-brand-blue"
          >
            {{ resource.resource_type }}
          </span>

          <span class="text-xs font-semibold text-ink-soft dark:text-slate-400">
            Session {{ resource.session_id }}
          </span>
        </div>

        <!-- Title -->
        <h3 class="font-display text-lg font-bold leading-snug flex-1">
          {{ resource.resource_title }}
        </h3>

        <!-- Open Button -->
        <a
          :href="resource.resource_link"
          target="_blank"
          class="mt-6 w-full flex items-center justify-center gap-2 py-3 rounded-xl font-semibold text-sm bg-emerald-100 text-emerald-700 hover:bg-emerald-200 dark:bg-emerald-500/15 dark:text-emerald-300 dark:hover:bg-emerald-500/25 transition"
        >
          <ArrowTopRightOnSquareIcon class="w-5 h-5" />
          Open Resource
        </a>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-if="filtered.length === 0"
      class="card p-10 text-center mt-6"
    >
      <h3 class="font-display text-lg font-semibold mb-2">
        No resources found
      </h3>
      <p class="text-sm text-ink-soft dark:text-slate-400">
        There are no resources available for the selected category.
      </p>
    </div>
  </div>
</template>