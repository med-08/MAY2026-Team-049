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

    const data = r?.data || {}

    doubts.value =
      data.doubts ||
      data.messages ||
      data.conversations ||
      []
  } catch (e) {
    error.value = e?.message || 'Failed to load doubts.'
  }
}

async function loadTutors() {
  try {
    const r = await studentApi.getDoubtTutors()

    tutors.value = r?.data?.tutors || []
    subjects.value = r?.data?.subjects || []
  } catch {
    tutors.value = []
    subjects.value = []
  }
}

onMounted(async () => {
  loading.value = true

  await Promise.all([
    loadDoubts(),
    loadTutors()
  ])

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

    const response = await studentApi.askDoubt(payload)

    if (
      response &&
      response.success === false
    ) {
      throw new Error(
        response.message || 'Failed to send doubt.'
      )
    }

    form.value = {
      question: '',
      subject: '',
      tutor_id: ''
    }

    await loadDoubts()
  } catch (e) {
    sendError.value =
      e?.message || 'Failed to send doubt.'
  } finally {
    sending.value = false
  }
}

function getTutorName(d) {
  return (
    d?.tutor ||
    d?.tutor_name ||
    d?.tutorName ||
    'Tutor'
  )
}

function getQuestion(d) {
  return (
    d?.question ||
    d?.message ||
    d?.content ||
    ''
  )
}

function getAnswer(d) {
  return (
    d?.answer ||
    d?.reply ||
    d?.reply_message ||
    d?.tutor_reply ||
    ''
  )
}

function getAskedAt(d) {
  return (
    d?.askedAt ||
    d?.asked_at ||
    d?.sent_at ||
    d?.created_at ||
    ''
  )
}

function getStatus(d) {
  const status = String(
    d?.status || ''
  ).toLowerCase()

  if (
    status.includes('answer') ||
    status.includes('complete') ||
    status.includes('replied')
  ) {
    return 'Completed'
  }

  return getAnswer(d)
    ? 'Completed'
    : 'Pending'
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
          <option value="">
            Select subject
          </option>

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
          <option value="">
            Select tutor
          </option>

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
        <div class="flex items-center justify-between mb-4">
          <h3 class="font-display font-bold">
            Your doubts & tutor replies
          </h3>

          <button
            type="button"
            class="text-xs font-semibold text-brand-blue hover:underline"
            @click="loadDoubts"
          >
            Refresh
          </button>
        </div>

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
            v-for="(d, index) in doubts"
            :key="d.id || d.doubt_id || d.message_id || index"
            class="card p-5"
          >

            <!-- Header -->
            <div
              class="flex justify-between items-start gap-3 mb-3"
            >
              <div>
                <p class="text-xs text-brand-blue font-semibold">
                  {{ d.subject || 'General' }}
                  &middot;
                  {{ getTutorName(d) }}
                </p>

                <p
                  class="text-xs text-ink-soft dark:text-slate-400 mt-0.5"
                >
                  Asked
                  {{ getAskedAt(d)
                    ? new Date(getAskedAt(d)).toLocaleString()
                    : ''
                  }}
                </p>
              </div>

              <StatusBadge
                :status="getStatus(d)"
              />
            </div>

            <!-- Student question -->
            <div
              class="rounded-xl bg-blue-50 dark:bg-blue-500/10 border border-blue-100 dark:border-blue-500/20 p-4 mb-3"
            >
              <p
                class="text-xs font-semibold text-blue-600 dark:text-blue-400 mb-1"
              >
                Your question
              </p>

              <p class="text-sm font-medium">
                {{ getQuestion(d) }}
              </p>
            </div>

            <!-- Tutor reply -->
            <div
              v-if="getAnswer(d)"
              class="rounded-xl bg-green-50 dark:bg-green-500/10 border border-green-100 dark:border-green-500/20 p-4"
            >
              <div
                class="flex items-center justify-between mb-1"
              >
                <p
                  class="text-xs font-semibold text-brand-green-dark dark:text-brand-green"
                >
                  Tutor's reply
                </p>

                <span class="text-[11px] text-slate-400">
                  Tutor
                </span>
              </div>

              <p
                class="text-sm text-ink-soft dark:text-slate-300 whitespace-pre-wrap"
              >
                {{ getAnswer(d) }}
              </p>
            </div>

            <!-- No reply -->
            <div
              v-else
              class="rounded-xl bg-slate-50 dark:bg-white/5 p-3"
            >
              <p
                class="text-xs italic text-ink-soft dark:text-slate-500"
              >
                Waiting for a reply from your tutor...
              </p>
            </div>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>