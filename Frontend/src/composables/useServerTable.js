import { ref, watch, onMounted } from 'vue'
import { globalSearch } from './useSearch'

/**
 * Server-backed replacement for useTableControls. Instead of filtering a
 * local mock array in the browser, this calls the real paginated Flask API
 * (search/status/sort_by/order/page/per_page) every time a relevant control
 * changes, and exposes the same shape (page, perPage, total, pageItems-ish
 * `items`, sortKey, sortAsc, toggleSort, statusFilter) that the existing
 * table components already expect.
 *
 * @param {(params: object) => Promise<{data: any[], meta?: {total:number}}>} fetchPage
 *   A function that calls the backend, e.g. (params) => adminApi.listStudents(params)
 * @param {object} [options]
 * @param {number} [options.perPage=8]
 * @param {boolean} [options.supportsStatusFilter=true] - whether the
 *   endpoint accepts a `status` query param (Tutors/Students/Parents do;
 *   plain read-only lists may not)
 * @param {Record<string,string|null>} [options.sortFieldMap] - maps a
 *   template-facing sort key (e.g. 'name') to the backend column name
 *   (e.g. 'student_name'). Keys with no backend equivalent (e.g. a
 *   many-to-many "subjects" list) should map to `null`, which falls back
 *   to the backend's default ordering rather than sending an invalid
 *   sort_by value.
 */
export function useServerTable(fetchPage, {
  perPage = 8,
  supportsStatusFilter = true,
  sortFieldMap = {},
} = {}) {
  const items = ref([])
  const loading = ref(true)
  const error = ref(null)

  const page = ref(1)
  const total = ref(0)
  const sortKey = ref(null)
  const sortAsc = ref(true)
  const statusFilter = ref('All')

  let debounceTimer = null
  let requestSeq = 0

  async function load() {
    const seq = ++requestSeq
    loading.value = true
    error.value = null

    const backendSortBy = sortKey.value ? sortFieldMap[sortKey.value] ?? null : null

    try {
      const res = await fetchPage({
        search: globalSearch.value?.trim() || undefined,
        status: supportsStatusFilter ? statusFilter.value : undefined,
        sort_by: backendSortBy || undefined,
        order: sortAsc.value ? 'asc' : 'desc',
        page: page.value,
        per_page: perPage,
      })

      if (seq !== requestSeq) return // a newer request already landed; ignore this stale one

      items.value = res.data ?? []
      total.value = res.meta?.total ?? items.value.length
    } catch (e) {
      if (seq !== requestSeq) return
      error.value = e.message || 'Failed to load data. Please try again.'
      items.value = []
      total.value = 0
    } finally {
      if (seq === requestSeq) loading.value = false
    }
  }

  function toggleSort(key) {
    if (sortKey.value === key) {
      sortAsc.value = !sortAsc.value
    } else {
      sortKey.value = key
      sortAsc.value = true
    }
  }

  // Debounce free-text search so we don't fire a request per keystroke.
  watch(globalSearch, () => {
    page.value = 1
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(load, 300)
  })

  watch(statusFilter, () => {
    page.value = 1
    load()
  })

  watch([sortKey, sortAsc], load)
  watch(page, load)

  onMounted(load)

  return {
    items,
    loading,
    error,
    page,
    perPage,
    total,
    sortKey,
    sortAsc,
    toggleSort,
    statusFilter,
    reload: load,
  }
}
