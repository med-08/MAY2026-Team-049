<script setup>
import { ref } from 'vue'
import {
  LockClosedIcon,
  LockOpenIcon,
  TrashIcon,
  ChevronUpDownIcon,
  ArrowUpIcon,
  ArrowDownIcon
} from '@heroicons/vue/24/outline'

import { students } from '../../data/mockData'
import { useTableControls } from '../../composables/useTableControls'
import { useToast } from '../../composables/useToast'

import Pagination from '../../components/ui/Pagination.vue'
import ConfirmModal from '../../components/ui/ConfirmModal.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import LoadingRows from '../../components/ui/LoadingRows.vue'

const { showToast } = useToast()

const {
  page,
  perPage,
  total,
  pageItems,
  sortKey,
  sortAsc,
  toggleSort,
  statusFilter
} = useTableControls(students, {
  searchFields: ['name', 'email'],
  perPage: 8,
  statusField: 'status'
})

const filters = ['All', 'Active', 'Blocked']

const loading = ref(true)
setTimeout(() => (loading.value = false), 400)

const confirmOpen = ref(false)
const targetStudent = ref(null)

function toggleBlock(student) {
  student.status = student.status === 'Active' ? 'Blocked' : 'Active'
  showToast(
    `${student.name} has been ${
      student.status === 'Blocked' ? 'blocked' : 'unblocked'
    }.`,
    'success'
  )
}

function askDelete(student) {
  targetStudent.value = student
  confirmOpen.value = true
}

function confirmDelete() {
  const idx = students.findIndex((s) => s.id === targetStudent.value.id)
  if (idx !== -1) students.splice(idx, 1)

  showToast(`${targetStudent.value.name} was deleted.`, 'success')

  confirmOpen.value = false
  targetStudent.value = null
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
  <div>
    <div
      class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5"
    >
      <div>
        <h2
          class="text-xl font-display font-bold text-slate-800 dark:text-slate-100"
        >
          Students
        </h2>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
          Manage every student enrolled on the platform.
        </p>
      </div>

      <div class="flex items-center gap-2">
        <button
          v-for="f in filters"
          :key="f"
          class="pill-filter"
          :class="[
            statusFilter === f
              ? {
                  'bg-sky-500 text-white border-transparent shadow-soft':
                    f === 'All',
                  'bg-emerald-500 text-white border-transparent shadow-soft':
                    f === 'Active',
                  'bg-red-500 text-white border-transparent shadow-soft':
                    f === 'Blocked'
                }
              : {
                  'bg-sky-100 text-sky-700 border-sky-200 hover:bg-sky-200':
                    f === 'All',
                  'bg-emerald-100 text-emerald-700 border-emerald-200 hover:bg-emerald-200':
                    f === 'Active',
                  'bg-red-100 text-red-700 border-red-200 hover:bg-red-200':
                    f === 'Blocked'
                }
          ]"
          @click="statusFilter = f"
        >
          {{ f }}
        </button>
      </div>
    </div>

    <div class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="border-b border-slate-100 dark:border-slate-800">
            <tr>
              <th
                v-for="c in columns"
                :key="c.key"
                class="table-th cursor-pointer select-none"
                @click="toggleSort(c.key)"
              >
                <span class="inline-flex items-center gap-1">
                  {{ c.label }}

                  <ArrowUpIcon
                    v-if="sortKey === c.key && sortAsc"
                    class="w-3 h-3"
                  />

                  <ArrowDownIcon
                    v-else-if="sortKey === c.key && !sortAsc"
                    class="w-3 h-3"
                  />

                  <ChevronUpDownIcon
                    v-else
                    class="w-3 h-3 opacity-40"
                  />
                </span>
              </th>

              <th class="table-th text-right">
                Actions
              </th>
            </tr>
          </thead>

          <tbody class="divide-y divide-slate-50 dark:divide-slate-800/60">
            <LoadingRows
              v-if="loading"
              :rows="6"
              :cols="8"
            />

            <tr
              v-else
              v-for="s in pageItems"
              :key="s.id"
              class="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors"
            >
              <td class="table-td font-mono text-xs">
                {{ s.id }}
              </td>

              <td class="table-td font-medium text-slate-800 dark:text-slate-100">
                {{ s.name }}
              </td>

              <td class="table-td">
                {{ s.email }}
              </td>

              <td class="table-td">
                {{ s.school }}
              </td>

              <td class="table-td">
                {{ s.subject }}
              </td>

              <td class="table-td">
                {{ s.parentName }}
              </td>

              <td class="table-td">
                <span
                  class="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold"
                  :class="
                    s.status === 'Active'
                      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300'
                      : 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300'
                  "
                >
                  {{ s.status }}
                </span>
              </td>

              <td class="table-td">
                <div class="flex items-center justify-end gap-1.5">
                  <button
                    class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 transition-colors"
                    :title="s.status === 'Active'
                      ? 'Block student'
                      : 'Unblock student'"
                    @click="toggleBlock(s)"
                  >
                    <LockClosedIcon
                      v-if="s.status === 'Active'"
                      class="w-4 h-4"
                    />

                    <LockOpenIcon
                      v-else
                      class="w-4 h-4"
                    />
                  </button>
                                    <button
                    class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-rose-50 dark:hover:bg-rose-500/10 text-rose-500 transition-colors"
                    title="Delete student"
                    @click="askDelete(s)"
                  >
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <EmptyState
          v-if="!loading && pageItems.length === 0"
          title="No students found"
          message="Try a different name, email, or filter."
        />
      </div>

      <div class="border-t border-slate-100 dark:border-slate-800 px-2">
        <Pagination
          v-if="!loading && total > 0"
          :page="page"
          :per-page="perPage"
          :total="total"
          @update:page="page = $event"
        />
      </div>
    </div>

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