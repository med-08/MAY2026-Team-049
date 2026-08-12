<template>
  <section class="view on">

    <!-- PROFILE HEADER -->
    <div class="profile-layout">

      <!-- LEFT: PROFILE CARD -->
      <div class="card glass profile-main-card">
        <div class="profile-hero">
          <div class="profile-avatar">
            {{ form.initials || 'T' }}
          </div>

          <div class="profile-identity">
            <h2>{{ form.name || 'Tutor' }}</h2>

            <div class="profile-email">
              {{ form.email || 'No email available' }}
            </div>

            <p class="profile-bio">
              {{ form.bio || 'Add a short professional bio' }}
            </p>
          </div>
        </div>

        <!-- QUICK INFO -->
        <div class="profile-stats">
          <div class="profile-stat">
            <span class="stat-label">Experience</span>
            <strong>
              {{ form.experience !== '' && form.experience != null
                ? `${form.experience} years`
                : 'Not added' }}
            </strong>
          </div>

          <div class="profile-stat">
            <span class="stat-label">Hourly rate</span>
            <strong>
              {{ form.hourlyRate || 'Not added' }}
            </strong>
          </div>

          <div class="profile-stat">
            <span class="stat-label">Availability</span>
            <strong>
              {{ form.availability || 'Not added' }}
            </strong>
          </div>
        </div>
      </div>


      <!-- RIGHT: TEACHING PROFILE -->
      <div class="card glass profile-form-card">

        <div class="profile-section-header">
          <div>
            <h3>Teaching profile</h3>
            <p>Manage your professional information</p>
          </div>

          <button
            v-if="!editing"
            type="button"
            class="edit-btn"
            @click="startEditing"
          >
            <span>✎</span>
            Edit profile
          </button>

          <div v-else class="edit-actions">
            <button
              type="button"
              class="cancel-btn"
              :disabled="saving"
              @click="cancelEditing"
            >
              Cancel
            </button>

            <button
              type="button"
              class="save-btn"
              :disabled="saving"
              @click="saveProfile"
            >
              {{ saving ? 'Saving...' : 'Save changes' }}
            </button>
          </div>
        </div>


        <!-- EDIT FORM -->
        <div class="profile-form">

          <!-- NAME -->
          <div class="form-group">
            <label>Full name</label>

            <input
              v-model="form.name"
              class="field"
              type="text"
              placeholder="Your full name"
              :disabled="!editing"
            />
          </div>


          <!-- EMAIL -->
          <div class="form-group">
            <label>Email</label>

            <input
              v-model="form.email"
              class="field readonly-field"
              type="email"
              disabled
            />

            <small class="field-note">
              Login email cannot be changed here.
            </small>
          </div>


          <!-- PHONE -->
          <div class="form-group">
            <label>Phone</label>

            <input
              v-model="form.phone"
              class="field"
              type="text"
              placeholder="Phone number"
              :disabled="!editing"
            />
          </div>


          <!-- BIO -->
          <div class="form-group full-width">
            <label>Professional bio</label>

            <textarea
              v-model="form.bio"
              class="field textarea"
              rows="3"
              placeholder="Tell students a little about yourself..."
              :disabled="!editing"
            ></textarea>
          </div>


          <!-- EXPERIENCE -->
          <div class="form-group">
            <label>Experience</label>

            <div class="input-with-suffix">
              <input
                v-model="form.experience"
                class="field"
                type="number"
                min="0"
                placeholder="e.g. 5"
                :disabled="!editing"
              />
              <span>years</span>
            </div>
          </div>


          <!-- EDUCATION -->
          <div class="form-group">
            <label>Education</label>

            <input
              v-model="form.education"
              class="field"
              type="text"
              placeholder="e.g. B.Tech Computer Science"
              :disabled="!editing"
            />
          </div>


          <!-- HOURLY RATE -->
          <div class="form-group">
            <label>Hourly rate</label>

            <input
              v-model="form.hourlyRate"
              class="field"
              type="text"
              placeholder="e.g. ₹500/hr"
              :disabled="!editing"
            />
          </div>


          <!-- AVAILABILITY -->
          <div class="form-group">
            <label>Availability</label>

            <input
              v-model="form.availability"
              class="field"
              type="text"
              placeholder="e.g. Mon-Fri, 4 PM - 8 PM"
              :disabled="!editing"
            />
          </div>


          <!-- SUBJECTS -->
          <div class="form-group full-width">
            <label>Subjects</label>

            <input
              v-model="subjectsText"
              class="field"
              type="text"
              placeholder="e.g. Maths, Physics, English"
              :disabled="!editing"
            />

            <small class="field-note">
              Separate multiple subjects with commas.
            </small>

            <div
              v-if="form.subjects.length"
              class="chips"
            >
              <span
                v-for="subject in form.subjects"
                :key="subject"
                class="badge live"
              >
                {{ subject }}
              </span>
            </div>
          </div>


          <!-- LANGUAGES -->
          <div class="form-group full-width">
            <label>Teaching languages</label>

            <input
              v-model="languagesText"
              class="field"
              type="text"
              placeholder="e.g. English, Hindi"
              :disabled="!editing"
            />

            <small class="field-note">
              Separate multiple languages with commas.
            </small>

            <div
              v-if="form.languages.length"
              class="chips"
            >
              <span
                v-for="language in form.languages"
                :key="language"
                class="badge"
              >
                {{ language }}
              </span>
            </div>
          </div>

        </div>


        <!-- STATUS MESSAGE -->
        <div
          v-if="message"
          class="profile-message"
          :class="{ error: messageType === 'error' }"
        >
          {{ message }}
        </div>

      </div>

    </div>

  </section>
