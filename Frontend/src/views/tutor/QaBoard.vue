<template>
  <section class="view on">
    <div class="grid g2col reveal qa-layout">

      <!-- ==================== Q&A BOARD ==================== -->
      <div class="card glass qa-board">

        <div class="ch qa-header">
          <div>
            <h3>Shared Q&amp;A board</h3>
            <div class="qa-subtitle">
              Questions and answers shared with your students
            </div>
          </div>

          <span class="visibility-pill">
            <span class="status-dot"></span>
            Student visible
          </span>
        </div>

        <div
          v-if="entries.length"
          class="qa-list"
        >
          <div
            v-for="entry in entries"
            :key="entry.faqId"
            class="qa-item"
          >

            <!-- Question -->
            <div class="question-section">

              <div class="question-icon">
                ?
              </div>

              <div class="question-content">
                <div class="question-top">
                  <div class="question-text">
                    {{ entry.question }}
                  </div>

                  <span class="live-badge">
                    <span></span>
                    Live
                  </span>
                </div>

                <div
                  v-if="entry.meta"
                  class="question-meta"
                >
                  {{ entry.meta }}
                </div>
              </div>

            </div>

            <!-- Answer -->
            <div
              v-if="entry.answer && entry.answer.trim()"
              class="answer-section"
            >
              <div class="answer-icon">
                ✓
              </div>

              <div class="answer-content">
                <div class="answer-label">
                  Tutor's answer
                </div>

                <div class="answer-text">
                  {{ entry.answer }}
                </div>
              </div>
            </div>

            <!-- No answer -->
            <div
              v-else
              class="pending-answer"
            >
              <span>Waiting for an answer</span>
            </div>

          </div>
        </div>

        <!-- Empty state -->
        <div
          v-else
          class="empty-qa"
        >
          <div class="empty-icon">?</div>
          <div class="empty-title">No questions yet</div>
          <div class="empty-text">
            Questions posted by students will appear here.
          </div>
        </div>

      </div>


      <!-- ==================== POST ANSWER ==================== -->
      <div class="card glass answer-card">

        <div class="ch">
          <div>
            <h3>Post an answer</h3>
            <div class="qa-subtitle">
              Share one answer with all your students
            </div>
          </div>
        </div>

        <div class="form-body">

          <div class="form-group">
            <label
              class="lab"
              for="qa-question"
            >
              Question
            </label>

            <div class="input-wrap">
              <span class="input-icon">?</span>

              <input
                id="qa-question"
                v-model="question"
                class="field"
                placeholder="What are students asking?"
                maxlength="500"
              >
            </div>

            <div class="character-count">
              {{ question.length }}/500
            </div>
          </div>


          <div class="form-group">
            <label
              class="lab"
              for="qa-answer"
            >
              Answer
            </label>

            <textarea
              id="qa-answer"
              v-model="answer"
              class="field answer-input"
              rows="5"
              placeholder="Write a clear answer for everyone…"
              maxlength="3000"
            ></textarea>

            <div class="character-count">
              {{ answer.length }}/3000
            </div>
          </div>


          <button
            class="publish-btn"
            type="button"
            :disabled="publishing || !canPublish"
            @click="publish"
          >
            <span v-if="!publishing">Publish answer</span>
            <span v-else>Publishing…</span>

            <span
              v-if="!publishing"
              class="arrow"
            >
              →
            </span>
          </button>


          <div
            v-if="message"
            class="success-message"
          >
            <span class="success-icon">✓</span>
            {{ message }}
          </div>


          <div class="helper-box">
            <div class="helper-icon">
              ✦
            </div>

            <div>
              <div class="helper-title">
                One answer, everyone informed
              </div>

              <div class="helper-text">
                Published answers are shared across your students.
              </div>
            </div>
          </div>

        </div>
      </div>

    </div>
  </section>
</template>


<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  entries: {
    type: Array,
    required: true
  }
})

const emit = defineEmits([
  'publish',
  'toast'
])

const question = ref('')
const answer = ref('')
const publishing = ref(false)
const message = ref('')

const canPublish = computed(() => {
  return (
    question.value.trim().length > 0 &&
    answer.value.trim().length > 0
  )
})

