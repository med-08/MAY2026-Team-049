<script setup>
import { ref, reactive, computed } from "vue"
import PageHeader from "../../components/student/PageHeader.vue"
import { CalendarIcon, ClockIcon, UserIcon, UsersIcon, BookOpenIcon } from "@heroicons/vue/24/outline"
import { bookingSlots as initialSlots } from "../../data/studentMockData"

const tab = ref("regular")
const slots = reactive({
  regular: initialSlots.regular.map((s) => ({ ...s })),
  oneToOne: initialSlots.oneToOne.map((s) => ({ ...s })),
})

const activeSlots = computed(() => slots[tab.value])
const hasOtherAvailable = (list, currentId) => list.some((s) => s.id !== currentId && !s.booked && s.seats > 0)

function bookSlot(slot) {
  if (slot.booked || slot.seats <= 0) return
  slot.booked = true
  slot.seats -= 1
}

function reschedule(list, slot) {
  const target = list.find((s) => s.id !== slot.id && !s.booked && s.seats > 0)
  if (!target) return
  slot.booked = false
  slot.seats += 1
  target.booked = true
  target.seats -= 1
}
</script>

<template>
  <div>
    <PageHeader title="Session Booking" subtitle="Book your next offline tuition slot with a tutor." />

    <div class="inline-flex p-1 rounded-xl bg-slate-100 dark:bg-white/5 mb-6">
      <button
        class="px-5 py-2 rounded-lg text-sm font-semibold transition"
        :class="tab === 'regular' ? 'bg-teal-100 dark:bg-teal-500/15 shadow-sm text-teal-700 dark:text-teal-300' : 'text-ink-soft dark:text-slate-400'"
        @click="tab = 'regular'"
      >
        Regular Sessions
      </button>
      <button
        class="px-5 py-2 rounded-lg text-sm font-semibold transition"
        :class="tab === 'oneToOne' ? 'bg-teal-100 dark:bg-teal-500/15 shadow-sm text-teal-700 dark:text-teal-300' : 'text-ink-soft dark:text-slate-400'"
        @click="tab = 'oneToOne'"
      >
        One-to-One Sessions
      </button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
      <div v-for="slot in activeSlots" :key="slot.id" class="card card-hover p-5">
        <div class="flex items-start justify-between mb-3">
          <h4 class="font-display font-bold">{{ slot.subject }}</h4>
          <span
            class="text-xs font-semibold px-2.5 py-1 rounded-full"
            :class="slot.booked ? 'bg-brand-blue/10 text-brand-blue' : 'bg-brand-green/10 text-brand-green-dark dark:text-brand-green'"
          >
            {{ slot.booked ? "Booked" : "Available" }}
          </span>
        </div>

        <div class="space-y-2 text-sm mb-4">
          <p class="flex items-center gap-2 text-ink-soft dark:text-slate-300"><UserIcon class="w-4 h-4 shrink-0" /> {{ slot.tutor }}</p>
          <p class="flex items-center gap-2 text-ink-soft dark:text-slate-300"><CalendarIcon class="w-4 h-4 shrink-0" /> {{ slot.date }}</p>
          <p class="flex items-center gap-2 text-ink-soft dark:text-slate-300"><ClockIcon class="w-4 h-4 shrink-0" /> {{ slot.time }}</p>
          <p class="flex items-center gap-2 text-ink-soft dark:text-slate-300"><UsersIcon class="w-4 h-4 shrink-0" /> {{ slot.seats }} seat(s) available</p>
        </div>

        <button
          v-if="!slot.booked"
          class="w-full py-2.5 rounded-xl font-semibold text-sm bg-teal-100 text-teal-700 hover:bg-teal-200 dark:bg-teal-500/15 dark:text-teal-300 dark:hover:bg-teal-500/25 transition disabled:opacity-40"
          :disabled="slot.seats <= 0"
          @click="bookSlot(slot)"
        >
          {{ slot.seats <= 0 ? "Full" : "Book Slot" }}
        </button>
        <button
          v-else
          class="w-full py-2.5 rounded-xl font-semibold text-sm border border-slate-200 dark:border-border-dark hover:bg-slate-50 dark:hover:bg-white/5 transition disabled:opacity-40 disabled:cursor-not-allowed"
          :disabled="!hasOtherAvailable(activeSlots, slot.id)"
          @click="reschedule(activeSlots, slot)"
        >
          Reschedule
        </button>
      </div>
    </div>
  </div>
</template>
