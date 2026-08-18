<script setup>
import { ref, onMounted } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import { studentApi } from '../../services/studentApi'

const items = ref([])
const loading = ref(true)
const error = ref('')

const typeStyle = {
  PDF: 'bg-rose-50 text-rose-600',
  Note: 'bg-blue-50 text-blue-600',
  Notes: 'bg-blue-50 text-blue-600',
  Link: 'bg-violet-50 text-violet-600',
  Video: 'bg-amber-50 text-amber-600',
  Document: 'bg-emerald-50 text-emerald-600'
}

function getTypeClass(type) {
  return typeStyle[type] || 'bg-slate-100 text-slate-600'
}

function getIcon(type) {
  const icons = {
    PDF: '📄',
    Note: '📝',
    Notes: '📝',
    Link: '🔗',
    Video: '▶',
    Document: '📚'
  }

  return icons[type] || '📖'
}

function getResourceUrl(link) {
  if (!link) return '#'

  return link.startsWith('http')
    ? link
    : `http://localhost:5000${link}`
}

async function load() {
  loading.value = true
  error.value = ''

  try {
    const r = await studentApi.getResources()
    items.value = r.data?.resources || []
  } catch (e) {
    error.value = e?.message || 'Unable to load resources.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>

    <PageHeader
      title="Study Resources"
      subtitle="Notes, links and learning materials shared by your tutor."
    />

    <!-- Small summary -->
    <div
      v-if="!loading && !error && items.length"
      class="mb-5 flex items-center gap-2"
    >
      <span
        class="rounded-full bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-600"
      >
        {{ items.length }}
        {{ items.length === 1 ? 'Resource' : 'Resources' }}
      </span>

      <span class="text-xs text-slate-400">
        Shared by your tutors
      </span>
    </div>

    <!-- Loading -->
    <div
      v-if="loading"
      class="py-10 text-center"
    >
      <div
        class="mx-auto mb-3 h-7 w-7 animate-spin rounded-full border-2 border-slate-200 border-t-teal-500"
      ></div>

      <p class="text-sm text-slate-500">
        Loading resources...
      </p>
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-600"
    >
      {{ error }}

      <button
        class="ml-2 font-semibold underline"
        @click="load"
      >
        Retry
      </button>
    </div>

    <!-- Empty -->
    <div
      v-else-if="!items.length"
      class="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-6 py-10 text-center dark:border-slate-700 dark:bg-white/5"
    >
      <div class="text-3xl">
        📚
      </div>

      <p class="mt-2 font-semibold text-slate-700 dark:text-slate-200">
        No resources yet
      </p>

      <p class="mt-1 text-xs text-slate-500">
        Your tutor's notes, PDFs and learning links will appear here.
      </p>
    </div>

    <!-- Resources -->
    <div
      v-else
      class="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3"
    >

      <article
        v-for="r in items"
        :key="r.resource_id"
        class="group relative overflow-hidden rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition-all hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md dark:border-slate-700 dark:bg-slate-900"
      >

        <!-- Top -->
        <div class="flex items-start justify-between gap-3">

          <div
            class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-lg"
            :class="getTypeClass(r.resource_type)"
          >
            {{ getIcon(r.resource_type) }}
          </div>

          <span
            class="rounded-full px-2.5 py-1 text-[10px] font-bold"
            :class="getTypeClass(r.resource_type)"
          >
            {{ r.resource_type || 'Resource' }}
          </span>

        </div>

        <!-- Content -->
        <div class="mt-3">

          <p
            class="mb-1 text-[11px] font-bold uppercase tracking-wide text-blue-500"
          >
            {{ r.subject || 'General' }}
          </p>

          <h3
            class="line-clamp-2 min-h-[40px] text-sm font-bold text-slate-800 dark:text-white"
            :title="r.resource_title"
          >
            {{ r.resource_title }}
          </h3>

        </div>

        <!-- Action -->
        <a
          v-if="r.resource_link"
          :href="getResourceUrl(r.resource_link)"
          target="_blank"
          rel="noopener noreferrer"
          class="mt-4 flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-teal-500 to-blue-500 px-3 py-2 text-xs font-bold text-white transition hover:opacity-90"
        >
          Open Resource
          <span>↗</span>
        </a>

        <span
          v-else
          class="mt-4 block text-center text-xs text-slate-400"
        >
          Resource link unavailable
        </span>

      </article>

    </div>

  </div>
</template>