</template>


<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { tutorApi } from '../../services/tutorApi'

const props = defineProps({
  tutor: {
    type: Object,
    required: true
  }
})

const editing = ref(false)
const saving = ref(false)
const message = ref('')
const messageType = ref('success')

const form = reactive({
  userId: null,
  name: '',
  email: '',
  phone: '',
  bio: '',
  experience: '',
  education: '',
  hourlyRate: '',
  availability: '',
  subjects: [],
  languages: [],
  initials: 'T'
})

const subjectsText = ref('')
const languagesText = ref('')


function copyTutorToForm(source) {
  form.userId = source?.userId ?? null
  form.name = source?.name ?? ''
  form.email = source?.email ?? ''
  form.phone = source?.phone ?? ''
  form.bio = source?.bio ?? ''
  form.experience = source?.experience ?? ''
  form.education = source?.education ?? ''
  form.hourlyRate = source?.hourlyRate ?? ''
  form.availability = source?.availability ?? ''

  form.subjects = Array.isArray(source?.subjects)
    ? [...source.subjects]
    : []

  form.languages = Array.isArray(source?.languages)
    ? [...source.languages]
    : []

  form.initials = source?.initials || getInitials(form.name)

  subjectsText.value = form.subjects.join(', ')
  languagesText.value = form.languages.join(', ')
}


function getInitials(name) {
  return String(name || 'Tutor')
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
}


watch(
  () => props.tutor,
  (newTutor) => {
    if (!editing.value) {
      copyTutorToForm(newTutor)
    }
  },
  {
    immediate: true,
    deep: true
  }
)


function startEditing() {
  message.value = ''
  messageType.value = 'success'

  copyTutorToForm(props.tutor)

  editing.value = true
}


function cancelEditing() {
  copyTutorToForm(props.tutor)

  editing.value = false
  message.value = ''
}


function cleanList(value) {
  return String(value || '')
    .split(',')
    .map(item => item.trim())
    .filter(Boolean)
    .filter((item, index, arr) => arr.indexOf(item) === index)
}


const preparedSubjects = computed(() => {
  return cleanList(subjectsText.value)
})


const preparedLanguages = computed(() => {
  return cleanList(languagesText.value)
})


async function saveProfile() {
  if (saving.value) return

  saving.value = true
  message.value = ''

  try {
    const payload = {
      name: form.name.trim(),
      phone: form.phone.trim(),
      bio: form.bio.trim(),
      experience: form.experience === ''
        ? ''
        : Number(form.experience),
      education: form.education.trim(),
      hourlyRate: form.hourlyRate.trim(),
      availability: form.availability.trim(),
      subjects: preparedSubjects.value,
      languages: preparedLanguages.value
    }

    await tutorApi.updateProfile(payload)

    form.subjects = [...preparedSubjects.value]
    form.languages = [...preparedLanguages.value]
    form.initials = getInitials(form.name)

    subjectsText.value = form.subjects.join(', ')
    languagesText.value = form.languages.join(', ')

    editing.value = false

    messageType.value = 'success'
    message.value = 'Profile updated successfully.'

    // Keep the dashboard/profile state in sync without forcing a page reload.
    if (typeof window !== 'undefined') {
      window.dispatchEvent(
        new CustomEvent('tutor-profile-updated')
      )
    }

  } catch (error) {
    console.error('[TutorProfile] Update failed:', error)

    messageType.value = 'error'
    message.value =
      error?.message ||
      'Unable to update profile. Please try again.'
  } finally {
    saving.value = false
  }
}
</script>


