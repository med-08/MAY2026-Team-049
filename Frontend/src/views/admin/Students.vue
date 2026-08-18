<script setup>
import { ref } from 'vue'
import {
  LockClosedIcon,
  LockOpenIcon,
  TrashIcon,
  ChevronUpDownIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  UserCircleIcon
} from '@heroicons/vue/24/outline'

import { adminApi } from '../../services/adminApi'
import { useServerTable } from '../../composables/useServerTable'
import { useToast } from '../../composables/useToast'

import Pagination from '../../components/ui/Pagination.vue'
import ConfirmModal from '../../components/ui/ConfirmModal.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import LoadingRows from '../../components/ui/LoadingRows.vue'

const { showToast } = useToast()

async function fetchStudents(params) {
  const res = await adminApi.listStudents(params)

  return {
    meta: res.meta,
    data: res.data.map((s) => ({
      id: s.student_id,
      name: s.student_name,
      email: s.email,
      school: s.school || '—',
      subject:
        s.subjects && s.subjects.length
          ? s.subjects.join(', ')
          : '—',
      parentName: s.parent_name || '—',
      status: s.status
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
  sortKey,
  sortAsc,
  toggleSort,
  statusFilter,
  reload
} = useServerTable(fetchStudents, {
  perPage: 8,
  sortFieldMap: {
    id: 'student_id',
    name: 'student_name',
    email: 'email',
    school: 'school',
    status: 'status',
    subject: null,
    parentName: null
  }
})

const filters = ['All', 'Active', 'Blocked']

const confirmOpen = ref(false)
const targetStudent = ref(null)
const actionInFlight = ref(false)

async function toggleBlock(student) {
  const newStatus =
    student.status === 'Active'
      ? 'Blocked'
      : 'Active'

  actionInFlight.value = true

  try {
    await adminApi.updateStudentStatus(
      student.id,
      newStatus
    )

    showToast(
      `${student.name} has been ${
        newStatus === 'Blocked'
          ? 'blocked'
          : 'unblocked'
      }.`,
      'success'
    )

    await reload()
  } catch (e) {
    showToast(
      e.message || 'Failed to update student status.',
      'error'
    )
  } finally {
    actionInFlight.value = false
  }
}

function askDelete(student) {
  targetStudent.value = student
  confirmOpen.value = true
}

async function confirmDelete() {
  const student = targetStudent.value

  confirmOpen.value = false

  if (!student) return

  try {
    await adminApi.deleteStudent(student.id)

    showToast(
      `${student.name} was deleted.`,
      'success'
    )

    await reload()
  } catch (e) {
    showToast(
      e.message || 'Failed to delete student.',
      'error'
    )
  } finally {
    targetStudent.value = null
  }
}

const columns = [
  { key: 'id', label: 'Student ID' },
  { key: 'name', label: 'Student Name' },
  { key: 'email', label: 'Email ID' },
  { key: 'school', label: 'School' },
  { key: 'subject', label: 'Subject' },
  { key: 'parentName', label: 'Parent Name' },
  { key: 'status', label: 'Status' }
]
</script>

<template>
  <div class="space-y-6">

    <!-- Header -->
    <div
      class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between"
    >
      <div>
        <div class="flex items-center gap-2">
          <div
            class="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-100 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400"
          >
            <UserCircleIcon class="h-5 w-5" />
          </div>

          <div>
            <p
              class="text-xs font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400"
            >
              User Management
            </p>

            <h2
              class="text-2xl font-display font-bold tracking-tight text-slate-800 dark:text-slate-100"
            >
              Students
            </h2>
          </div>
        </div>

        <p
          class="mt-2 max-w-2xl text-sm leading-6 text-slate-500 dark:text-slate-400"
        >
          Manage student accounts, enrollment information,
          status, and associated parent details.
        </p>
      </div>

      <!-- Filters -->
      <div
        class="flex w-full items-center rounded-xl border border-slate-200 bg-white p-1 shadow-sm dark:border-slate-700 dark:bg-slate-800 sm:w-auto"
      >
        <button
          v-for="f in filters"
          :key="f"
          class="rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200"
          :class="
            statusFilter === f
              ? {
                  'bg-sky-500 text-white shadow-sm':
                    f === 'All',

                  'bg-emerald-500 text-white shadow-sm':
                    f === 'Active',

                  'bg-red-500 text-white shadow-sm':
                    f === 'Blocked'
                }
              : {
                  'text-slate-500 hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-200':
                    true
                }
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
      title="Couldn't load students"
      :message="error"
    />

    <!-- Table -->
    <div
      v-else
      class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800"
    >

      <!-- Table Header -->
      <div
        class="flex flex-col gap-1 border-b border-slate-100 px-5 py-4 dark:border-slate-700 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h3
            class="font-display text-base font-semibold text-slate-800 dark:text-slate-100"
          >
            Student Directory
          </h3>

          <p
            class="mt-0.5 text-xs text-slate-500 dark:text-slate-400"
          >
            View and manage all registered students.
          </p>
        </div>

        <div
          v-if="!loading"
          class="text-xs font-medium text-slate-400 dark:text-slate-500"
        >
          {{ total }} {{ total === 1 ? 'student' : 'students' }}
        </div>
      </div>

      <!-- Responsive Table -->
      <div class="overflow-x-auto">
        <table class="w-full min-w-[1050px]">

          <!-- Table Head -->
          <thead
            class="bg-slate-50/80 dark:bg-slate-800/80"
          >
            <tr
              class="border-b border-slate-100 dark:border-slate-700"
            >
              <th
                v-for="c in columns"
                :key="c.key"
                class="px-5 py-3.5 text-left text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400"
                :class="{
                  'cursor-pointer select-none hover:text-slate-700 dark:hover:text-slate-200':
                    c.key
                }"
                @click="toggleSort(c.key)"
              >
                <span
                  class="inline-flex items-center gap-1.5"
                >
                  {{ c.label }}

                  <ArrowUpIcon
                    v-if="
                      sortKey === c.key &&
                      sortAsc
                    "
                    class="h-3.5 w-3.5"
                  />

                  <ArrowDownIcon
                    v-else-if="
                      sortKey === c.key &&
                      !sortAsc
                    "
                    class="h-3.5 w-3.5"
                  />

                  <ChevronUpDownIcon
                    v-else
                    class="h-3.5 w-3.5 opacity-30"
                  />
                </span>
              </th>

              <th
                class="px-5 py-3.5 text-right text-[11px] font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400"
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
              :cols="8"
            />

            <!-- Students -->
            <template v-else>
              <tr
                v-for="s in pageItems"
                :key="s.id"
                class="group transition-colors duration-150 hover:bg-slate-50/80 dark:hover:bg-slate-700/20"
              >

                <!-- ID -->
                <td class="px-5 py-4">
                  <span
                    class="rounded-md bg-slate-100 px-2 py-1 font-mono text-[11px] font-medium text-slate-600 dark:bg-slate-700 dark:text-slate-300"
                  >
                    {{ s.id }}
                  </span>
                </td>

                <!-- Name -->
                <td class="px-5 py-4">
                  <div class="flex items-center gap-3">
                    <div
                      class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400"
                    >
                      <UserCircleIcon
                        class="h-5 w-5"
                      />
                    </div>

                    <div class="min-w-0">
                      <p
                        class="truncate text-sm font-semibold text-slate-800 dark:text-slate-100"
                      >
                        {{ s.name }}
                      </p>

                      <p
                        class="text-[11px] text-slate-400"
                      >
                        Student
                      </p>
                    </div>
                  </div>
                </td>

                <!-- Email -->
                <td class="px-5 py-4">
                  <span
                    class="text-sm text-slate-600 dark:text-slate-300"
                  >
                    {{ s.email }}
                  </span>
                </td>

                <!-- School -->
                <td class="px-5 py-4">
                  <span
                    class="text-sm text-slate-600 dark:text-slate-300"
                  >
                    {{ s.school }}
                  </span>
                </td>

                <!-- Subject -->
                <td class="max-w-[220px] px-5 py-4">
                  <span
                    class="block truncate text-sm text-slate-600 dark:text-slate-300"
                    :title="s.subject"
                  >
                    {{ s.subject }}
                  </span>
                </td>

                <!-- Parent -->
                <td class="px-5 py-4">
                  <span
                    class="text-sm text-slate-600 dark:text-slate-300"
                  >
                    {{ s.parentName }}
                  </span>
                </td>

                <!-- Status -->
                <td class="px-5 py-4">
                  <span
                    class="inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold"
                    :class="
                      s.status === 'Active'
                        ? 'bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-300 dark:ring-emerald-500/20'
                        : 'bg-red-50 text-red-700 ring-1 ring-inset ring-red-200 dark:bg-red-500/10 dark:text-red-300 dark:ring-red-500/20'
                    "
                  >
                    <span
                      class="h-1.5 w-1.5 rounded-full"
                      :class="
                        s.status === 'Active'
                          ? 'bg-emerald-500'
                          : 'bg-red-500'
                      "
                    />

                    {{ s.status }}
                  </span>
                </td>

                <!-- Actions -->
                <td class="px-5 py-4">
                  <div
                    class="flex items-center justify-end gap-1.5"
                  >
                    <button
                      class="flex h-8 w-8 items-center justify-center rounded-lg text-slate-500 transition-all hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-200"
                      :class="{
                        'pointer-events-none opacity-50':
                          actionInFlight
                      }"
                      :title="
                        s.status === 'Active'
                          ? 'Block student'
                          : 'Unblock student'
                      "
                      @click="toggleBlock(s)"
                    >
                      <LockClosedIcon
                        v-if="s.status === 'Active'"
                        class="h-4 w-4"
                      />

                      <LockOpenIcon
                        v-else
                        class="h-4 w-4"
                      />
                    </button>

                    <button
                      class="flex h-8 w-8 items-center justify-center rounded-lg text-rose-500 transition-all hover:bg-rose-50 hover:text-rose-600 dark:text-rose-400 dark:hover:bg-rose-500/10 dark:hover:text-rose-300"
                      title="Delete student"
                      @click="askDelete(s)"
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
            title="No students found"
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
      title="Delete this student?"
      :message="`This will permanently remove ${targetStudent?.name} from the platform.`"
      confirm-label="Delete"
      @confirm="confirmDelete"
      @cancel="confirmOpen = false"
    />

  </div>
</template>