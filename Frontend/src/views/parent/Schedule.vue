<script setup>
import { computed, ref } from 'vue'
import { VideoCameraIcon, ClockIcon } from '@heroicons/vue/24/outline'
import EmptyState from '../../components/ui/EmptyState.vue'
import { useToast } from '../../composables/useToast'
import { useParentPortal } from '../../composables/useParentPortal'

const { showToast } = useToast()
const { children, upcomingSessionsList, completedSessions } = useParentPortal(1)

const selectedChildId = ref(children.value[0]?.student_id)
const selectedChild = computed(() => children.value.find((c) => c.student_id === selectedChildId.value))

const upcoming = computed(() => upcomingSessionsList(selectedChildId.value))
const past = computed(() => completedSessions(selectedChildId.value))

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })
}
</script>

<template>
  <div v-if="selectedChild" class="space-y-6">
    <div v-if="children.length > 1" class="flex items-center gap-2">
      <button
        v-for="child in children"
        :key="child.student_id"
        class="pill-filter"
        :class="selectedChildId === child.student_id
          ? 'bg-gradient-to-r from-brand-green-500 to-brand-blue-500 text-white border-transparent'
          : 'text-slate-500 dark:text-slate-400 border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800'"
        @click="selectedChildId = child.student_id"
      >
        {{ child.student_name }}
      </button>
    </div>

    <!-- Upcoming -->
    <div class="card p-5">
      <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4 flex items-center gap-2">
        <ClockIcon class="w-5 h-5 text-brand-blue-500" />
        Upcoming Sessions
      </h3>
      <div v-if="upcoming.length" class="grid sm:grid-cols-2 gap-4">
        <div v-for="s in upcoming" :key="s.session_id" class="rounded-xl bg-grad-blue dark:bg-slate-800/60 p-4">
          <p class="text-xs font-semibold uppercase tracking-wider text-brand-blue-700 dark:text-brand-blue-400">{{ s.session_type }}</p>
          <p class="mt-1 font-display font-bold text-slate-800 dark:text-slate-100">{{ s.subjectName }}</p>
          <p class="text-sm text-slate-600 dark:text-slate-300 mt-1">with {{ s.tutorName }}</p>
          <p class="text-sm text-slate-500 dark:text-slate-400 mt-2">{{ formatDate(s.session_date) }}</p>
          <p class="text-sm text-slate-500 dark:text-slate-400">{{ s.start_time }} – {{ s.end_time }}</p>
          <button class="btn-primary mt-4 w-full justify-center" @click="showToast('Joining session...')">
            <VideoCameraIcon class="w-4 h-4" />
            Join Session
          </button>
        </div>
      </div>
      <EmptyState v-else title="No upcoming sessions" message="Nothing booked yet for this child." />
    </div>

    <!-- Past -->
    <div class="card p-5">
      <h3 class="font-display font-semibold text-slate-800 dark:text-slate-100 mb-4">Past Sessions</h3>
      <div v-if="past.length" class="space-y-3">
        <div v-for="s in past" :key="s.session_id" class="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60">
          <div class="flex items-center justify-between">
            <p class="text-sm font-semibold text-slate-800 dark:text-slate-100">{{ s.subjectName }} · {{ s.session_type }}</p>
            <span class="text-xs text-slate-400">{{ formatDate(s.session_date) }}</span>
          </div>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">with {{ s.tutorName }} · {{ s.start_time }} – {{ s.end_time }}</p>
          <div v-if="s.update" class="mt-3 pt-3 border-t border-slate-200 dark:border-slate-700 text-sm space-y-1">
            <p class="text-slate-600 dark:text-slate-300"><span class="font-semibold text-slate-700 dark:text-slate-200">Topics covered:</span> {{ s.update.topics_covered }}</p>
            <p class="text-slate-600 dark:text-slate-300"><span class="font-semibold text-slate-700 dark:text-slate-200">Homework:</span> {{ s.update.homework_assigned }}</p>
          </div>
        </div>
      </div>
      <EmptyState v-else title="No past sessions yet" message="Completed sessions will show up here." />
    </div>
  </div>
</template>
