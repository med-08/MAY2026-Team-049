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

async function load() {
  loading.value = true
  try {
    const r = await studentApi.getBookingSlots()
    slots.value = r.data?.bookingSlots || slots.value
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
onMounted(load)

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
    showToast(`Session booked - ${s.subject} with ${s.tutor} on ${s.date} at ${s.time}`, 'success')
    await load()
  } catch (e) {
    showToast(e.message || 'Could not book this session. Please try again.', 'error')
  } finally {
    busy.value = null
    pendingSlot.value = null
  }
}
</script>

<template>
  <div>
    <PageHeader title="Session Booking" subtitle="Book a real session from your tutor's schedule." />

    <div class="inline-flex p-1 rounded-xl bg-slate-100 dark:bg-white/5 mb-6">
      <button class="px-5 py-2 rounded-lg text-sm font-semibold" :class="tab === 'regular' ? 'bg-teal-100 text-teal-700' : 'text-slate-500'" @click="tab = 'regular'">Regular Sessions</button>
      <button class="px-5 py-2 rounded-lg text-sm font-semibold" :class="tab === 'oneToOne' ? 'bg-teal-100 text-teal-700' : 'text-slate-500'" @click="tab = 'oneToOne'">One-to-One</button>
    </div>

    <p v-if="loading">Loading available sessions...</p>
    <p v-else-if="error" class="text-danger">{{ error }}</p>
    <div v-else-if="!active.length" class="card p-8 text-center text-slate-500">
      No sessions are currently available. Your tutor can add one from the Tutor Schedule.
    </div>
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      <div v-for="s in active" :key="s.id" class="card p-5">
        <div class="flex justify-between mb-3">
          <h4 class="font-display font-bold">{{ s.subject }}</h4>
          <span class="text-xs font-semibold px-2.5 py-1 rounded-full" :class="s.booked ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'">
            {{ s.booked ? 'Booked' : 'Available' }}
          </span>
        </div>
        <div class="space-y-2 text-sm text-slate-500 mb-4">
          <p>{{ s.tutor }}</p>
          <p>{{ s.date }} &middot; {{ s.time }}</p>
          <p>{{ s.type }}</p>
        </div>
        <button
  v-if="!s.booked"
  class="w-full py-2.5 rounded-xl bg-green-50 text-green-700 border border-green-100 font-semibold text-sm hover:bg-green-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
  :disabled="busy === s.id"
  @click="openConfirm(s)"
>
  {{ busy === s.id ? 'Booking...' : 'Book Session' }}
</button>
      </div>
    </div>

    <ConfirmModal
      :open="confirmOpen"
      tone="positive"
      title="Confirm your booking"
      :message="pendingSlot ? `Book ${pendingSlot.subject} with ${pendingSlot.tutor} on ${pendingSlot.date} at ${pendingSlot.time}?` : ''"
      confirm-label="Book Session"
      @cancel="cancelConfirm"
      @confirm="confirmBooking"
    />
  </div>
</template>
