<script setup>
import { reactive } from "vue"
import PageHeader from "../../components/student/PageHeader.vue"
import StatusBadge from "../../components/student/StatusBadge.vue"
import { homeworkList as initialHomework } from "../../data/studentMockData"

const homeworkList = reactive(initialHomework.map((h) => ({ ...h })))

function markCompleted(item) {
  item.status = "Submitted"
  item.submissionDate = new Date().toLocaleDateString("en-GB")
}
</script>

<template>
  <div>
    <PageHeader
      title="Homework"
      subtitle="Track assignments, submission status and tutor feedback."
    />

    <div class="space-y-4">
      <div
        v-for="h in homeworkList"
        :key="h.assignmentId"
        class="card p-5"
        :class="h.status === 'Late' ? 'ring-1 ring-danger/40' : ''"
      >
        <div class="flex flex-col lg:flex-row lg:justify-between gap-6">

          <!-- Left -->
          <div class="flex-1">
            <p class="text-xs font-semibold text-brand-blue">
              {{ h.session }}
            </p>

            <h3 class="font-semibold text-lg mt-1">
              {{ h.title }}
            </h3>

            <p class="text-sm text-ink-soft dark:text-slate-400 mt-2">
              {{ h.description }}
            </p>

            <div
              class="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-y-2 text-sm"
            >
              <p>
                <span class="font-medium">Due Date:</span>
                {{ h.dueDate }}
              </p>

              <p>
                <span class="font-medium">Submission:</span>
                {{ h.submissionDate || "Not Submitted" }}
              </p>
            </div>

            <div
              v-if="h.feedback"
              class="mt-4 rounded-xl bg-slate-100 dark:bg-slate-800 p-3"
            >
              <p class="text-xs font-semibold text-brand-blue mb-1">
                Tutor Feedback
              </p>

              <p class="text-sm">
                {{ h.feedback }}
              </p>
            </div>
          </div>

          <!-- Right -->
          <div
            class="flex flex-col items-start lg:items-end gap-3 lg:w-48"
          >
            <StatusBadge :status="h.status" />

            <button
              v-if="h.status === 'Pending' || h.status === 'Late'"
              @click="markCompleted(h)"
              class="px-4 py-2 rounded-xl text-sm font-semibold bg-amber-100 text-amber-700 hover:bg-amber-200 dark:bg-amber-500/15 dark:text-amber-300 dark:hover:bg-amber-500/25 transition"
            >
              Mark as Completed
            </button>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>