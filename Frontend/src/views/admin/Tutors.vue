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

// Transform the backend's Tutor shape (tutor_name/phone_no/experience_years)
// into the field names this view's template already uses.
async function fetchTutors(params) {
  const res = await adminApi.listTutors(params)
  return {
    meta: res.meta,
    data: res.data.map((t) => ({
      id: t.tutor_id,
      name: t.tutor_name,
      email: t.email,
      experience: t.experience_years != null ? `${t.experience_years} yrs` : '—',
      phone: t.phone_no || '—',
      subjects: t.subjects || [],
      status: t.status
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
} = useServerTable(fetchTutors, {
  perPage: 8,
  supportsStatusFilter: true,
  sortFieldMap: {
    name: 'tutor_name',
    email: 'email',
    status: 'status'
  }
})

const filters = ['All', 'Active', 'Blocked']

const confirmOpen = ref(false)
const target = ref(null)

async function toggleBlock(t) {
  const newStatus = t.status === 'Active' ? 'Blocked' : 'Active'
  try {
    await adminApi.updateTutorStatus(t.id, newStatus)
    showToast(`${t.name} has been ${newStatus === 'Blocked' ? 'blocked' : 'unblocked'}.`, 'success')
    await reload()
  } catch (e) {
    showToast(e.message || 'Failed to update tutor status.', 'error')
  }
}

function askDelete(t) {
  target.value = t
  confirmOpen.value = true
}

async function confirmDelete() {
  const tutor = target.value
  confirmOpen.value = false
  if (!tutor) return

  try {
    await adminApi.deleteTutor(tutor.id)
    showToast(`${tutor.name} was deleted.`, 'success')
    await reload()
  } catch (e) {
    showToast(e.message || 'Failed to delete tutor.', 'error')
  } finally {
    target.value = null
  }
}
</script>

<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5">
      <div>
        <h2 class="text-xl font-display font-bold text-slate-800 dark:text-slate-100">Tutors</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">The educators guiding students through every subject.</p>
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
      title="Couldn't load tutors"
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
              <th class="table-th">Tutor Name</th>
              <th class="table-th">Email ID</th>
              <th class="table-th">Experience</th>
              <th class="table-th">Phone Number</th>
              <th class="table-th">Subjects</th>
              <th class="table-th">Status</th>
              <th class="table-th text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-800/60">
            <LoadingRows v-if="loading" :rows="6" :cols="7" />
            <tr v-else v-for="t in pageItems" :key="t.id" class="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors">
              <td class="table-td font-medium text-slate-800 dark:text-slate-100">{{ t.name }}</td>
              <td class="table-td">{{ t.email }}</td>
              <td class="table-td">{{ t.experience }}</td>
              <td class="table-td">{{ t.phone }}</td>
              <td class="table-td">
                <span class="inline-flex flex-wrap gap-1.5">
                  <span
                    v-for="sub in t.subjects"
                    :key="sub"
                    class="px-2 py-0.5 rounded-full text-xs font-medium bg-brand-blue-50 text-brand-blue-700 dark:bg-brand-blue-500/10 dark:text-brand-blue-400"
                  >
                    {{ sub }}
                  </span>
                </span>
              </td>
              <td class="table-td">
                <span
                  class="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold"
                  :class="
                    t.status === 'Active'
                      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300'
                      : 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300'
                  "
                >
                  {{ t.status }}
                </span>
              </td>
              <td class="table-td">
                <div class="flex items-center justify-end gap-1.5">
                  <button
                    class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 transition-colors"
                    :title="t.status === 'Active' ? 'Block tutor' : 'Unblock tutor'"
                    @click="toggleBlock(t)"
                  >
                    <LockClosedIcon v-if="t.status === 'Active'" class="w-4 h-4" />
                    <LockOpenIcon v-else class="w-4 h-4" />
                  </button>
                  <button
                    class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-rose-50 dark:hover:bg-rose-500/10 text-rose-500 transition-colors"
                    title="Delete tutor"
                    @click="askDelete(t)"
                  >
                    <TrashIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <EmptyState v-if="!loading && pageItems.length === 0" title="No tutors found" message="Try a different name or email." />
      </div>
      <div class="border-t border-slate-100 dark:border-slate-800 px-2">
        <Pagination v-if="!loading && total > 0" :page="page" :per-page="perPage" :total="total" @update:page="page = $event" />
      </div>
    </div>

    <ConfirmModal
      :open="confirmOpen"
      title="Delete this tutor?"
      :message="`This will permanently remove ${target?.name} from the platform.`"
      confirm-label="Delete"
      @confirm="confirmDelete"
      @cancel="confirmOpen = false"
    />
  </div>
</template>
