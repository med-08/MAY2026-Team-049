<script setup>
import {
  CheckIcon,
  XMarkIcon,
  ClipboardDocumentCheckIcon,
  EnvelopeIcon,
  CalendarDaysIcon
} from '@heroicons/vue/24/outline'

import { adminApi } from '../../services/adminApi'
import { useServerTable } from '../../composables/useServerTable'
import { useToast } from '../../composables/useToast'

import Pagination from '../../components/ui/Pagination.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import LoadingRows from '../../components/ui/LoadingRows.vue'

const { showToast } = useToast()

async function fetchApprovals() {
  const res = await adminApi.listApprovals('Pending')

  return {
    meta: res.meta,
    data: res.data.map((item) => ({
      id: item.id,
      entityType: item.type.toLowerCase(),
      name: item.name,
      email: item.email,
      role: item.type,
      registrationDate: item.registration_date,
      status: item.status
    }))
  }
}

const {
  page,
  perPage,
  total,
  items: pageItems,
  loading,
  error,
  reload
} = useServerTable(fetchApprovals, {
  perPage: 8,
  supportsStatusFilter: false
})

async function approve(item) {
  try {
    await adminApi.approveEntity(
      item.entityType,
      item.id
    )

    showToast(
      `${item.name}'s registration was approved.`,
      'success'
    )

    await reload()
  } catch (e) {
    showToast(
      e.message || 'Failed to approve registration.',
      'error'
    )
  }
}

async function reject(item) {
  try {
    await adminApi.rejectEntity(
      item.entityType,
      item.id
    )

    showToast(
      `${item.name}'s registration was rejected.`,
      'error'
    )

    await reload()
  } catch (e) {
    showToast(
      e.message || 'Failed to reject registration.',
      'error'
    )
  }
}

function formatDate(d) {
  if (!d) return '—'

  return new Date(d).toLocaleDateString(
    'en-US',
    {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    }
  )
}
</script>

