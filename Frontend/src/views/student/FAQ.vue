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
  <div
    class="
      min-h-full
      bg-slate-50
      dark:bg-[#080d1d]
      text-slate-800
      dark:text-slate-100
      transition-colors
      duration-200
    "
  >

    <!-- Page Header -->
    <PageHeader
      title="Frequently Asked Questions"
      subtitle="Answers published by your tutor."
    />

    <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-5">

      <!-- Search + Count -->
      <div class="mb-5">
        <div class="flex flex-col sm:flex-row sm:items-center gap-3">

          <!-- Search -->
          <div class="relative flex-1 max-w-3xl">

            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="
                absolute
                left-3.5
                top-1/2
                -translate-y-1/2
                w-5
                h-5
                text-slate-400
                dark:text-slate-500
              "
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              stroke-width="2"
            >
              <circle cx="11" cy="11" r="7" />
              <path d="m20 20-3.5-3.5" />
            </svg>

            <input
              v-model="q"
              type="text"
              placeholder="Search FAQs..."
              class="
                w-full
                pl-11
                pr-10
                py-3
                rounded-xl
                border
                border-slate-200
                dark:border-slate-700
                bg-white
                dark:bg-[#11182b]
                text-sm
                text-slate-700
                dark:text-slate-200
                placeholder:text-slate-400
                dark:placeholder:text-slate-500
                shadow-sm
                outline-none
                transition-all
                duration-200
                focus:border-brand-blue
                focus:ring-2
                focus:ring-brand-blue/20
              "
            />

            <!-- Clear -->
            <button
              v-if="q"
              type="button"
              @click="q = ''"
              class="
                absolute
                right-3
                top-1/2
                -translate-y-1/2
                w-6
                h-6
                rounded-md
                flex
                items-center
                justify-center
                text-slate-400
                hover:text-slate-700
                dark:hover:text-white
                hover:bg-slate-100
                dark:hover:bg-slate-800
                transition
              "
              aria-label="Clear search"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <path d="M6 6l12 12M18 6 6 18" />
              </svg>
            </button>

          </div>

          <!-- Question Count -->
          <div
            v-if="!loading"
            class="
              self-start
              sm:self-auto
              inline-flex
              items-center
              gap-2
              px-3
              py-2.5
              rounded-xl
              border
              border-slate-200
              dark:border-slate-700
              bg-white
              dark:bg-[#11182b]
              shadow-sm
              text-xs
              font-semibold
              text-slate-500
              dark:text-slate-400
            "
          >
            <span
              class="
                w-1.5
                h-1.5
                rounded-full
                bg-brand-blue
                shadow-[0_0_6px_rgba(37,99,235,0.5)]
              "
            ></span>

            {{ filtered.length }}
            {{ filtered.length === 1 ? 'Question' : 'Questions' }}
          </div>

        </div>
      </div>

      <!-- Loading -->
      <div
        v-if="loading"
        class="
          max-w-4xl
          rounded-2xl
          border
          border-slate-200
          dark:border-slate-700
          bg-white
          dark:bg-[#11182b]
          overflow-hidden
          shadow-sm
        "
      >
        <div
          v-for="n in 5"
          :key="n"
          class="
            px-4
            py-4
            border-b
            last:border-b-0
            border-slate-100
            dark:border-slate-800
            animate-pulse
          "
        >
          <div
            class="
              h-4
              bg-slate-200
              dark:bg-slate-700
              rounded
              w-3/4
            "
          ></div>
        </div>
      </div>

      <!-- Empty -->
      <div
        v-else-if="!filtered.length"
        class="
          max-w-4xl
          rounded-2xl
          border
          border-slate-200
          dark:border-slate-700
          bg-white
          dark:bg-[#11182b]
          shadow-sm
          px-5
          py-9
          text-center
        "
      >
        <div
          class="
            mx-auto
            w-11
            h-11
            rounded-xl
            bg-blue-50
            dark:bg-blue-500/10
            flex
            items-center
            justify-center
            text-brand-blue
            mb-3
          "
        >
          <svg
            width="19"
            height="19"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.8"
          >
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-3.5-3.5" />
          </svg>
        </div>

        <p
          class="
            text-sm
            font-semibold
            text-slate-700
            dark:text-slate-200
          "
        >
          No FAQs found
        </p>

        <p
          class="
            text-xs
            text-slate-400
            dark:text-slate-500
            mt-1
          "
        >
          Try searching with a different keyword.
        </p>
      </div>

      <!-- FAQ List -->
      <div
        v-else
        class="
          max-w-4xl
          rounded-2xl
          border
          border-slate-200
          dark:border-slate-700
          bg-white
          dark:bg-[#11182b]
          overflow-hidden
          shadow-sm
        "
      >

        <div
          v-for="(f, index) in filtered"
          :key="f.id"
          class="
            group
            border-b
            last:border-b-0
            border-slate-100
            dark:border-slate-800
            transition-colors
            duration-200
          "
          :class="
            open === f.id
              ? 'bg-slate-50 dark:bg-[#151e34]'
              : 'hover:bg-slate-50/80 dark:hover:bg-[#131c30]'
          "
        >

          <!-- Question -->
          <button
            type="button"
            class="
              w-full
              px-4
              py-3.5
              sm:py-4
              flex
              items-center
              gap-3
              text-left
            "
            @click="open = open === f.id ? null : f.id"
          >

            <!-- Number -->
            <span
              class="
                shrink-0
                w-8
                h-8
                rounded-lg
                flex
                items-center
                justify-center
                text-[10px]
                font-bold
                transition-all
                duration-200
              "
              :class="
                open === f.id
                  ? 'bg-brand-blue text-white shadow-sm'
                  : 'bg-blue-50 dark:bg-blue-500/10 text-brand-blue'
              "
            >
              {{ String(index + 1).padStart(2, '0') }}
            </span>

            <!-- Question -->
            <span
              class="
                flex-1
                text-sm
                font-semibold
                leading-5
                text-slate-700
                dark:text-slate-200
              "
            >
              {{ f.q }}
            </span>

            <!-- Chevron -->
            <span
              class="
                shrink-0
                w-7
                h-7
                rounded-lg
                flex
                items-center
                justify-center
                text-slate-400
                dark:text-slate-500
                transition-all
                duration-200
              "
              :class="
                open === f.id
                  ? 'bg-blue-50 dark:bg-blue-500/10 text-brand-blue'
                  : 'group-hover:bg-slate-100 dark:group-hover:bg-slate-800'
              "
            >
              <svg
                width="15"
                height="15"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.2"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="transition-transform duration-200"
                :class="open === f.id ? 'rotate-180' : ''"
              >
                <path d="m6 9 6 6 6-6" />
              </svg>
            </span>

          </button>

          <!-- Answer -->
          <div
            v-if="open === f.id"
            class="
              px-4
              pb-4
              pl-[3.75rem]
              sm:pl-[4.5rem]
            "
          >
            <div
              class="
                border-l-2
                border-brand-blue/30
                pl-4
              "
            >
              <p
                class="
                  text-xs
                  sm:text-sm
                  leading-6
                  text-slate-500
                  dark:text-slate-400
                "
              >
                {{ f.a }}
              </p>
            </div>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>