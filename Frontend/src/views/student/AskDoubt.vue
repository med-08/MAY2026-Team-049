<script setup>
import { ref, onMounted } from 'vue'
import PageHeader from '../../components/student/PageHeader.vue'
import StatusBadge from '../../components/student/StatusBadge.vue'
import { studentApi } from '../../services/studentApi'

const doubts = ref([])
const tutors = ref([])
const subjects = ref([])
const loading = ref(true)
const error = ref('')
const sending = ref(false)
const sendError = ref('')

const form = ref({
  question: '',
  subject: '',
  tutor_id: ''
})

async function loadDoubts() {
  try {
    const r = await studentApi.getDoubts()
    doubts.value = r.data?.doubts || []
  } catch (e) {
    error.value = e.message
  }
}

async function loadTutors() {
  try {
    const r = await studentApi.getDoubtTutors()
    tutors.value = r.data?.tutors || []
    subjects.value = r.data?.subjects || []
  } catch {
    tutors.value = []
    subjects.value = []
  }
}

onMounted(async () => {
  loading.value = true
  await Promise.all([loadDoubts(), loadTutors()])
  loading.value = false
})

async function send() {
  const question = form.value.question.trim()

  if (
    !question ||
    !form.value.subject ||
    !form.value.tutor_id ||
    sending.value
  ) {
    return
  }

  sending.value = true
  sendError.value = ''

  try {
    const payload = {
      question,
      subject: form.value.subject,
      tutor_id: form.value.tutor_id
    }

    await studentApi.askDoubt(payload)

    form.value = {
      question: '',
      subject: '',
      tutor_id: ''
    }

    await loadDoubts()
  } catch (e) {
    sendError.value = e.message
  } finally {
    sending.value = false
  }
}
</script>

<template>
  <div>
    <PageHeader
      title="Ask Doubt"
      subtitle="Ask your tutor a question and track replies here."
    />

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- Submit a new doubt -->
      <div class="card p-5 lg:order-2 h-fit">
        <h3 class="font-display font-bold mb-4">
          Submit a new doubt
        </h3>

        <!-- Subject -->
        <label
          class="block text-xs font-semibold text-ink-soft dark:text-slate-400 mb-1.5"
        >
          Subject
        </label>

        <select
          v-model="form.subject"
          class="w-full p-2.5 rounded-xl border border-slate-200 dark:border-border-dark bg-transparent mb-4 text-sm"
        >
          <option value="">Select subject</option>

          <option
            v-for="s in subjects"
            :key="s"
            :value="s"
          >
            {{ s }}
          </option>
        </select>

        <!-- Tutor -->
        <label
          class="block text-xs font-semibold text-ink-soft dark:text-slate-400 mb-1.5"
        >
          Tutor
        </label>

        <select
          v-model="form.tutor_id"
          class="w-full p-2.5 rounded-xl border border-slate-200 dark:border-border-dark bg-transparent mb-4 text-sm"
        >
          <option value="">Select tutor</option>

          <option
            v-for="t in tutors"
            :key="t.tutor_id"
            :value="t.tutor_id"
          >
            {{ t.name }}
          </option>
        </select>

        <!-- Question -->
        <label
          class="block text-xs font-semibold text-ink-soft dark:text-slate-400 mb-1.5"
        >
          Your question
        </label>

        <textarea
          v-model="form.question"
          rows="4"
          maxlength="2000"
          placeholder="Type your doubt here..."
          class="w-full p-3 rounded-xl border border-slate-200 dark:border-border-dark bg-transparent text-sm mb-1"
        />

        <p
          class="text-[11px] text-ink-soft dark:text-slate-500 mb-3 text-right"
        >
          {{ form.question.length }}/2000
        </p>

        <p
          v-if="sendError"
          class="text-sm text-danger mb-3"
        >
          {{ sendError }}
        </p>

        <!-- Send -->
        <button
  class="w-full py-2.5 rounded-xl bg-blue-50 text-blue-600 border border-blue-100 font-semibold text-sm hover:bg-blue-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
  :disabled="
    sending ||
    !form.question.trim() ||
    !form.subject ||
    !form.tutor_id
  "
  @click="send"
>
  {{ sending ? 'Sending...' : 'Send' }}
</button>
      </div>

      <!-- Doubt history -->
      <div class="lg:col-span-2 lg:order-1">
        <h3 class="font-display font-bold mb-4">
          Your doubts
        </h3>

        <p
          v-if="loading"
          class="text-slate-500"
        >
          Loading doubts...
        </p>

        <p
          v-else-if="error"
          class="text-danger"
        >
          {{ error }}
        </p>

        <div
          v-else-if="!doubts.length"
          class="card p-8 text-center text-slate-500"
        >
          You haven't asked any doubts yet.
        </div>

        <div
          v-else
          class="space-y-4"
        >
          <div
            v-for="d in doubts"
            :key="d.id"
            class="card p-5"
          >
            <div class="flex justify-between items-start gap-3 mb-2">
              <div>
                <p class="text-xs text-brand-blue font-semibold">
                  {{ d.subject }} &middot; {{ d.tutor }}
                </p>

                <p
                  class="text-xs text-ink-soft dark:text-slate-400 mt-0.5"
                >
                  Asked
                  {{ d.askedAt ? new Date(d.askedAt).toLocaleString() : '' }}
                </p>
              </div>

              <StatusBadge
                :status="d.status === 'Answered' ? 'Completed' : 'Pending'"
              />
            </div>

            <p class="text-sm font-medium mb-3">
              {{ d.question }}
            </p>

            <!-- Tutor reply -->
            <div
              v-if="d.answer"
              class="rounded-xl bg-slate-50 dark:bg-white/5 p-3"
            >
              <p
                class="text-xs font-semibold text-brand-green-dark dark:text-brand-green mb-1"
              >
                Tutor's reply
              </p>

              <p class="text-sm text-ink-soft dark:text-slate-300">
                {{ d.answer }}
              </p>
            </div>

            <p
              v-else
              class="text-xs italic text-ink-soft dark:text-slate-500"
            >
              Waiting for a reply...
            </p>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>