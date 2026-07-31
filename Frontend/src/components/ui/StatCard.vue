<script setup>
const props = defineProps({
  title: { type: String, required: true },
  value: { type: [Number, String], required: true },
  subtitle: { type: String, default: "" },
  color: { type: String, default: "emerald" },
  icon: { type: [Object, Function], required: true }
})

const gradients = {
  emerald: "from-emerald-50 to-white dark:from-slate-900 dark:to-slate-900",
  blue: "from-blue-50 to-white dark:from-slate-900 dark:to-slate-900",
  purple: "from-violet-50 to-white dark:from-slate-900 dark:to-slate-900",
  red: "from-red-50 to-white dark:from-slate-900 dark:to-slate-900",
  amber: "from-amber-50 to-white dark:from-slate-900 dark:to-slate-900",
  teal: "from-teal-50 to-white dark:from-slate-900 dark:to-slate-900"
}

const iconBg = {
  emerald: "bg-emerald-500",
  blue: "bg-blue-500",
  purple: "bg-violet-500",
  red: "bg-red-500",
  amber: "bg-amber-500",
  teal: "bg-teal-500"
}

const textColor = {
  emerald: "text-emerald-700 dark:text-emerald-400",
  blue: "text-blue-700 dark:text-blue-400",
  purple: "text-violet-700 dark:text-violet-400",
  red: "text-red-700 dark:text-red-400",
  amber: "text-amber-700 dark:text-amber-400",
  teal: "text-teal-700 dark:text-teal-400"
}
</script>

<template>
  <div
    class="relative overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-800 bg-gradient-to-br p-7 min-h-[180px] shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
    :class="gradients[color]"
  >
    <div class="flex items-start justify-between">
      <div>
        <p
          class="text-xs font-semibold uppercase tracking-wider"
          :class="textColor[color]"
        >
          {{ title }}
        </p>

        <div class="mt-4 border-t border-slate-200 dark:border-slate-700"></div>

        <h2
          class="mt-5 text-5xl font-bold text-slate-800 dark:text-slate-100"
        >
          {{ value }}
        </h2>

        <p
          class="mt-3 text-sm text-slate-500 dark:text-slate-400"
        >
          {{ subtitle }}
        </p>
      </div>

      <div
        class="flex h-16 w-16 items-center justify-center rounded-full shadow-lg"
        :class="iconBg[color]"
      >
        <component
          :is="icon"
          class="h-8 w-8 text-white"
        />
      </div>
    </div>

    <div
      class="absolute -right-10 -bottom-10 h-32 w-32 rounded-full opacity-10"
      :class="iconBg[color]"
    ></div>
  </div>
</template>