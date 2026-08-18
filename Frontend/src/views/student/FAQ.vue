<script setup>
import { ref, computed, onMounted } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import { studentApi } from '../../services/studentApi'

const faqs = ref([])
const q = ref('')
const open = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const r = await studentApi.getFaqs()
    faqs.value = r.data?.faqs || []
  } finally {
    loading.value = false
  }
})

const filtered = computed(() => {
  const x = q.value.toLowerCase()
  return faqs.value.filter(
    f =>
      !x ||
      f.q.toLowerCase().includes(x) ||
      f.a.toLowerCase().includes(x)
  )
})
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <PageHeader
      title="Frequently Asked Questions"
      subtitle="Answers published by your tutor."
    />

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">

      <!-- Search Section -->
      <div class="mb-7">
        <div class="relative max-w-3xl">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="m21 21-4.35-4.35m2.1-5.4a7.5 7.5 0 1 1-15 0 7.5 7.5 0 0 1 15 0z"
            />
          </svg>

          <input
            v-model="q"
            class="w-full pl-12 pr-4 py-3.5 rounded-2xl border border-slate-200 bg-white shadow-sm outline-none text-sm text-slate-700 placeholder:text-slate-400 focus:border-brand-blue focus:ring-4 focus:ring-blue-50 transition"
            placeholder="Search FAQs..."
          />
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="max-w-3xl space-y-3">
        <div
          v-for="n in 5"
          :key="n"
          class="bg-white rounded-2xl border border-slate-200 p-5 shadow-sm animate-pulse"
        >
          <div class="h-4 bg-slate-200 rounded w-3/4"></div>
          <div class="h-3 bg-slate-100 rounded w-1/3 mt-3"></div>
        </div>
      </div>

      <!-- Empty State -->
      <div
        v-else-if="!filtered.length"
        class="max-w-3xl bg-white rounded-2xl border border-slate-200 shadow-sm p-10 text-center"
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
              d="M9.5 9a3 3 0 1 1 5.3 1.9c-.8.9-1.8 1.3-2.3 2.6"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="M12 17.5h.01"
            />
            <circle
              cx="12"
              cy="12"
              r="9"
            />
          </svg>
        </div>

        <h3 class="text-lg font-semibold text-slate-800">
          No FAQs available
        </h3>

        <p class="text-sm text-slate-500 mt-2">
          No questions matched your search. Try using different keywords.
        </p>
      </div>

      <!-- FAQ List -->
      <div
        v-else
        class="max-w-3xl space-y-3"
      >
        <div
          v-for="f in filtered"
          :key="f.id"
          class="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden transition-all duration-200 hover:shadow-md"
          :class="open === f.id ? 'border-blue-200 shadow-md' : ''"
        >
          <!-- Question -->
          <button
            class="w-full p-5 text-left flex items-center justify-between gap-5 hover:bg-slate-50 transition-colors"
            @click="open = open === f.id ? null : f.id"
          >
            <div class="flex items-start gap-4">
              <div
                class="w-9 h-9 rounded-full bg-blue-50 text-brand-blue flex items-center justify-center shrink-0 text-sm font-bold"
              >
                ?
              </div>

              <span
                class="font-semibold text-slate-800 text-sm sm:text-base leading-6"
              >
                {{ f.q }}
              </span>
            </div>

            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-5 h-5 text-slate-400 shrink-0 transition-transform duration-200"
              :class="open === f.id ? 'rotate-180 text-brand-blue' : ''"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                d="m6 9 6 6 6-6"
              />
            </svg>
          </button>

          <!-- Answer -->
          <div
            v-if="open === f.id"
            class="border-t border-slate-100 bg-slate-50/70"
          >
            <div class="px-5 py-5 pl-[4.5rem]">
              <p class="text-sm text-slate-600 leading-6">
                {{ f.a }}
              </p>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>