async function publish() {
  if (!canPublish.value || publishing.value) {
    return
  }

  publishing.value = true
  message.value = ''

  try {
    emit('publish', {
      question: question.value.trim(),
      answer: answer.value.trim()
    })

    question.value = ''
    answer.value = ''

    message.value = 'Answer published successfully.'
  } catch (error) {
    message.value =
      error?.message || 'Unable to publish answer.'

    emit('toast', message.value)
  } finally {
    publishing.value = false
  }
}
</script>


<style scoped>

/* =========================================================
   LAYOUT
========================================================= */

.qa-layout {
  grid-template-columns: 1.45fr 0.9fr;
  gap: 18px;
  align-items: start;
}

.qa-board,
.answer-card {
  overflow: hidden;
}


/* =========================================================
   HEADER
========================================================= */

.qa-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 15px;
}

.qa-subtitle {
  margin-top: 4px;
  font-size: 12px;
  color: var(--muted);
  line-height: 1.4;
}

.visibility-pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 7px 11px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.07);
  border: 1px solid rgba(34, 197, 94, 0.16);
  color: #159a61;
  font-size: 10px;
  font-weight: 700;
  white-space: nowrap;
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #20b978;
  box-shadow: 0 0 0 3px rgba(32, 185, 120, 0.10);
}


/* =========================================================
   Q&A LIST
========================================================= */

.qa-list {
  margin-top: 4px;
}

.qa-item {
  position: relative;
  padding: 15px 0;
  border-bottom: 1px solid rgba(100, 110, 150, 0.12);
}

.qa-item:last-child {
  border-bottom: none;
  padding-bottom: 3px;
}


/* =========================================================
   QUESTION
========================================================= */

.question-section {
  display: flex;
  align-items: flex-start;
  gap: 11px;
}

.question-icon {
  flex: 0 0 30px;
  width: 30px;
  height: 30px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 9px;

  background: linear-gradient(
    135deg,
    rgba(105, 83, 255, 0.12),
    rgba(50, 174, 239, 0.10)
  );

  border: 1px solid rgba(105, 83, 255, 0.13);

  color: #6757ee;
  font-size: 14px;
  font-weight: 800;
}

.question-content {
  flex: 1;
  min-width: 0;
}

.question-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.question-text {
  color: var(--text);
  font-size: 14px;
  font-weight: 700;
  line-height: 1.45;
}

.question-meta {
  margin-top: 4px;
  color: var(--muted);
  font-size: 11.5px;
}


/* =========================================================
   LIVE BADGE
========================================================= */

