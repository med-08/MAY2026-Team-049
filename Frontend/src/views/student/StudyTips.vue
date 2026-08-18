<script setup>
import { ref, onMounted } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import { studentApi } from '../../services/studentApi'

const tips = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const r = await studentApi.getStudyTips()
    tips.value = r.data?.studyTips || []
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <PageHeader
      title="Study Tips"
      subtitle="Tips recorded by your tutor for you."
    />

    <div class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

      <!-- Loading State -->
      <div
        v-if="loading"
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"
      >
        <div
          v-for="n in 6"
          :key="n"
          class="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm animate-pulse"
        >
          <div class="h-5 w-24 bg-slate-200 rounded-full mb-5"></div>
          <div class="h-4 bg-slate-200 rounded w-full mb-3"></div>
          <div class="h-4 bg-slate-200 rounded w-5/6 mb-3"></div>
          <div class="h-4 bg-slate-200 rounded w-2/3"></div>
        </div>
      </div>

      <!-- Error State -->
      <div
        v-else-if="error"
        class="bg-red-50 border border-red-200 rounded-2xl p-6 flex items-start gap-4"
      >
        <div
          class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center shrink-0"
        >
          <span class="text-red-600 text-lg">!</span>
        </div>

        <div>
          <h3 class="font-semibold text-red-800">
            Unable to load study tips
          </h3>
          <p class="text-sm text-red-600 mt-1">
            {{ error }}
          </p>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!tips.length"
        class="bg-white rounded-2xl border border-slate-200 shadow-sm p-10 text-center"
      >
        <div
          class="mx-auto w-16 h-16 rounded-full bg-blue-50 flex items-center justify-center mb-5"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="w-8 h-8 text-brand-blue"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="1.8"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5S19.832 5.477 21 6.253v13C19.832 18.477 18.246 18 16.5 18s-3.332.477-4.5 1.253"
            />
          </svg>
        </div>

        <h3 class="text-lg font-semibold text-slate-800">
          No study tips yet
        </h3>

        <p class="text-sm text-slate-500 mt-2 max-w-md mx-auto">
          Your tutor hasn't added any study tips yet. Check back later for
          helpful advice and guidance.
        </p>
      </div>

      <!-- Study Tips -->
      <div
        v-else
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5"
      >
        <div
          v-for="t in tips"
          :key="t.id"
          class="group bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-200"
        >
          <!-- Top Section -->
          <div class="flex items-center justify-between gap-3 mb-5">
            <span
              class="inline-flex items-center px-3 py-1.5 rounded-full bg-blue-50 text-brand-blue text-xs font-semibold"
            >
              {{ t.subject }}
            </span>

            <div
              class="w-9 h-9 rounded-full bg-slate-50 group-hover:bg-blue-50 flex items-center justify-center transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                class="w-5 h-5 text-slate-400 group-hover:text-brand-blue transition-colors"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                stroke-width="1.8"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M12 18.5a6.5 6.5 0 100-13 6.5 6.5 0 000 13z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M12 8.5v4l2.5 1.5"
                />
              </svg>
            </div>
          </div>

          <!-- Tip -->
          <p class="text-slate-700 text-sm leading-6">
            {{ t.tip }}
          </p>

          <!-- Bottom Accent -->
          <div
            class="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2"
          >
            <div class="w-1.5 h-1.5 rounded-full bg-brand-blue"></div>
            <span class="text-xs text-slate-400">
              Tutor's study tip
            </span>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>