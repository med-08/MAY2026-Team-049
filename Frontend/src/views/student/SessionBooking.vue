<script setup>
import { ref, computed, onMounted } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import ConfirmModal from '../../components/ui/ConfirmModal.vue'
import { useToast } from '../../composables/useToast'
import { studentApi } from '../../services/studentApi'

const { showToast } = useToast()

const tab = ref('regular')
const slots = ref({ regular: [], oneToOne: [] })
const loading = ref(true)
const error = ref('')
const busy = ref(null)

const confirmOpen = ref(false)
const pendingSlot = ref(null)

const active = computed(() => slots.value[tab.value] || [])

const availableCount = computed(() =>
  active.value.filter(s => !s.booked).length
)

const subjectIcon = subject => {
  const icons = {
    English: '📚',
    Mathematics: '📐',
    Physics: '⚛️',
    Chemistry: '🧪',
    Biology: '🧬',
    Science: '🔬'
  }

  return icons[subject] || '📖'
}

const subjectColor = subject => {
  const colors = {
    English: 'bg-blue-50 text-blue-600',
    Mathematics: 'bg-violet-50 text-violet-600',
    Physics: 'bg-cyan-50 text-cyan-600',
    Chemistry: 'bg-emerald-50 text-emerald-600',
    Biology: 'bg-green-50 text-green-600',
    Science: 'bg-orange-50 text-orange-600'
  }

  return colors[subject] || 'bg-indigo-50 text-indigo-600'
}

/*
 * SESSION TYPE COLOUR CONVENTION
 *
 * Regular  -> blue    (matches the tutor schedule badge)
 * One-to-One -> violet (matches the tutor schedule badge)
 *
 * Used consistently: badge colour + left accent border on the card,
 * so a student can tell the two apart at a glance without reading text.
 */
const isOneToOne = s => (s.type || '').toLowerCase().includes('one')

const typeBadgeClasses = s =>
  isOneToOne(s)
    ? 'bg-violet-50 text-violet-700 dark:bg-violet-900/20 dark:text-violet-300'
    : 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300'

const typeAccentClasses = s =>
  isOneToOne(s)
    ? 'border-l-4 border-l-violet-400 dark:border-l-violet-500'
    : 'border-l-4 border-l-blue-400 dark:border-l-blue-500'

async function acknowledgeNewSessionNotifications() {
  try {
    const res = await studentApi.getNotifications()
    const unread = (res?.data?.notifications || []).filter(
      n => !n.isRead && n.type === 'Session Available'
    )
    await Promise.all(unread.map(n => studentApi.markNotificationRead(n.id)))
  } catch {
    // Notification acknowledgement is non-blocking for booking.
  }
}

async function load() {
  loading.value = true
  error.value = ''

  try {
    const r = await studentApi.getBookingSlots()

    slots.value = r.data?.bookingSlots || {
      regular: [],
      oneToOne: []
    }
  } catch (e) {
    error.value = e?.message || 'Unable to load available sessions.'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await acknowledgeNewSessionNotifications()
  await load()
})

function openConfirm(s) {
  if (s.booked || busy.value) return

  pendingSlot.value = s
  confirmOpen.value = true
}

function cancelConfirm() {
  confirmOpen.value = false
  pendingSlot.value = null
}

async function confirmBooking() {
  const s = pendingSlot.value

  confirmOpen.value = false

  if (!s || busy.value) return

  busy.value = s.id

  try {
    await studentApi.bookSession(s.id)

    showToast(
      `Session booked - ${s.subject} with ${s.tutor} on ${s.date} at ${s.time}`,
      'success'
    )

    await load()
  } catch (e) {
    showToast(
      e?.message || 'Could not book this session. Please try again.',
      'error'
    )
  } finally {
    busy.value = null
    pendingSlot.value = null
  }
}
</script>

