<script setup>
import { adminApi } from '../../services/adminApi'
import { useServerTable } from '../../composables/useServerTable'
import Pagination from '../../components/ui/Pagination.vue'
import EmptyState from '../../components/ui/EmptyState.vue'
import LoadingRows from '../../components/ui/LoadingRows.vue'

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
      subjects: t.subjects || []
    }))
  }
}

const {
  page,
  perPage,
  total,
  items: pageItems,
  loading,
  error
} = useServerTable(fetchTutors, {
  perPage: 8,
  supportsStatusFilter: false,
  sortFieldMap: {
    name: 'tutor_name',
    email: 'email'
  }
})
</script>

<template>
  <div>
    <div class="mb-5">
      <h2 class="text-xl font-display font-bold text-slate-800 dark:text-slate-100">Tutors</h2>
      <p class="text-sm text-slate-500 dark:text-slate-400 mt-0.5">The educators guiding students through every subject.</p>
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
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-800/60">
            <LoadingRows v-if="loading" :rows="1" :cols="5" />
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
            </tr>
          </tbody>
        </table>
        <EmptyState v-if="!loading && pageItems.length === 0" title="No tutors found" message="Try a different name or email." />
      </div>
      <div class="border-t border-slate-100 dark:border-slate-800 px-2">
        <Pagination v-if="!loading && total > 0" :page="page" :per-page="perPage" :total="total" @update:page="page = $event" />
      </div>
    </div>
  </div>
</template>
