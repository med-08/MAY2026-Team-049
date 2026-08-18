<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import StatusBadge from '../../components/student/StatusBadge.vue'
import { studentApi } from '../../services/studentApi'

const WEEKDAY_LABELS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

const MONTH_LABELS = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December'
]

const today = new Date()

const YEAR_OPTIONS = Array.from(
  { length: 11 },
  (_, index) => today.getFullYear() - 5 + index
)

const viewYear = ref(today.getFullYear())
const viewMonth = ref(today.getMonth() + 1)

const loading = ref(true)
const error = ref('')
const daysMap = ref({})

function isoOf(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')

  return `${y}-${m}-${day}`
}

const todayIso = isoOf(today)

const monthLabel = computed(() => {
  return `${MONTH_LABELS[viewMonth.value - 1]} ${viewYear.value}`
})

/*
|--------------------------------------------------------------------------
| Calendar
|--------------------------------------------------------------------------
*/

const weeks = computed(() => {
  const firstOfMonth = new Date(
    viewYear.value,
    viewMonth.value - 1,
    1
  )

  const totalDaysInMonth = new Date(
    viewYear.value,
    viewMonth.value,
    0
  ).getDate()

  const leadingBlanks =
    (firstOfMonth.getDay() + 6) % 7

  const cells = []

  // Previous month
  for (let i = leadingBlanks; i > 0; i--) {
    cells.push(
      new Date(
        viewYear.value,
        viewMonth.value - 1,
        1 - i
      )
    )
  }

  // Current month
  for (let d = 1; d <= totalDaysInMonth; d++) {
    cells.push(
      new Date(
        viewYear.value,
        viewMonth.value - 1,
        d
      )
    )
  }

  // Next month
  while (cells.length % 7 !== 0) {
    const next = new Date(
      cells[cells.length - 1]
    )

    next.setDate(next.getDate() + 1)
    cells.push(next)
  }

  const result = []

  for (let i = 0; i < cells.length; i += 7) {
    result.push(
      cells.slice(i, i + 7).map((date) => ({
        date,
        iso: isoOf(date),

        inMonth:
          date.getMonth() === viewMonth.value - 1 &&
          date.getFullYear() === viewYear.value,

        isToday: isoOf(date) === todayIso,

        dayName: date.toLocaleDateString(undefined, {
          weekday: 'short'
        })
      }))
    )
  }

  return result
})

function sessionsFor(iso) {
  const list = daysMap.value?.[iso]

  return Array.isArray(list) ? list : []
}

function hasSessions(iso) {
  return sessionsFor(iso).length > 0
}

/*
|--------------------------------------------------------------------------
| API
|--------------------------------------------------------------------------
*/

async function loadTimetable() {
  loading.value = true
  error.value = ''

  try {
    const r = await studentApi.getTimetable(
      viewYear.value,
      viewMonth.value
    )

    daysMap.value = r.data?.days || {}
  } catch (e) {
    console.error('Timetable loading error:', e)

    error.value =
      e.message || 'Failed to load timetable.'
  } finally {
    loading.value = false
  }
}

/*
|--------------------------------------------------------------------------
| Navigation
|--------------------------------------------------------------------------
*/

function goToPrevMonth() {
  if (viewMonth.value === 1) {
    viewMonth.value = 12
    viewYear.value -= 1
  } else {
    viewMonth.value -= 1
  }
}

function goToNextMonth() {
  if (viewMonth.value === 12) {
    viewMonth.value = 1
    viewYear.value += 1
  } else {
    viewMonth.value += 1
  }
}

function goToToday() {
  viewYear.value = today.getFullYear()
  viewMonth.value = today.getMonth() + 1
}

watch(
  [viewYear, viewMonth],
  loadTimetable
)

onMounted(loadTimetable)
</script>

