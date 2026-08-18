<script setup>
import { ref, onMounted } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import StatusBadge from '../../components/student/StatusBadge.vue'
import { studentApi } from '../../services/studentApi'

const data = ref({
  upcoming: [],
  completed: []
})

const loading = ref(true)
const error = ref('')

async function loadSessions() {
  loading.value = true
  error.value = ''

  try {
    const r = await studentApi.getSessions()

    data.value = r.data || {
      upcoming: [],
      completed: []
    }
  } catch (e) {
    error.value = e?.message || 'Unable to load sessions.'
  } finally {
    loading.value = false
  }
}

onMounted(loadSessions)
</script>

<template>
  <div>

    <!-- Header -->
    <PageHeader
      title="My Sessions"
      subtitle="View your booked tuition sessions."
    />

    <!-- Loading -->
    <div
      v-if="loading"
      class="py-10 text-center text-sm text-slate-500"
    >
      Loading sessions...
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="mb-5 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-600"
    >
      {{ error }}

      <button
        class="ml-2 font-semibold underline"
        @click="loadSessions"
      >
        Retry
      </button>
    </div>

    <template v-else>

      <!-- Upcoming -->
      <section class="mb-7">

        <div class="mb-3 flex items-center justify-between">
          <div>
            <h3 class="font-display text-lg font-bold text-slate-800 dark:text-white">
              Upcoming Sessions
            </h3>

            <p class="text-xs text-slate-500">
              Your scheduled tuition sessions
            </p>
          </div>

          <span
            v-if="data.upcoming.length"
            class="rounded-full bg-teal-50 px-3 py-1 text-xs font-semibold text-teal-700"
          >
            {{ data.upcoming.length }}
            {{ data.upcoming.length === 1 ? 'session' : 'sessions' }}
          </span>
        </div>

        <!-- No upcoming -->
        <div
          v-if="!data.upcoming.length"
          class="card px-5 py-5 text-sm text-slate-500"
        >
          No upcoming sessions booked.
        </div>

        <!-- Upcoming list -->
        <div
          v-else
          class="space-y-2.5"
        >

          <div
            v-for="s in data.upcoming"
            :key="s.id"
            class="group flex items-center gap-4 rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm transition hover:border-teal-200 hover:shadow-md dark:border-slate-700 dark:bg-slate-900"
          >

            <!-- Subject -->
            <div
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-teal-500 text-sm font-bold text-white"
            >
              {{ s.subject?.charAt(0)?.toUpperCase() || '?' }}
            </div>

            <!-- Main -->
            <div class="min-w-0 flex-1">

              <div class="flex flex-wrap items-center gap-2">

                <h4 class="font-display font-bold text-slate-800 dark:text-white">
                  {{ s.subject }}
                </h4>

                <StatusBadge :status="s.status" />

              </div>

              <div class="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">

                <span>
                  👨‍🏫 {{ s.tutor }}
                </span>

                <span>
                  📅 {{ s.date }}
                </span>

                <span>
                  🕐 {{ s.time }}
                </span>

                <span v-if="s.duration">
                  ⏱ {{ s.duration }}
                </span>

                <span v-if="s.type">
                  {{ s.type }}
                </span>

              </div>

            </div>

            <!-- Join -->
            <a
              v-if="s.meeting_url || s.meetingUrl"
              :href="s.meeting_url || s.meetingUrl"
              target="_blank"
              rel="noopener noreferrer"
              class="shrink-0 rounded-lg bg-gradient-to-r from-teal-500 to-blue-500 px-4 py-2 text-xs font-bold text-white transition hover:opacity-90"
            >
              Join
            </a>

          </div>

        </div>
      </section>


      <!-- Completed -->
      <section>

        <div class="mb-3">
          <h3 class="font-display text-lg font-bold text-slate-800 dark:text-white">
            Completed Sessions
          </h3>

          <p class="text-xs text-slate-500">
            Your previous tuition sessions
          </p>
        </div>

        <!-- No completed -->
        <div
          v-if="!data.completed.length"
          class="card px-5 py-5 text-sm text-slate-500"
        >
          No completed sessions yet.
        </div>

        <!-- Completed list -->
        <div
          v-else
          class="space-y-2"
        >

          <div
            v-for="s in data.completed"
            :key="s.id"
            class="flex items-center gap-4 rounded-xl border border-slate-200 bg-white px-4 py-3 dark:border-slate-700 dark:bg-slate-900"
          >

            <!-- Subject -->
            <div
              class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-sm font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-300"
            >
              {{ s.subject?.charAt(0)?.toUpperCase() || '?' }}
            </div>

            <!-- Info -->
            <div class="min-w-0 flex-1">

              <div class="flex flex-wrap items-center gap-2">

                <h4 class="font-semibold text-slate-800 dark:text-white">
                  {{ s.subject }}
                </h4>

                <StatusBadge :status="s.status" />

              </div>

              <div class="mt-1 flex flex-wrap gap-x-4 text-xs text-slate-500">

                <span>
                  👨‍🏫 {{ s.tutor }}
                </span>

                <span>
                  📅 {{ s.date }} · {{ s.time }}
                </span>

              </div>

              <div
                v-if="s.topics?.length || s.homework"
                class="mt-1 text-xs text-slate-400"
              >
                <span v-if="s.topics?.length">
                  Topics: {{ s.topics.join(', ') }}
                </span>

                <span v-if="s.homework" class="ml-3">
                  Homework: {{ s.homework }}
                </span>
              </div>

            </div>

          </div>

        </div>

      </section>

    </template>

  </div>
</template>