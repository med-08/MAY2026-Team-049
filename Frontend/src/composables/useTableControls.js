import { ref, computed, watch } from 'vue'
import { globalSearch } from './useSearch'

export function useTableControls(sourceRef, { searchFields = ['name', 'email'], perPage = 8, statusField = null } = {}) {
  const page = ref(1)
  const sortKey = ref(null)
  const sortAsc = ref(true)
  const statusFilter = ref('All')

  const filtered = computed(() => {
    let items = sourceRef.value ?? sourceRef

    if (statusField && statusFilter.value !== 'All') {
      items = items.filter((item) => item[statusField] === statusFilter.value)
    }

    const q = globalSearch.value.trim().toLowerCase()
    if (q) {
      items = items.filter((item) =>
        searchFields.some((f) => String(item[f] ?? '').toLowerCase().includes(q))
      )
    }

    if (sortKey.value) {
      items = [...items].sort((a, b) => {
        const av = String(a[sortKey.value] ?? '').toLowerCase()
        const bv = String(b[sortKey.value] ?? '').toLowerCase()
        if (av < bv) return sortAsc.value ? -1 : 1
        if (av > bv) return sortAsc.value ? 1 : -1
        return 0
      })
    }

    return items
  })

  const total = computed(() => filtered.value.length)

  const pageItems = computed(() => {
    const start = (page.value - 1) * perPage
    return filtered.value.slice(start, start + perPage)
  })

  function toggleSort(key) {
    if (sortKey.value === key) {
      sortAsc.value = !sortAsc.value
    } else {
      sortKey.value = key
      sortAsc.value = true
    }
  }

  watch([globalSearch, statusFilter], () => {
    page.value = 1
  })

  return { page, perPage, total, pageItems, sortKey, sortAsc, toggleSort, statusFilter }
}