<template>
  <div>

    <!-- ========================================================= -->
    <!-- HEADER -->
    <!-- ========================================================= -->

    <PageHeader
      title="Timetable"
      subtitle="Your actual booked schedule, by date."
    />

    <!-- ========================================================= -->
    <!-- MONTH CONTROLS -->
    <!-- ========================================================= -->

    <div class="mb-6">

      <div
        class="
          relative
          overflow-hidden
          rounded-3xl
          border
          border-slate-200/80
          dark:border-slate-700/70
          bg-white
          dark:bg-slate-900
          shadow-sm
          p-4
          md:p-5
        "
      >

        <!-- Decorative background -->
        <div
          class="
            absolute
            -top-16
            -right-16
            w-40
            h-40
            rounded-full
            bg-brand-blue/10
            blur-2xl
            pointer-events-none
          "
        ></div>

        <div
          class="
            absolute
            -bottom-16
            left-1/3
            w-40
            h-40
            rounded-full
            bg-emerald-400/10
            blur-2xl
            pointer-events-none
          "
        ></div>

        <div
          class="
            relative
            flex
            flex-col
            xl:flex-row
            xl:items-center
            xl:justify-between
            gap-5
          "
        >

          <!-- MONTH NAVIGATION -->

          <div class="flex items-center gap-3">

            <!-- Previous -->
            <button
              type="button"
              @click="goToPrevMonth"
              class="
                group
                w-11
                h-11
                shrink-0
                flex
                items-center
                justify-center
                rounded-2xl
                border
                border-slate-200
                dark:border-slate-700
                bg-slate-50
                dark:bg-slate-800
                text-slate-600
                dark:text-slate-300
                hover:bg-brand-blue
                hover:text-white
                hover:border-brand-blue
                hover:shadow-lg
                hover:shadow-brand-blue/20
                transition-all
                duration-200
              "
              aria-label="Previous month"
            >
              <svg
                width="19"
                height="19"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="group-hover:-translate-x-0.5 transition-transform"
              >
                <path d="M15 18l-6-6 6-6" />
              </svg>
            </button>

            <!-- Month -->
            <div
              class="
                min-w-[210px]
                sm:min-w-[250px]
                text-center
                rounded-2xl
                px-5
                py-3
                bg-gradient-to-r
                from-brand-blue/10
                via-indigo-500/5
                to-emerald-400/10
                border
                border-brand-blue/10
              "
            >

              <div
                class="
                  flex
                  items-center
                  justify-center
                  gap-2
                  mb-1
                  text-[10px]
                  uppercase
                  tracking-[0.2em]
                  font-bold
                  text-brand-blue
                "
              >
                <svg
                  width="13"
                  height="13"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <rect
                    x="3"
                    y="4"
                    width="18"
                    height="18"
                    rx="3"
                  />
                  <line x1="16" y1="2" x2="16" y2="6" />
                  <line x1="8" y1="2" x2="8" y2="6" />
                  <line x1="3" y1="10" x2="21" y2="10" />
                </svg>

                Timetable
              </div>

              <h2
                class="
                  font-display
                  font-extrabold
                  text-xl
                  sm:text-2xl
                  text-slate-800
                  dark:text-white
                  tracking-tight
                "
              >
                {{ monthLabel }}
              </h2>

            </div>

            <!-- Next -->
            <button
              type="button"
              @click="goToNextMonth"
              class="
                group
                w-11
                h-11
                shrink-0
                flex
                items-center
                justify-center
                rounded-2xl
                border
                border-slate-200
                dark:border-slate-700
                bg-slate-50
                dark:bg-slate-800
                text-slate-600
                dark:text-slate-300
                hover:bg-brand-blue
                hover:text-white
                hover:border-brand-blue
                hover:shadow-lg
                hover:shadow-brand-blue/20
                transition-all
                duration-200
              "
              aria-label="Next month"
            >
              <svg
                width="19"
                height="19"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                stroke-linejoin="round"
                class="group-hover:translate-x-0.5 transition-transform"
              >
                <path d="M9 18l6-6-6-6" />
              </svg>
            </button>

          </div>

          <!-- SELECTORS -->

          <div
            class="
              flex
              items-center
              justify-center
              xl:justify-end
              gap-2
              flex-wrap
            "
          >

            <!-- Month -->
            <div class="relative">

              <label
                class="sr-only"
                for="timetable-month"
              >
                Month
              </label>

              <svg
                class="
                  absolute
                  left-3
                  top-1/2
                  -translate-y-1/2
                  pointer-events-none
                  text-brand-blue
                  z-10
                "
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <rect
                  x="3"
                  y="4"
                  width="18"
                  height="18"
                  rx="3"
                />
                <line x1="16" y1="2" x2="16" y2="6" />
                <line x1="8" y1="2" x2="8" y2="6" />
                <line x1="3" y1="10" x2="21" y2="10" />
              </svg>

              <select
                id="timetable-month"
                v-model.number="viewMonth"
                class="
                  appearance-none
                  w-[145px]
                  rounded-2xl
                  border
                  border-slate-200
                  dark:border-slate-700
                  bg-slate-50
                  dark:bg-slate-800
                  pl-10
                  pr-9
                  py-3
                  text-sm
                  font-bold
                  text-slate-700
                  dark:text-slate-200
                  cursor-pointer
                  shadow-sm
                  hover:border-brand-blue/50
                  hover:bg-white
                  dark:hover:bg-slate-750
                  focus:outline-none
                  focus:ring-2
                  focus:ring-brand-blue/20
                  focus:border-brand-blue
                  transition-all
                "
              >
                <option
                  v-for="(label, index) in MONTH_LABELS"
                  :key="label"
                  :value="index + 1"
                >
                  {{ label }}
                </option>
              </select>

              <svg
                class="
                  absolute
                  right-3
                  top-1/2
                  -translate-y-1/2
                  pointer-events-none
                  text-slate-400
                "
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path d="M6 9l6 6 6-6" />
              </svg>

            </div>

            <!-- Year -->
            <div class="relative">

              <label
                class="sr-only"
                for="timetable-year"
              >
                Year
              </label>

              <svg
                class="
                  absolute
                  left-3
                  top-1/2
                  -translate-y-1/2
                  pointer-events-none
                  text-emerald-500
                  z-10
                "
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <rect
                  x="3"
                  y="4"
                  width="18"
                  height="18"
                  rx="3"
                />
                <line x1="16" y1="2" x2="16" y2="6" />
                <line x1="8" y1="2" x2="8" y2="6" />
                <line x1="3" y1="10" x2="21" y2="10" />
              </svg>

              <select
                id="timetable-year"
                v-model.number="viewYear"
                class="
                  appearance-none
                  w-[115px]
                  rounded-2xl
                  border
                  border-slate-200
                  dark:border-slate-700
                  bg-slate-50
                  dark:bg-slate-800
                  pl-10
                  pr-9
                  py-3
                  text-sm
                  font-bold
                  text-slate-700
                  dark:text-slate-200
                  cursor-pointer
                  shadow-sm
                  hover:border-emerald-400
                  hover:bg-white
                  focus:outline-none
                  focus:ring-2
                  focus:ring-emerald-400/20
                  focus:border-emerald-400
                  transition-all
                "
              >
                <option
                  v-for="year in YEAR_OPTIONS"
                  :key="year"
                  :value="year"
                >
                  {{ year }}
                </option>
              </select>

              <svg
                class="
                  absolute
                  right-3
                  top-1/2
                  -translate-y-1/2
                  pointer-events-none
                  text-slate-400
                "
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
              >
                <path d="M6 9l6 6 6-6" />
              </svg>

            </div>

            <!-- Today -->
            <button
              type="button"
              @click="goToToday"
              class="
                inline-flex
                items-center
                justify-center
                gap-2
                px-4
                py-3
                rounded-2xl
                bg-gradient-to-r
                from-brand-blue
                to-emerald-500
                text-white
                text-sm
                font-bold
                shadow-md
                shadow-brand-blue/20
                hover:shadow-lg
                hover:-translate-y-0.5
                active:translate-y-0
                transition-all
              "
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
              >
                <circle cx="12" cy="12" r="9" />
                <path d="M12 7v5l3 2" />
              </svg>

              Today
            </button>

          </div>

        </div>
      </div>
    </div>

    <!-- ========================================================= -->
    <!-- LOADING -->
    <!-- ========================================================= -->

    <div
      v-if="loading"
      class="
        rounded-3xl
        border
        border-slate-200
        dark:border-slate-700
        bg-white
        dark:bg-slate-900
        p-10
        text-center
        shadow-sm
      "
    >
      <div
        class="
          mx-auto
          w-10
          h-10
          rounded-full
          border-4
          border-slate-200
          border-t-brand-blue
          animate-spin
        "
      ></div>

      <p class="mt-4 text-sm font-medium text-slate-500">
        Loading your timetable...
      </p>
    </div>

    <!-- ERROR -->

    <div
      v-else-if="error"
      class="
        rounded-2xl
        border
        border-red-200
        dark:border-red-900/50
        bg-red-50
        dark:bg-red-950/20
        p-4
        text-danger
      "
    >
      {{ error }}
    </div>

    <!-- ========================================================= -->
    <!-- CALENDAR -->
    <!-- ========================================================= -->

    <template v-else>

      <!-- ======================================================= -->
      <!-- DESKTOP CALENDAR -->
      <!-- ======================================================= -->

      <div
        class="
          hidden
          sm:block
          rounded-3xl
          overflow-hidden
          border
          border-slate-200
          dark:border-slate-700
          bg-white
          dark:bg-slate-900
          shadow-lg
          shadow-slate-200/40
          dark:shadow-black/20
        "
      >

        <div class="overflow-x-auto">

          <div class="min-w-[900px]">

            <!-- WEEKDAY HEADER -->

            <div
              class="
                grid
                grid-cols-7
                bg-slate-50
                dark:bg-slate-800/80
                border-b
                border-slate-200
                dark:border-slate-700
              "
            >

              <div
                v-for="label in WEEKDAY_LABELS"
                :key="label"
                class="
                  relative
                  px-3
                  py-4
                  text-center
                  font-display
                  font-bold
                  text-xs
                  uppercase
                  tracking-wider
                  text-slate-500
                  dark:text-slate-400
                "
              >
                {{ label }}

                <!-- Header accent -->
                <div
                  class="
                    absolute
                    bottom-0
                    left-1/2
                    -translate-x-1/2
                    w-5
                    h-0.5
                    rounded-full
                    bg-brand-blue/40
                  "
                ></div>
              </div>

            </div>

            <!-- WEEKS -->

            <div
              v-for="(week, wIdx) in weeks"
              :key="wIdx"
              class="
                grid
                grid-cols-7
                border-b
                last:border-b-0
                border-slate-200
                dark:border-slate-700
              "
            >

              <!-- DAY -->

              <div
                v-for="cell in week"
                :key="cell.iso"
                class="
                  relative
                  min-h-[155px]
                  p-2
                  border-r
                  last:border-r-0
                  border-slate-200
                  dark:border-slate-700
                  transition-all
                  duration-200
                "
                :class="[
                  !cell.inMonth
                    ? 'bg-slate-50/60 dark:bg-white/[0.015]'
                    : 'bg-white dark:bg-slate-900',

                  cell.isToday
                    ? 'bg-brand-blue/[0.035] dark:bg-brand-blue/[0.07]'
                    : '',

                  hasSessions(cell.iso)
                    ? 'hover:bg-slate-50 dark:hover:bg-slate-800/60'
                    : ''
                ]"
              >

                <!-- TODAY TOP ACCENT -->

                <div
                  v-if="cell.isToday"
                  class="
                    absolute
                    top-0
                    left-2
                    right-2
                    h-1
                    rounded-b-full
                    bg-gradient-to-r
                    from-brand-blue
                    to-emerald-400
                  "
                ></div>

                <!-- DATE HEADER -->

                <div
                  class="
                    flex
                    items-center
                    justify-between
                    mb-2
                  "
                >

                  <!-- Day name for mobile-like visual -->
                  <span
                    v-if="cell.inMonth"
                    class="
                      text-[9px]
                      uppercase
                      tracking-wider
                      font-semibold
                      text-slate-400
                    "
                  >
                    {{ cell.dayName }}
                  </span>

                  <span
                    v-else
                    class="text-[9px]"
                  ></span>

                  <!-- Date -->

                  <span
                    class="
                      relative
                      text-xs
                      font-bold
                      w-8
                      h-8
                      flex
                      items-center
                      justify-center
                      rounded-xl
                      transition-all
                    "
                    :class="
                      cell.isToday
                        ? `
                          bg-gradient-to-br
                          from-brand-blue
                          to-indigo-500
                          text-white
                          shadow-md
                          shadow-brand-blue/30
                        `
                        : cell.inMonth
                          ? `
                            text-slate-700
                            dark:text-slate-200
                            bg-slate-100
                            dark:bg-slate-800
                          `
                          : `
                            text-slate-300
                            dark:text-slate-600
                          `
                    "
                  >
                    {{ cell.date.getDate() }}
                  </span>

                </div>

                <!-- SESSIONS -->

                <div
                  v-if="cell.inMonth"
                  class="
                    space-y-1.5
                    max-h-[105px]
                    overflow-y-auto
                    pr-0.5
                  "
                >

                  <!-- Session Card -->

                  <div
                    v-for="(c, index) in sessionsFor(cell.iso).slice(0, 3)"
                    :key="
                      c.session_id ??
                      `${cell.iso}-${c.time}-${c.subject}`
                    "
                    class="
                      group
                      relative
                      overflow-hidden
                      rounded-xl
                      border
                      border-slate-100
                      dark:border-slate-700
                      bg-slate-50
                      dark:bg-slate-800/80
                      px-2.5
                      py-2
                      cursor-default
                      hover:-translate-y-0.5
                      hover:shadow-md
                      transition-all
                      duration-200
                    "
                    :title="
                      `${c.subject || 'Subject'} · ${c.time || ''} · ${c.tutor || 'Tutor'}`
                    "
                  >

                    <!-- Colored side -->
                    <div
                      class="
                        absolute
                        left-0
                        top-0
                        bottom-0
                        w-1
                        bg-gradient-to-b
                        from-brand-blue
                        to-indigo-400
                      "
                    ></div>

                    <div class="pl-1">

                      <p
                        class="
                          font-bold
                          text-[11px]
                          text-slate-700
                          dark:text-slate-200
                          truncate
                        "
                      >
                        {{ c.subject || 'Subject' }}
                      </p>

                      <div
                        class="
                          flex
                          items-center
                          gap-1
                          mt-1
                          text-[10px]
                          text-slate-500
                          dark:text-slate-400
                        "
                      >

                        <svg
                          width="11"
                          height="11"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="currentColor"
                          stroke-width="2"
                        >
                          <circle cx="12" cy="12" r="9" />
                          <path d="M12 7v5l3 2" />
                        </svg>

                        <span class="truncate">
                          {{ c.time || '--' }}
                        </span>

                      </div>

                      <div
                        v-if="c.tutor"
                        class="
                          text-[9px]
                          text-slate-400
                          truncate
                          mt-0.5
                        "
                      >
                        {{ c.tutor }}
                      </div>

                    </div>

                  </div>

                  <!-- More -->

                  <div
                    v-if="sessionsFor(cell.iso).length > 3"
                    class="
                      flex
                      items-center
                      justify-center
                      rounded-lg
                      bg-brand-blue/5
                      dark:bg-brand-blue/10
                      text-[10px]
                      font-bold
                      text-brand-blue
                      py-1.5
                    "
                  >
                    +{{ sessionsFor(cell.iso).length - 3 }} more
                  </div>

                </div>

                <!-- EMPTY DAY -->

                <div
                  v-else-if="cell.inMonth"
                  class="
                    flex
                    items-center
                    justify-center
                    h-[65px]
                    opacity-0
                    hover:opacity-100
                    transition-opacity
                  "
                >
                  <span
                    class="
                      text-[10px]
                      text-slate-300
                      dark:text-slate-600
                    "
                  >
                    No sessions
                  </span>
                </div>

              </div>

            </div>

          </div>
        </div>
      </div>

      <!-- ======================================================= -->
      <!-- MOBILE AGENDA -->
      <!-- ======================================================= -->

      <div
        class="
          sm:hidden
          space-y-3
        "
      >

        <template
          v-for="week in weeks"
          :key="`m-${week[0].iso}`"
        >

          <div
            v-for="cell in week.filter(c => c.inMonth)"
            :key="`m-${cell.iso}`"
            class="
              relative
              overflow-hidden
              rounded-2xl
              border
              border-slate-200
              dark:border-slate-700
              bg-white
              dark:bg-slate-900
              shadow-sm
              p-4
            "
            :class="
              cell.isToday
                ? 'ring-2 ring-brand-blue/20'
                : ''
            "
          >

            <!-- Today accent -->

            <div
              v-if="cell.isToday"
              class="
                absolute
                left-0
                top-0
                bottom-0
                w-1
                bg-gradient-to-b
                from-brand-blue
                to-emerald-400
              "
            ></div>

            <!-- DATE -->

            <div
              class="
                flex
                items-center
                justify-between
                mb-3
              "
            >

              <div class="flex items-center gap-3">

                <div
                  class="
                    w-11
                    h-11
                    rounded-xl
                    flex
                    flex-col
                    items-center
                    justify-center
                  "
                  :class="
                    cell.isToday
                      ? 'bg-brand-blue text-white'
                      : 'bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-200'
                  "
                >
                  <span class="text-[9px] uppercase font-bold">
                    {{ cell.dayName }}
                  </span>

                  <span class="text-lg font-extrabold leading-none">
                    {{ cell.date.getDate() }}
                  </span>
                </div>

                <div>
                  <h3
                    class="
                      font-display
                      font-bold
                      text-sm
                      text-slate-800
                      dark:text-white
                    "
                  >
                    {{
                      cell.date.toLocaleDateString(
                        undefined,
                        {
                          weekday: 'long',
                          month: 'short'
                        }
                      )
                    }}
                  </h3>

                  <p
                    class="
                      text-xs
                      text-slate-400
                      mt-0.5
                    "
                  >
                    {{ monthLabel }}
                  </p>
                </div>

              </div>

              <span
                v-if="cell.isToday"
                class="
                  text-[10px]
                  font-bold
                  px-2.5
                  py-1
                  rounded-full
                  bg-brand-blue/10
                  text-brand-blue
                "
              >
                Today
              </span>

            </div>

            <!-- NO SESSION -->

            <div
              v-if="!sessionsFor(cell.iso).length"
              class="
                rounded-xl
                bg-slate-50
                dark:bg-slate-800/60
                p-4
                text-center
              "
            >
              <svg
                class="
                  mx-auto
                  mb-2
                  text-slate-300
                  dark:text-slate-600
                "
                width="22"
                height="22"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
              >
                <circle cx="12" cy="12" r="9" />
                <path d="M8 12h8" />
              </svg>

              <p
                class="
                  text-xs
                  font-medium
                  text-slate-400
                "
              >
                No sessions scheduled
              </p>
            </div>

            <!-- SESSIONS -->

            <div
              v-for="c in sessionsFor(cell.iso)"
              :key="
                c.session_id ??
                `${cell.iso}-m-${c.time}`
              "
              class="
                relative
                overflow-hidden
                rounded-xl
                border
                border-slate-100
                dark:border-slate-700
                bg-slate-50
                dark:bg-slate-800/70
                p-3
                mb-2
                last:mb-0
              "
            >

              <div
                class="
                  absolute
                  left-0
                  top-0
                  bottom-0
                  w-1
                  bg-gradient-to-b
                  from-brand-blue
                  to-indigo-400
                "
              ></div>

              <div class="pl-2">

                <div
                  class="
                    flex
                    items-center
                    justify-between
                    gap-2
                  "
                >

                  <p
                    class="
                      font-bold
                      text-sm
                      text-slate-800
                      dark:text-white
                    "
                  >
                    {{ c.subject || 'Subject' }}
                  </p>

                  <StatusBadge
                    v-if="c.status"
                    :status="c.status"
                  />

                </div>

                <div
                  class="
                    flex
                    items-center
                    gap-1.5
                    mt-2
                    text-xs
                    text-slate-500
                  "
                >

                  <svg
                    width="13"
                    height="13"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <circle cx="12" cy="12" r="9" />
                    <path d="M12 7v5l3 2" />
                  </svg>

                  {{ c.time || '--' }}

                </div>

                <p
                  v-if="c.tutor"
                  class="
                    text-[11px]
                    text-slate-400
                    mt-1
                  "
                >
                  Tutor: {{ c.tutor }}
                </p>

              </div>

            </div>

          </div>

        </template>

      </div>

    </template>

  </div>
</template>