<template>
  <div class="space-y-6">

    <!-- Header -->
    <div
      class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between"
    >
      <div>
        <div class="flex items-center gap-3">

          <div
            class="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-100 text-amber-600 shadow-sm dark:bg-amber-500/10 dark:text-amber-400"
          >
            <ClipboardDocumentCheckIcon class="h-6 w-6" />
          </div>

          <div>
            <p
              class="text-[11px] font-bold uppercase tracking-[0.16em] text-amber-600 dark:text-amber-400"
            >
              Account Review
            </p>

            <h2
              class="text-2xl font-display font-bold tracking-tight text-slate-800 dark:text-slate-100 sm:text-3xl"
            >
              Pending Approvals
            </h2>
          </div>

        </div>

        <p
          class="mt-2 max-w-2xl text-sm leading-6 text-slate-500 dark:text-slate-400"
        >
          Review new registrations before they join
          the LearnAtHome platform.
        </p>
      </div>

      <!-- Pending Count -->
      <div
        v-if="!loading"
        class="flex items-center gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 dark:border-amber-500/20 dark:bg-amber-500/10"
      >
        <div
          class="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100 text-amber-600 dark:bg-amber-500/20 dark:text-amber-400"
        >
          <ClipboardDocumentCheckIcon class="h-4 w-4" />
        </div>

        <div>
          <p
            class="text-lg font-bold leading-none text-amber-700 dark:text-amber-300"
          >
            {{ total }}
          </p>

          <p
            class="mt-1 text-[11px] font-medium text-amber-600 dark:text-amber-400"
          >
            Awaiting review
          </p>
        </div>
      </div>
    </div>

    <!-- Error -->
    <EmptyState
      v-if="error"
      title="Couldn't load pending approvals"
      :message="error"
    />

    <!-- Main Card -->
    <div
      v-else
      class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800"
    >

      <!-- Card Header -->
      <div
        class="flex flex-col gap-3 border-b border-slate-100 px-5 py-4 dark:border-slate-700 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <div class="flex items-center gap-2">
            <h3
              class="font-display text-base font-semibold text-slate-800 dark:text-slate-100"
            >
              Registration Queue
            </h3>

            <span
              v-if="!loading"
              class="rounded-full bg-amber-50 px-2.5 py-0.5 text-[11px] font-bold text-amber-600 dark:bg-amber-500/10 dark:text-amber-400"
            >
              {{ total }} pending
            </span>
          </div>

          <p
            class="mt-0.5 text-xs text-slate-500 dark:text-slate-400"
          >
            Approve or reject newly submitted registrations.
          </p>
        </div>

        <div
          class="flex items-center gap-2 text-xs text-slate-400 dark:text-slate-500"
        >
          <span
            class="h-2 w-2 animate-pulse rounded-full bg-amber-500"
          />

          Requires your review
        </div>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="w-full min-w-[900px]">

          <!-- Table Header -->
          <thead
            class="bg-slate-50/80 dark:bg-slate-800/80"
          >
            <tr
              class="border-b border-slate-100 dark:border-slate-700"
            >
              <th
                class="px-5 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Applicant
              </th>

              <th
                class="px-5 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Email ID
              </th>

              <th
                class="px-5 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Role
              </th>

              <th
                class="px-5 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Registration Date
              </th>

              <th
                class="px-5 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Status
              </th>

              <th
                class="px-5 py-3.5 text-right text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Review
              </th>
            </tr>
          </thead>

          <!-- Table Body -->
          <tbody
            class="divide-y divide-slate-100 dark:divide-slate-700/70"
          >

            <!-- Loading -->
            <LoadingRows
              v-if="loading"
              :rows="6"
              :cols="6"
            />

            <!-- Approval Rows -->
            <template v-else>
              <tr
                v-for="item in pageItems"
                :key="`${item.entityType}-${item.id}`"
                class="group transition-colors duration-150 hover:bg-amber-50/30 dark:hover:bg-amber-500/[0.03]"
              >

                <!-- Applicant -->
                <td class="px-5 py-4">
                  <div class="flex items-center gap-3">

                    <div
                      class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-amber-400 to-orange-500 text-white shadow-sm"
                    >
                      <ClipboardDocumentCheckIcon
                        class="h-5 w-5"
                      />
                    </div>

                    <div class="min-w-0">
                      <p
                        class="truncate text-sm font-semibold text-slate-800 dark:text-slate-100"
                      >
                        {{ item.name }}
                      </p>

                      <p
                        class="mt-0.5 text-[11px] capitalize text-slate-400"
                      >
                        {{ item.entityType }} · ID {{ item.id }}
                      </p>
                    </div>

                  </div>
                </td>

                <!-- Email -->
                <td class="px-5 py-4">
                  <div class="flex items-center gap-2">
                    <EnvelopeIcon
                      class="h-4 w-4 shrink-0 text-slate-400"
                    />

                    <span
                      class="text-sm text-slate-600 dark:text-slate-300"
                    >
                      {{ item.email }}
                    </span>
                  </div>
                </td>

                <!-- Role -->
                <td class="px-5 py-4">
                  <span
                    class="inline-flex items-center rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-700 dark:border-slate-700 dark:bg-slate-700/50 dark:text-slate-300"
                  >
                    {{ item.role }}
                  </span>
                </td>

                <!-- Date -->
                <td class="px-5 py-4">
                  <div class="flex items-center gap-2">
                    <CalendarDaysIcon
                      class="h-4 w-4 shrink-0 text-slate-400"
                    />

                    <span
                      class="text-sm text-slate-600 dark:text-slate-300"
                    >
                      {{ formatDate(item.registrationDate) }}
                    </span>
                  </div>
                </td>

                <!-- Status -->
                <td class="px-5 py-4">
                  <span
                    class="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700 ring-1 ring-inset ring-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:ring-amber-500/20"
                  >
                    <span
                      class="h-1.5 w-1.5 rounded-full bg-amber-500"
                    />

                    {{ item.status }}
                  </span>
                </td>

                <!-- Actions -->
                <td class="px-5 py-4">
                  <div
                    class="flex items-center justify-end gap-2"
                  >

                    <!-- Approve -->
                    <button
                      class="group/approve flex h-9 items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 text-xs font-semibold text-emerald-700 transition-all hover:border-emerald-300 hover:bg-emerald-100 hover:shadow-sm disabled:cursor-not-allowed disabled:opacity-30 dark:border-emerald-500/20 dark:bg-emerald-500/10 dark:text-emerald-300 dark:hover:bg-emerald-500/20"
                      title="Approve registration"
                      :disabled="item.status !== 'Pending'"
                      @click="approve(item)"
                    >
                      <CheckIcon
                        class="h-4 w-4 transition-transform group-hover/approve:scale-110"
                      />

                      <span>Approve</span>
                    </button>

                    <!-- Reject -->
                    <button
                      class="group/reject flex h-9 items-center gap-1.5 rounded-lg border border-rose-200 bg-rose-50 px-3 text-xs font-semibold text-rose-600 transition-all hover:border-rose-300 hover:bg-rose-100 hover:shadow-sm disabled:cursor-not-allowed disabled:opacity-30 dark:border-rose-500/20 dark:bg-rose-500/10 dark:text-rose-300 dark:hover:bg-rose-500/20"
                      title="Reject registration"
                      :disabled="item.status !== 'Pending'"
                      @click="reject(item)"
                    >
                      <XMarkIcon
                        class="h-4 w-4 transition-transform group-hover/reject:scale-110"
                      />

                      <span>Reject</span>
                    </button>

                  </div>
                </td>

              </tr>
            </template>

          </tbody>
        </table>

        <!-- Empty -->
        <div
          v-if="!loading && pageItems.length === 0"
          class="px-6 py-10"
        >
          <EmptyState
            title="No pending approvals"
            message="There are currently no registrations waiting for review."
          />
        </div>
      </div>

      <!-- Pagination -->
      <div
        v-if="!loading && total > 0"
        class="border-t border-slate-100 bg-slate-50/50 px-3 dark:border-slate-700 dark:bg-slate-800/50"
      >
        <Pagination
          :page="page"
          :per-page="perPage"
          :total="total"
          @update:page="page = $event"
        />
      </div>
    </div>

  </div>
</template>