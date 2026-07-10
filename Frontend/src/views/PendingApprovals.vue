<script setup>
import { ref } from 'vue'
import { CheckIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { pendingApprovals } from '../data/mockData'
import { useTableControls } from '../composables/useTableControls'
import { useToast } from '../composables/useToast'
import Pagination from '../components/ui/Pagination.vue'
import EmptyState from '../components/ui/EmptyState.vue'
import LoadingRows from '../components/ui/LoadingRows.vue'

const { showToast } = useToast()

const { page, perPage, total, pageItems } = useTableControls(pendingApprovals, {
  searchFields: ['name', 'email'],
  perPage: 8
})

const loading = ref(true)
setTimeout(() => (loading.value = false), 400)

function approve(item) {
  item.status = 'Approved'
  showToast(`${item.name}'s registration was approved.`, 'success')
}

function reject(item) {
  item.status = 'Rejected'
  showToast(`${item.name}'s registration was rejected.`, 'error')
}

function formatDate(d) {
  return new Date(d).toLocaleDateString('en-US', { day: '2-digit', month: 'short', year: 'numeric' })
}

const statusStyle = (status) => {
  if (status === 'Approved') return 'text-brand-green-700 dark:text-brand-green-400'
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

    <div class="card overflow-hidden">
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
            <tr v-else v-for="item in pageItems" :key="item.id" class="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors">
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
