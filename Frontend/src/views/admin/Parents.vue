<script setup>
import { ref } from 'vue'
import { LockClosedIcon, LockOpenIcon, TrashIcon } from '@heroicons/vue/24/outline'
import { adminApi } from '../../services/adminApi'
import { useServerTable } from '../../composables/useServerTable'
import { useToast } from '../../composables/useToast'
import Pagination from '../../components/ui/Pagination.vue'
import ConfirmModal from '../../components/ui/ConfirmModal.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import LoadingRows from '../../components/ui/LoadingRows.vue'

const { showToast } = useToast()

// Transform the backend's Parent shape (parent_name/phone_no/children[])
// into the field names this view's template already uses (name/phone/
// studentName), so the template itself needs no changes.
async function fetchParents(params) {
  const res = await adminApi.listParents(params)
  return {
    meta: res.meta,
    data: res.data.map((p) => ({
      id: p.parent_id,
      name: p.parent_name,
      email: p.email,
      phone: p.phone_no || '—',
      // NOTE (assumption): the schema allows a parent to have multiple
      // children (1:many), while this table has one "Student Name"
      // column. We join every linked child's name with a comma.
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

const filters = ['All', 'Active', 'Blocked']

const confirmOpen = ref(false)
const target = ref(null)

async function toggleBlock(p) {
  const newStatus = p.status === 'Active' ? 'Blocked' : 'Active'
  try {
    await adminApi.updateParentStatus(p.id, newStatus)
    showToast(`${p.name} has been ${newStatus === 'Blocked' ? 'blocked' : 'unblocked'}.`, 'success')
    await reload()
  } catch (e) {
    showToast(e.message || 'Failed to update parent status.', 'error')
  }
}

function askDelete(p) {
  target.value = p
  confirmOpen.value = true
}

async function confirmDelete() {
  const parent = target.value
  confirmOpen.value = false
  if (!parent) return

  try {
    await adminApi.deleteParent(parent.id)
    showToast(`${parent.name} was deleted.`, 'success')
    await reload()
  } catch (e) {
    showToast(e.message || 'Failed to delete parent.', 'error')
  } finally {
    target.value = null
  }
}
</script>

<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
      <div>
        <h2 class="text-xl font-display font-bold text-slate-800 dark:text-slate-100">
          Parents
        </h2>

        <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">
          Everyone keeping an eye on their student's progress.
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
                  'bg-sky-500 text-white border-transparent shadow-soft': f === 'All',
                  'bg-emerald-500 text-white border-transparent shadow-soft': f === 'Active',
                  'bg-red-500 text-white border-transparent shadow-soft': f === 'Blocked'
                }
              : {
                  'bg-sky-100 text-sky-700 border-sky-200 hover:bg-sky-200': f === 'All',
                  'bg-emerald-100 text-emerald-700 border-emerald-200 hover:bg-emerald-200': f === 'Active',
                  'bg-red-100 text-red-700 border-red-200 hover:bg-red-200': f === 'Blocked'
                }
          ]"
          @click="statusFilter = f"
        >
          {{ f }}
        </button>
      </div>
    </div>

    <EmptyState
      v-if="error"
      title="Couldn't load parents"
      :message="error"
    />

    <div
      v-else
      class="card overflow-hidden"
    >
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="border-b border-slate-100 dark:border-slate-800">
            <tr>
              <th class="table-th">Parent Name</th>
              <th class="table-th">Student Name</th>
              <th class="table-th">Email ID</th>
              <th class="table-th">Phone Number</th>
              <th class="table-th">Status</th>
              <th class="table-th text-right">Actions</th>
            </tr>
          </thead>

          <tbody class="divide-y divide-slate-50 dark:divide-slate-800/60">
            <LoadingRows
              v-if="loading"
              :rows="6"
              :cols="6"
            />

            <tr
              v-else
              v-for="p in pageItems"
              :key="p.id"
              class="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors"
            >
              <td class="table-td font-medium text-slate-800 dark:text-slate-100">
                {{ p.name }}
              </td>

              <td class="table-td">
                {{ p.studentName }}
              </td>

              <td class="table-td">
                {{ p.email }}
              </td>

              <td class="table-td">
                {{ p.phone }}
              </td>

              <td class="table-td">
                <span
                  class="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold"
                  :class="
                    p.status === 'Active'
                      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300'
                      : 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300'
                  "
                >
                  {{ p.status }}
                </span>
              </td>

              <td class="table-td">
                <div class="flex items-center justify-end gap-1.5">
                  <button
                    class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 transition-colors"
                    :title="p.status === 'Active' ? 'Block parent' : 'Unblock parent'"
                    @click="toggleBlock(p)"
                  >
                    <LockClosedIcon
                      v-if="p.status === 'Active'"
                      class="w-4 h-4"
                    />

                    <LockOpenIcon
                      v-else
                      class="w-4 h-4"
                    />
                  </button>
                                    <button
                    class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-rose-50 dark:hover:bg-rose-500/10 text-rose-500 transition-colors"
                    title="Delete parent"
                    @click="askDelete(p)"
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
          title="No parents found"
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
      title="Delete this parent?"
      :message="`This will permanently remove ${target?.name} from the platform.`"
      confirm-label="Delete"
      @confirm="confirmDelete"
      @cancel="confirmOpen = false"
    />
  </div>
</template>
