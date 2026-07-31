<script setup>
import { ref, computed } from "vue"
import PageHeader from "../../components/student/PageHeader.vue"
import { ChevronDownIcon, MagnifyingGlassIcon } from "@heroicons/vue/24/outline"
import { faqs } from "../../data/studentMockData"

const openId = ref(faqs[0]?.id ?? null)
const searchQuery = ref("")

function toggle(id) {
  openId.value = openId.value === id ? null : id
}

const filteredFaqs = computed(() => {
  if (!searchQuery.value.trim()) return faqs

  const query = searchQuery.value.toLowerCase()

  return faqs.filter(
    (faq) =>
      faq.q.toLowerCase().includes(query) ||
      faq.a.toLowerCase().includes(query)
  )
})
</script>
<template>
  <div>
    <PageHeader
      title="Frequently Asked Questions"
      subtitle="Quick answers about sessions, quizzes, homework, and more."
    />

    <!-- Search Bar -->
    <div class="max-w-2xl mb-5">
      <div class="relative">
        <MagnifyingGlassIcon
          class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400"
        />

        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search FAQs..."
          class="w-full pl-11 pr-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-blue"
        />
      </div>
    </div>

    <!-- FAQ List -->
    <div class="max-w-2xl space-y-3">
      <div
        v-for="f in filteredFaqs"
        :key="f.id"
        class="card overflow-hidden"
      >
        <button
          class="w-full flex items-center justify-between gap-4 px-5 py-4 text-left transition"
          :class="openId === f.id ? 'bg-sky-100 dark:bg-sky-500/15' : 'hover:bg-sky-50 dark:hover:bg-sky-500/10'"
          @click="toggle(f.id)"
        >
          <span class="text-sm font-semibold" :class="openId === f.id ? 'text-sky-700 dark:text-sky-300' : ''">{{ f.q }}</span>

          <ChevronDownIcon
            class="w-5 h-5 shrink-0 transition-transform duration-200"
            :class="openId === f.id ? 'rotate-180 text-sky-700 dark:text-sky-300' : 'text-ink-soft'"
          />
        </button>

        <div
          v-show="openId === f.id"
          class="px-5 pb-4"
        >
          <p class="text-sm text-ink-soft dark:text-slate-300">
            {{ f.a }}
          </p>
        </div>
      </div>

      <!-- No Results -->
      <div
        v-if="filteredFaqs.length === 0"
        class="card p-8 text-center text-sm text-slate-500"
      >
        No FAQs found matching "<strong>{{ searchQuery }}</strong>".
      </div>
    </div>
  </div>
</template>