.live-badge {
  flex: 0 0 auto;

  display: inline-flex;
  align-items: center;
  gap: 5px;

  padding: 4px 8px;

  border-radius: 999px;

  background: rgba(28, 190, 124, 0.07);
  border: 1px solid rgba(28, 190, 124, 0.18);

  color: #159a61;

  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.live-badge span {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #20b978;
}


/* =========================================================
   ANSWER
========================================================= */

.answer-section {
  display: flex;
  gap: 10px;

  margin-top: 10px;
  margin-left: 41px;

  padding: 10px 12px;

  border-radius: 10px;

  background: rgba(95, 84, 235, 0.045);

  border: 1px solid rgba(95, 84, 235, 0.08);

  transition: background 0.2s ease;
}

.answer-section:hover {
  background: rgba(95, 84, 235, 0.065);
}

.answer-icon {
  flex: 0 0 22px;

  width: 22px;
  height: 22px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 7px;

  background: rgba(31, 185, 119, 0.10);

  color: #159a61;

  font-size: 11px;
  font-weight: 900;
}

.answer-content {
  min-width: 0;
  flex: 1;
}

.answer-label {
  margin-bottom: 3px;

  color: var(--muted);

  font-size: 9px;
  font-weight: 800;

  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.answer-text {
  color: var(--text);

  font-size: 12.5px;
  line-height: 1.55;

  white-space: pre-wrap;
  word-break: break-word;
}


/* =========================================================
   PENDING ANSWER
========================================================= */

.pending-answer {
  margin-top: 8px;
  margin-left: 41px;

  color: var(--muted);

  font-size: 10.5px;
  font-style: italic;
}


/* =========================================================
   FORM
========================================================= */

.form-body {
  margin-top: 3px;
}

.form-group {
  position: relative;
  margin-bottom: 14px;
}

.input-wrap {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 13px;
  top: 50%;
  transform: translateY(-50%);

  width: 21px;
  height: 21px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 6px;

  background: rgba(105, 83, 255, 0.08);

  color: #6757ee;

  font-size: 11px;
  font-weight: 800;

  z-index: 2;
}

.input-wrap .field {
  padding-left: 43px;
}

.answer-input {
  min-height: 125px;
}

.character-count {
  position: absolute;
  right: 5px;
  bottom: -14px;

  color: var(--muted);

  font-size: 8.5px;
  opacity: 0.7;
}


/* =========================================================
   PUBLISH BUTTON
========================================================= */

.publish-btn {
  width: 100%;
  min-height: 43px;

  margin-top: 7px;

  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;

  border: none;
  border-radius: 11px;

  background: linear-gradient(
    135deg,
    #6752f5,
    #35aeea
  );

  color: white;

  font-size: 13px;
  font-weight: 750;

  cursor: pointer;

  box-shadow:
    0 9px 20px rgba(91, 83, 235, 0.18);

  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    opacity 0.18s ease;
}

.publish-btn:hover:not(:disabled) {
  transform: translateY(-1px);

  box-shadow:
    0 12px 25px rgba(91, 83, 235, 0.25);
}

.publish-btn:active:not(:disabled) {
  transform: translateY(0);
}

.publish-btn:disabled {
  opacity: 0.48;
  cursor: not-allowed;
  box-shadow: none;
}

.arrow {
  font-size: 17px;
  line-height: 1;
}


/* =========================================================
   SUCCESS MESSAGE
========================================================= */

.success-message {
  display: flex;
  align-items: center;
  gap: 7px;

  margin-top: 10px;
  padding: 8px 10px;

  border-radius: 8px;

  background: rgba(31, 185, 119, 0.07);

  color: #159a61;

  font-size: 11px;
  font-weight: 650;
}

.success-icon {
  display: flex;
  align-items: center;
  justify-content: center;

  width: 17px;
  height: 17px;

  border-radius: 50%;

  background: rgba(31, 185, 119, 0.12);

  font-size: 9px;
}


/* =========================================================
   HELPER
========================================================= */

.helper-box {
  display: flex;
  align-items: center;
  gap: 9px;

  margin-top: 13px;
  padding: 10px 11px;

  border-radius: 10px;

  background: rgba(100, 110, 150, 0.045);

  border: 1px solid rgba(100, 110, 150, 0.08);
}

.helper-icon {
  flex: 0 0 27px;

  width: 27px;
  height: 27px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 8px;

  background: rgba(105, 83, 255, 0.09);

  color: #6757ee;

  font-size: 13px;
}

.helper-title {
  color: var(--text);

  font-size: 10.5px;
  font-weight: 750;
}

.helper-text {
  margin-top: 2px;

  color: var(--muted);

  font-size: 9.5px;
  line-height: 1.35;
}


/* =========================================================
   EMPTY STATE
========================================================= */

.empty-qa {
  padding: 30px 15px;
  text-align: center;
}

.empty-icon {
  width: 40px;
  height: 40px;

  margin: 0 auto 9px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 12px;

  background: rgba(105, 83, 255, 0.08);

  color: #6757ee;

  font-size: 18px;
  font-weight: 800;
}

.empty-title {
  color: var(--text);

  font-size: 13px;
  font-weight: 750;
}

.empty-text {
  margin-top: 4px;

  color: var(--muted);

  font-size: 10.5px;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (max-width: 900px) {
  .qa-layout {
    grid-template-columns: 1fr !important;
  }
}

@media (max-width: 560px) {
  .qa-header {
    flex-direction: column;
  }

  .question-top {
    flex-direction: column;
    gap: 6px;
  }

  .answer-section,
  .pending-answer {
    margin-left: 0;
  }
}

</style>