<template>
  <div class="space-y-6">

    <!-- Header -->
    <PageHeader
      title="Session Booking"
      subtitle="Choose an available session from your tutor's schedule."
    />

    <!-- Tabs + Count -->
    <div class="flex flex-wrap items-center justify-between gap-3">

      <div
        class="inline-flex rounded-xl bg-slate-100 p-1 dark:bg-white/5"
      >
        <button
          type="button"
          class="rounded-lg px-5 py-2 text-sm font-semibold transition"
          :class="
            tab === 'regular'
              ? 'bg-white text-teal-700 shadow-sm dark:bg-slate-800 dark:text-teal-300'
              : 'text-slate-500 hover:text-slate-700'
          "
          @click="tab = 'regular'"
        >
          Regular Sessions
        </button>

        <button
          type="button"
          class="rounded-lg px-5 py-2 text-sm font-semibold transition"
          :class="
            tab === 'oneToOne'
              ? 'bg-white text-teal-700 shadow-sm dark:bg-slate-800 dark:text-teal-300'
              : 'text-slate-500 hover:text-slate-700'
          "
          @click="tab = 'oneToOne'"
        >
          One-to-One
        </button>
      </div>

      <span
        v-if="!loading && !error"
        class="rounded-full bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300"
      >
        {{ availableCount }} available
      </span>

    </div>

    <!-- Loading -->
    <div
      v-if="loading"
      class="card p-8 text-center"
    >
      <div
        class="mx-auto mb-3 h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-teal-500"
      ></div>

      <p class="text-sm font-medium text-slate-600 dark:text-slate-300">
        Loading available sessions...
      </p>
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="rounded-2xl border border-red-200 bg-red-50 p-5 dark:border-red-900/40 dark:bg-red-950/20"
    >
      <div class="flex items-center justify-between gap-4">
        <div>
          <p class="font-semibold text-red-700 dark:text-red-300">
            Unable to load sessions
          </p>

          <p class="mt-1 text-sm text-red-600 dark:text-red-400">
            {{ error }}
          </p>
        </div>

        <button
          type="button"
          class="shrink-0 rounded-xl bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700"
          @click="load"
        >
          Retry
        </button>
      </div>
    </div>

    <!-- Empty -->
    <div
      v-else-if="!active.length"
      class="card p-10 text-center"
    >
      <div
        class="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-2xl dark:bg-slate-800"
      >
        📅
      </div>

      <h3 class="mt-4 font-display font-bold text-slate-800 dark:text-white">
        No sessions available
      </h3>

      <p class="mx-auto mt-1 max-w-md text-sm text-slate-500">
        Your tutor hasn't added any {{ tab === 'regular' ? 'regular' : 'one-to-one' }}
        sessions yet.
      </p>
    </div>

    <!-- Session Cards -->
    <div
      v-else
      class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3"
    >

      <article
        v-for="s in active"
        :key="s.id"
        class="group overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-lg dark:border-slate-700 dark:bg-slate-900"
        :class="typeAccentClasses(s)"
      >

        <!-- Subject -->
        <div class="flex items-center justify-between border-b border-slate-100 p-4 dark:border-slate-700">

          <div class="flex items-center gap-3">

            <div
              class="flex h-11 w-11 items-center justify-center rounded-xl text-xl"
              :class="subjectColor(s.subject)"
            >
              {{ subjectIcon(s.subject) }}
            </div>

            <div>
              <p class="text-xs text-slate-400">
                Subject
              </p>

              <h3 class="font-display font-bold text-slate-800 dark:text-white">
                {{ s.subject }}
              </h3>
            </div>

          </div>

          <div class="flex flex-col items-end gap-1.5">

            <span
              class="rounded-full px-2.5 py-1 text-[10px] font-extrabold uppercase tracking-wide"
              :class="typeBadgeClasses(s)"
            >
              {{ isOneToOne(s) ? 'One-to-One' : 'Regular' }}
            </span>

            <span
              class="rounded-full px-2.5 py-1 text-[11px] font-bold"
              :class="
                s.booked
                  ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-300'
                  : 'bg-emerald-50 text-emerald-600 dark:bg-emerald-900/20 dark:text-emerald-300'
              "
            >
              {{ s.booked ? 'Booked' : 'Available' }}
            </span>

          </div>

        </div>

        <!-- Details -->
        <div class="p-4">

          <div class="space-y-3 text-sm">

            <div class="flex items-center gap-3">
              <span class="text-base">👨‍🏫</span>

              <div>
                <p class="text-xs text-slate-400">
                  Tutor
                </p>

                <p class="font-medium text-slate-700 dark:text-slate-200">
                  {{ s.tutor }}
                </p>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <span class="text-base">📅</span>

              <div>
                <p class="text-xs text-slate-400">
                  Date & Time
                </p>

                <p class="font-medium text-slate-700 dark:text-slate-200">
                  {{ s.date }} · {{ s.time }}
                </p>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <span class="text-base">🎓</span>

              <div>
                <p class="text-xs text-slate-400">
                  Session Type
                </p>

                <span
                  class="mt-0.5 inline-block rounded-md px-2 py-0.5 text-xs font-bold"
                  :class="typeBadgeClasses(s)"
                >
                  {{ s.meeting_type_label || (isOneToOne(s) ? 'One-on-One Session' : 'Regular Session') }}
                </span>
              </div>
            </div>

            <!-- Created by -->
            <div
              v-if="s.created_by_label"
              class="flex items-center gap-3"
            >
              <span class="text-base">👤</span>

              <div>
                <p class="text-xs text-slate-400">
                  Created By
                </p>

                <p class="font-medium text-slate-700 dark:text-slate-200">
                  {{ s.created_by_label }}
                </p>
              </div>
            </div>

            <!-- Reason -->
            <div
              v-if="s.meeting_reason"
              class="flex items-start gap-3"
            >
              <span class="text-base">📝</span>

              <div class="min-w-0">
                <p class="text-xs text-slate-400">
                  Reason
                </p>

                <p class="font-medium text-slate-700 dark:text-slate-200 break-words">
                  {{ s.meeting_reason }}
                </p>
              </div>
            </div>

          </div>

          <!-- Book Button -->
          <button
            v-if="!s.booked"
            type="button"
            class="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-teal-500 to-blue-500 px-4 py-3 text-sm font-bold text-white shadow-sm transition-all hover:-translate-y-0.5 hover:shadow-md disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="busy === s.id"
            @click="openConfirm(s)"
          >
            <span>
              {{ busy === s.id ? '⏳' : '📅' }}
            </span>

            {{ busy === s.id ? 'Booking...' : 'Book Session' }}
          </button>

          <!-- Already booked -->
          <div
            v-else
            class="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-blue-50 px-4 py-3 text-sm font-semibold text-blue-700 dark:bg-blue-900/20 dark:text-blue-300"
          >
            ✓ Already Booked
          </div>

        </div>

      </article>

    </div>

    <!-- Confirmation -->
    <ConfirmModal
      :open="confirmOpen"
      tone="positive"
      title="Confirm your booking"
      :message="
        pendingSlot
          ? `Book ${pendingSlot.subject} with ${pendingSlot.tutor} on ${pendingSlot.date} at ${pendingSlot.time}?`
          : ''
      "
      confirm-label="Book Session"
      @cancel="cancelConfirm"
      @confirm="confirmBooking"
    />

  </div>
</template>