<script setup>
import { CheckIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { adminApi } from '../../services/adminApi'
import { useServerTable } from '../../composables/useServerTable'
import { useToast } from '../../composables/useToast'
import Pagination from '../../components/ui/Pagination.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import LoadingRows from '../../components/ui/LoadingRows.vue'

const { showToast } = useToast()

// The backend combines pending Students/Tutors/Parents into one list, with
// field names (registration_date/type) slightly different from the mock's
// (registrationDate/role). Map them here so the template stays unchanged.
async function fetchApprovals() {
  const res = await adminApi.listApprovals('Pending')
  return {
    meta: res.meta,
    data: res.data.map((item) => ({
      id: item.id,
      entityType: item.type.toLowerCase(), // 'student' | 'tutor' | 'parent', for API calls
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
} = useServerTable(fetchApprovals, { perPage: 8, supportsStatusFilter: false })

// NOTE (assumption/UX change from the mock): the backend's approvals list
// only ever returns entries that are currently Pending, so once an item is
// approved/rejected it simply disappears from this queue after reload()
// rather than staying visible with a greyed-out "Approved"/"Rejected"
// badge. This matches how a real "review queue" behaves.
async function approve(item) {
  try {
    await adminApi.approveEntity(item.entityType, item.id)
    showToast(`${item.name}'s registration was approved.`, 'success')
    await reload()
  } catch (e) {
    showToast(e.message || 'Failed to approve registration.', 'error')
  }
}

async function reject(item) {
  try {
    await adminApi.rejectEntity(item.entityType, item.id)
    showToast(`${item.name}'s registration was rejected.`, 'error')
    await reload()
  } catch (e) {
    showToast(e.message || 'Failed to reject registration.', 'error')
  }
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' })
}

const statusStyle = (status) => {
  if (status === 'Active') return 'text-brand-green-700 dark:text-brand-green-400'
  if (status === 'Rejected') return 'text-rose-600 dark:text-rose-400'
  return 'text-brand-orange-700 dark:text-brand-orange-400'
}
</script>

<template>
  <div>
    <div class="mb-5">
      <h2 class="text-xl font-display font-bold text-slate-800 dark:text-slate-100">Pending Approvals</h2>
      <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Review new sign-ups before they join the platform.</p>
    </div>

    <EmptyState
      v-if="error"
      title="Couldn't load pending approvals"
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
              <th class="table-th">Name</th>
              <th class="table-th">Email ID</th>
              <th class="table-th">Role</th>
              <th class="table-th">Registration Date</th>
              <th class="table-th">Status</th>
              <th class="table-th text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-800/60">
            <LoadingRows v-if="loading" :rows="6" :cols="6" />
            <tr v-else v-for="item in pageItems" :key="`${item.entityType}-${item.id}`" class="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors">
              <td class="table-td font-medium text-slate-800 dark:text-slate-100">{{ item.name }}</td>
              <td class="table-td">{{ item.email }}</td>
              <td class="table-td">{{ item.role }}</td>
              <td class="table-td">{{ formatDate(item.registrationDate) }}</td>
              <td class="table-td font-semibold" :class="statusStyle(item.status)">{{ item.status }}</td>
              <td class="table-td">
                <div class="flex items-center justify-end gap-1.5">
                  <button
                    class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-brand-green-50 dark:hover:bg-brand-green-500/10 text-brand-green-600 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    title="Approve"
                    :disabled="item.status !== 'Pending'"
                    @click="approve(item)"
                  >
                    <CheckIcon class="w-4 h-4" />
                  </button>
                  <button
                    class="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-rose-50 dark:hover:bg-rose-500/10 text-rose-500 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                    title="Reject"
                    :disabled="item.status !== 'Pending'"
                    @click="reject(item)"
                  >
                    <XMarkIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <EmptyState v-if="!loading && pageItems.length === 0" title="No pending approvals" message="Try a different name or email." />
      </div>
      <div class="border-t border-slate-100 dark:border-slate-800 px-2">
        <Pagination v-if="!loading && total > 0" :page="page" :per-page="perPage" :total="total" @update:page="page = $event" />
      </div>
    </div>
  </div>
</template>
