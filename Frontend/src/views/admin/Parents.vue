<script setup>
import { ref } from 'vue'
import {
  LockClosedIcon,
  LockOpenIcon,
  TrashIcon,
  UserGroupIcon,
  PhoneIcon,
  EnvelopeIcon
} from '@heroicons/vue/24/outline'

import { adminApi } from '../../services/adminApi'
import { useServerTable } from '../../composables/useServerTable'
import { useToast } from '../../composables/useToast'

import Pagination from '../../components/ui/Pagination.vue'
import ConfirmModal from '../../components/ui/ConfirmModal.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import LoadingRows from '../../components/ui/LoadingRows.vue'

const { showToast } = useToast()

async function fetchParents(params) {
  const res = await adminApi.listParents(params)

  return {
    meta: res.meta,
    data: res.data.map((p) => ({
      id: p.parent_id,
      name: p.parent_name,
      email: p.email,
      phone: p.phone_no || '—',
      studentName:
        p.children && p.children.length
          ? p.children.map((c) => c.student_name).join(', ')
          : '—',
      status: p.status
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
  statusFilter,
  reload
} = useServerTable(fetchParents, {
  perPage: 8,
  sortFieldMap: {
    name: 'parent_name',
    email: 'email',
    status: 'status'
  }
})

const filters = ['All', 'Active', 'Blocked', 'Pending']

const confirmOpen = ref(false)
const target = ref(null)

async function toggleBlock(p) {
  if (p.status === 'Pending') return

  const newStatus =
    p.status === 'Active'
      ? 'Blocked'
      : 'Active'

  try {
    await adminApi.updateParentStatus(
      p.id,
      newStatus
    )

    showToast(
      `${p.name} has been ${
        newStatus === 'Blocked'
          ? 'blocked'
          : 'unblocked'
      }.`,
      'success'
    )

    await reload()
  } catch (e) {
    showToast(
      e.message || 'Failed to update parent status.',
      'error'
    )
  }
}

function askDelete(p) {
  if (p.status === 'Pending') return
  target.value = p
  confirmOpen.value = true
}

async function confirmDelete() {
  const parent = target.value

  confirmOpen.value = false

  if (!parent) return

  try {
    await adminApi.deleteParent(parent.id)

    showToast(
      `${parent.name} was deleted.`,
      'success'
    )

    await reload()
  } catch (e) {
    showToast(
      e.message || 'Failed to delete parent.',
      'error'
    )
  } finally {
    target.value = null
  }
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
            class="flex h-11 w-11 items-center justify-center rounded-xl bg-purple-100 text-purple-600 shadow-sm dark:bg-purple-500/10 dark:text-purple-400"
          >
            <UserGroupIcon class="h-6 w-6" />
          </div>

          <div>
            <p
              class="text-[11px] font-bold uppercase tracking-[0.16em] text-purple-600 dark:text-purple-400"
            >
              User Management
            </p>

            <h2
              class="text-2xl font-display font-bold tracking-tight text-slate-800 dark:text-slate-100 sm:text-3xl"
            >
              Parents
            </h2>
          </div>

        </div>

        <p
          class="mt-2 max-w-2xl text-sm leading-6 text-slate-500 dark:text-slate-400"
        >
          Manage parents and keep track of the students
          connected to their accounts.
        </p>
      </div>

      <!-- Filters -->
      <div
        class="flex w-full items-center rounded-xl border border-slate-200 bg-white p-1 shadow-sm dark:border-slate-700 dark:bg-slate-800 sm:w-auto"
      >
        <button
          v-for="f in filters"
          :key="f"
          class="rounded-lg px-4 py-2 text-sm font-semibold transition-all duration-200"
          :class="
            statusFilter === f
              ? {
                  'bg-sky-500 text-white shadow-sm':
                    f === 'All',

                  'bg-emerald-500 text-white shadow-sm':
                    f === 'Active',

                  'bg-red-500 text-white shadow-sm':
                    f === 'Blocked',

                  'bg-amber-500 text-white shadow-sm':
                    f === 'Pending'
                }
              : 'text-slate-500 hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-200'
          "
          @click="statusFilter = f"
        >
          {{ f }}
        </button>
      </div>
    </div>

    <!-- Error -->
    <EmptyState
      v-if="error"
      title="Couldn't load parents"
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
              Parent Directory
            </h3>

            <span
              v-if="!loading"
              class="rounded-full bg-purple-50 px-2.5 py-0.5 text-[11px] font-bold text-purple-600 dark:bg-purple-500/10 dark:text-purple-400"
            >
              {{ total }}
            </span>
          </div>

          <p
            class="mt-0.5 text-xs text-slate-500 dark:text-slate-400"
          >
            View parent contact details, linked students,
            and account status.
          </p>
        </div>

        <div
          class="flex items-center gap-2 text-xs text-slate-400 dark:text-slate-500"
        >
          <span
            class="h-2 w-2 rounded-full bg-emerald-500"
          />

          Active parent accounts
        </div>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="w-full min-w-[1000px]">

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
                Parent
              </th>

              <th
                class="px-5 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Student Name
              </th>

              <th
                class="px-5 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Email ID
              </th>

              <th
                class="px-5 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Phone Number
              </th>

              <th
                class="px-5 py-3.5 text-left text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Status
              </th>

              <th
                class="px-5 py-3.5 text-right text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400"
              >
                Actions
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

            <!-- Parent Rows -->
            <template v-else>
              <tr
                v-for="p in pageItems"
                :key="p.id"
                class="group transition-colors duration-150 hover:bg-purple-50/30 dark:hover:bg-purple-500/[0.03]"
              >

                <!-- Parent -->
                <td class="px-5 py-4">
                  <div class="flex items-center gap-3">

                    <div
                      class="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-purple-500 to-fuchsia-600 text-white shadow-sm"
                    >
                      <UserGroupIcon class="h-5 w-5" />

                      <span
                        v-if="p.status === 'Active'"
                        class="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-white bg-emerald-500 dark:border-slate-800"
                      />
                    </div>

                    <div class="min-w-0">
                      <p
                        class="truncate text-sm font-semibold text-slate-800 dark:text-slate-100"
                      >
                        {{ p.name }}
                      </p>

                      <p
                        class="mt-0.5 text-[11px] text-slate-400"
                      >
                        Parent ID · {{ p.id }}
                      </p>
                    </div>

                  </div>
                </td>

                <!-- Student -->
                <td class="max-w-[240px] px-5 py-4">
                  <div
                    v-if="p.studentName !== '—'"
                    class="flex max-w-[240px] flex-wrap gap-1.5"
                  >
                    <span
                      v-for="student in p.studentName.split(', ')"
                      :key="student"
                      class="rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700 dark:border-slate-700 dark:bg-slate-700/50 dark:text-slate-300"
                    >
                      {{ student }}
                    </span>
                  </div>

                  <span
                    v-else
                    class="text-sm text-slate-400"
                  >
                    —
                  </span>
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
                      {{ p.email }}
                    </span>
                  </div>
                </td>

                <!-- Phone -->
                <td class="px-5 py-4">
                  <div class="flex items-center gap-2">
                    <PhoneIcon
                      class="h-4 w-4 shrink-0 text-slate-400"
                    />

                    <span
                      class="text-sm text-slate-600 dark:text-slate-300"
                    >
                      {{ p.phone }}
                    </span>
                  </div>
                </td>

                <!-- Status -->
                <td class="px-5 py-4">
                  <span
                    class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset"
                    :class="
                      p.status === 'Active'
                        ? 'bg-emerald-50 text-emerald-700 ring-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-300 dark:ring-emerald-500/20'
                        : p.status === 'Pending'
                        ? 'bg-amber-50 text-amber-700 ring-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:ring-amber-500/20'
                        : 'bg-red-50 text-red-700 ring-red-200 dark:bg-red-500/10 dark:text-red-300 dark:ring-red-500/20'
                    "
                  >
                    <span
                      class="h-1.5 w-1.5 rounded-full"
                      :class="
                        p.status === 'Active'
                          ? 'bg-emerald-500'
                          : p.status === 'Pending'
                          ? 'bg-amber-500'
                          : 'bg-red-500'
                      "
                    />

                    {{ p.status }}
                  </span>
                </td>

                <!-- Actions -->
                <td class="px-5 py-4">
                  <div
                    class="flex items-center justify-end gap-1.5"
                  >
                    <button
                      class="flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 transition-all hover:bg-slate-100 hover:text-slate-700 disabled:pointer-events-none disabled:opacity-40 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-200"
                      :title="
                        p.status === 'Pending'
                          ? 'Awaiting approval — review in Pending Approvals'
                          : p.status === 'Active'
                          ? 'Block parent'
                          : 'Unblock parent'
                      "
                      :disabled="p.status === 'Pending'"
                      @click="toggleBlock(p)"
                    >
                      <LockClosedIcon
                        v-if="p.status === 'Active'"
                        class="h-4 w-4"
                      />

                      <LockOpenIcon
                        v-else
                        class="h-4 w-4"
                      />
                    </button>

                    <button
                      class="flex h-8 w-8 items-center justify-center rounded-lg text-rose-500 transition-all hover:bg-rose-50 hover:text-rose-600 disabled:pointer-events-none disabled:opacity-40 dark:text-rose-400 dark:hover:bg-rose-500/10 dark:hover:text-rose-300"
                      :title="
                        p.status === 'Pending'
                          ? 'Awaiting approval — review in Pending Approvals'
                          : 'Delete parent'
                      "
                      :disabled="p.status === 'Pending'"
                      @click="askDelete(p)"
                    >
                      <TrashIcon class="h-4 w-4" />
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
            title="No parents found"
            message="Try a different name, email, or filter."
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

    <!-- Delete Confirmation -->
    <ConfirmModal
      :open="confirmOpen"
      title="Delete this parent?"
      :message="`This will permanently remove ${target?.name} from the platform.`"
      confirm-label="Delete"
      @confirm="confirmDelete"
      @cancel="confirmOpen = false"
    />

  </div>
</template>