<style scoped>
.profile-layout {
  display: grid;
  grid-template-columns: 1fr 1.15fr;
  gap: 18px;
  align-items: stretch;
}

.profile-main-card,
.profile-form-card {
  min-width: 0;
}

.profile-hero {
  display: flex;
  align-items: center;
  gap: 18px;
  min-height: 210px;
}

.profile-avatar {
  width: 92px;
  height: 92px;
  flex: 0 0 92px;
  border-radius: 26px;

  display: flex;
  align-items: center;
  justify-content: center;

  font-size: 34px;
  font-weight: 800;
  color: white;

  background: linear-gradient(
    135deg,
    #6755ff,
    #36b9ec
  );

  box-shadow:
    0 14px 32px rgba(91, 77, 255, 0.24);
}

.profile-identity h2 {
  margin: 0;
  font-size: 28px;
  line-height: 1.1;
}

.profile-email {
  margin-top: 7px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}

.profile-bio {
  margin: 13px 0 0;
  color: var(--muted);
  line-height: 1.55;
  font-size: 13px;
}

.profile-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 18px;
}

.profile-stat {
  padding: 14px;
  border: 1px solid rgba(120, 120, 180, 0.12);
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.38);
}

.stat-label {
  display: block;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  margin-bottom: 7px;
}

.profile-stat strong {
  display: block;
  font-size: 13px;
  color: var(--text);
  line-height: 1.35;
}

.profile-section-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 18px;
}

.profile-section-header h3 {
  margin: 0;
}

.profile-section-header p {
  margin: 5px 0 0;
  color: var(--muted);
  font-size: 12px;
}

.edit-btn,
.save-btn,
.cancel-btn {
  border: 0;
  border-radius: 12px;
  padding: 10px 15px;
  font-weight: 700;
  font-size: 12px;
  cursor: pointer;
  transition: 0.2s ease;
  white-space: nowrap;
}

.edit-btn {
  color: #604dff;
  background: rgba(103, 85, 255, 0.11);
  border: 1px solid rgba(103, 85, 255, 0.18);
}

.edit-btn:hover {
  transform: translateY(-1px);
  background: rgba(103, 85, 255, 0.17);
}

.edit-btn span {
  margin-right: 5px;
}

.edit-actions {
  display: flex;
  gap: 8px;
}

.cancel-btn {
  color: var(--muted);
  background: rgba(120, 120, 150, 0.08);
}

.save-btn {
  color: white;
  background: linear-gradient(
    135deg,
    #6554ff,
    #35afe8
  );
  box-shadow: 0 8px 20px rgba(91, 77, 255, 0.2);
}

.save-btn:hover {
  transform: translateY(-1px);
}

.save-btn:disabled,
.cancel-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.profile-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 13px;
}

.form-group {
  min-width: 0;
}

.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  display: block;
  margin-bottom: 7px;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
}

.field {
  width: 100%;
  box-sizing: border-box;
}

.textarea {
  resize: vertical;
  min-height: 82px;
}

.readonly-field {
  opacity: 0.7;
  cursor: not-allowed;
}

.field:disabled:not(.readonly-field) {
  cursor: default;
  opacity: 0.82;
}

.field-note {
  display: block;
  margin-top: 5px;
  color: var(--muted);
  font-size: 10px;
}

.input-with-suffix {
  position: relative;
}

.input-with-suffix .field {
  padding-right: 60px;
}

.input-with-suffix span {
  position: absolute;
  right: 13px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted);
  font-size: 11px;
  pointer-events: none;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 9px;
}

.profile-message {
  margin-top: 14px;
  padding: 10px 13px;
  border-radius: 11px;
  font-size: 12px;
  color: #168b69;
  background: rgba(24, 177, 135, 0.09);
  border: 1px solid rgba(24, 177, 135, 0.15);
}

.profile-message.error {
  color: #d94b61;
  background: rgba(217, 75, 97, 0.08);
  border-color: rgba(217, 75, 97, 0.14);
}

@media (max-width: 900px) {
  .profile-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 620px) {
  .profile-form {
    grid-template-columns: 1fr;
  }

  .full-width {
    grid-column: auto;
  }

  .profile-stats {
    grid-template-columns: 1fr;
  }

  .profile-section-header {
    flex-direction: column;
  }

  .edit-actions {
    width: 100%;
  }

  .edit-actions button {
    flex: 1;
  }
}
</style>