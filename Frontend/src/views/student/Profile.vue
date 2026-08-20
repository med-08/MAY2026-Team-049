<script setup>
import { ref, reactive, onMounted, computed } from "vue"
import PageHeader from "../../components/student/PageHeader.vue"
import InitialsAvatar from "../../components/student/InitialsAvatar.vue"
import { studentApi } from "../../services/studentApi"

import {
  EnvelopeIcon,
  BuildingLibraryIcon,
  UserGroupIcon,
  PencilIcon,
  KeyIcon,
  XMarkIcon,
  PhoneIcon,
} from "@heroicons/vue/24/outline"

const loading = ref(true)
const error = ref("")
const editModalOpen = ref(false)
const passwordModalOpen = ref(false)
const subjectOptions = ref([])
const selectedSubjectToAdd = ref('')
const subjectBusy = ref(false)

const student = ref({
  student_id: null,
  name: "",
  email: "",
  phone: "",
  school: "",
  subjects: [],
  parentName: ""
})

const initials = computed(() => {
  if (!student.value.name) return "ST"
  return student.value.name
    .split(" ")
    .map(part => part[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
})

const editForm = reactive({
  name: "",
  phone: "",
  school: "",
})

const passwordForm = reactive({
  currentPassword: "",
  newPassword: "",
  confirmPassword: "",
})

async function loadProfile() {
  loading.value = true
  error.value = ""

  try {
    const res = await studentApi.getProfile()
    if (res.success && res.data?.student) {
      const s = res.data.student
      student.value = {
        student_id: s.student_id,
        name: s.name || "",
        email: s.email || "",
        phone: s.phone || "",
        school: s.school || "",
        subjects: s.subjects || [],
        parentName: s.parentName || ""
      }
    } else {
      error.value = "Failed to load profile."
    }
  } catch (err) {
    console.error("Profile fetch error:", err)
    error.value = "Failed to load profile."
  } finally {
    loading.value = false
  }
}

async function loadSubjects() {
  try { const r = await studentApi.getSubjects(); subjectOptions.value = r.data?.subjects || [] } catch (e) {}
}
async function addSubject() {
  if (!selectedSubjectToAdd.value || subjectBusy.value) return
  subjectBusy.value = true
  try { await studentApi.addSubject(selectedSubjectToAdd.value); await Promise.all([loadProfile(), loadSubjects()]); selectedSubjectToAdd.value = '' }
  catch (e) { alert(e.message || 'Unable to add subject.') } finally { subjectBusy.value = false }
}
async function removeSubject(subject) {
  const option = subjectOptions.value.find(x => x.subject_name === subject)
  if (!option || subjectBusy.value) return
  if (student.value.subjects.length <= 1) { alert('Keep at least one subject enrolled.'); return }
  subjectBusy.value = true
  try { await studentApi.removeSubject(option.subject_id); await Promise.all([loadProfile(), loadSubjects()]) }
  catch (e) { alert(e.message || 'Unable to remove subject.') } finally { subjectBusy.value = false }
}

onMounted(async () => { await Promise.all([loadProfile(), loadSubjects()]) })

function openEditModal() {
  editForm.name = student.value.name || ""
  editForm.phone = student.value.phone || ""
  editForm.school = student.value.school || ""
  editModalOpen.value = true
}

async function saveProfile() {
  try {
    const payload = {
      name: editForm.name,
      phone: editForm.phone,
      school: editForm.school
    }

    const res = await studentApi.updateProfile(payload)
    if (res.success) {
      student.value.name = editForm.name
      student.value.phone = editForm.phone
      student.value.school = editForm.school
      editModalOpen.value = false
      alert("Profile updated successfully.")
    } else {
      alert(res.message || "Failed to update profile.")
    }
  } catch (err) {
    console.error("Update profile error:", err)
    alert(err.message || "Failed to update profile.")
  }
}

function openPasswordModal() {
  passwordForm.currentPassword = ""
  passwordForm.newPassword = ""
  passwordForm.confirmPassword = ""
  passwordModalOpen.value = true
}

async function changePassword() {
  if (!passwordForm.currentPassword.trim()) {
    alert("Please enter your current password.")
    return
  }

  if (passwordForm.newPassword.length < 8) {
    alert("Password must contain at least 8 characters.")
    return
  }

  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    alert("Passwords do not match.")
    return
  }

  try {
    await studentApi.changePassword(passwordForm)
    passwordModalOpen.value = false
    passwordForm.currentPassword = ""
    passwordForm.newPassword = ""
    passwordForm.confirmPassword = ""
    alert("Password changed successfully.")
  } catch (err) {
    alert(err.message || "Failed to change password.")
  }
}
</script>

<template>
  <div>
    <PageHeader
      title="Profile"
      subtitle="Your personal and academic information."
    />

    <div v-if="loading" class="card max-w-2xl p-6 md:p-8">
      <p class="text-slate-500">Loading profile...</p>
    </div>

    <div v-else-if="error" class="card max-w-2xl p-6 md:p-8 text-red-500">
      {{ error }}
    </div>

    <div v-else class="card max-w-2xl p-6 md:p-8">
      <div class="flex flex-col sm:flex-row items-center sm:items-start gap-5 mb-8">
        <InitialsAvatar :initials="initials" size="lg" />

        <div class="text-center sm:text-left">
          <h2 class="font-display font-bold text-xl">
            {{ student.name || "New Student" }}
          </h2>

          <p class="text-sm text-ink-soft dark:text-slate-400">
            {{ student.school || "No school added" }}
          </p>

        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-8">
        <div class="flex items-start gap-3">
          <EnvelopeIcon class="w-5 h-5 text-brand-blue mt-0.5 shrink-0" />
          <div>
            <p class="text-xs text-ink-soft dark:text-slate-400">Email</p>
            <p class="text-sm font-semibold">{{ student.email || "No email" }}</p>
          </div>
        </div>

        <div class="flex items-start gap-3">
          <PhoneIcon class="w-5 h-5 text-brand-blue mt-0.5 shrink-0" />
          <div>
            <p class="text-xs text-ink-soft dark:text-slate-400">Phone</p>
            <p class="text-sm font-semibold">{{ student.phone || "No phone added" }}</p>
          </div>
        </div>

        <div class="flex items-start gap-3">
          <BuildingLibraryIcon class="w-5 h-5 text-brand-blue mt-0.5 shrink-0" />
          <div>
            <p class="text-xs text-ink-soft dark:text-slate-400">School</p>
            <p class="text-sm font-semibold">{{ student.school || "No school added" }}</p>
          </div>
        </div>

        <div class="flex items-start gap-3 sm:col-span-2">
          <span class="w-5 h-5 text-brand-blue mt-0.5 shrink-0 text-center font-bold">📚</span>
          <div>
            <p class="text-xs text-ink-soft dark:text-slate-400">Subjects Chosen at Registration</p>
            <div v-if="student.subjects.length" class="mt-1 flex flex-wrap gap-2">
              <span v-for="subject in student.subjects" :key="subject" class="inline-flex items-center gap-1 rounded-full bg-brand-blue/10 px-3 py-1 text-xs font-semibold text-brand-blue">{{ subject }}<button type="button" class="ml-1 text-brand-blue/60 hover:text-rose-500" @click="removeSubject(subject)" :disabled="subjectBusy">×</button></span>
            </div>
            <p v-else class="text-sm font-semibold">No subjects selected</p>
            <div class="mt-3 flex max-w-md gap-2">
              <select v-model="selectedSubjectToAdd" class="field flex-1 text-xs"><option value="">Add another subject...</option><option v-for="x in subjectOptions.filter(x => !x.selected)" :key="x.subject_id" :value="x.subject_id">{{ x.subject_name }}</option></select>
              <button type="button" class="rounded-lg bg-gradient-to-r from-teal-500 to-blue-500 px-3 py-2 text-xs font-bold text-white disabled:opacity-50" :disabled="!selectedSubjectToAdd || subjectBusy" @click="addSubject">Add</button>
            </div>
          </div>
        </div>

        <div class="flex items-start gap-3 sm:col-span-2">
          <UserGroupIcon class="w-5 h-5 text-brand-blue mt-0.5 shrink-0" />
          <div>
            <p class="text-xs text-ink-soft dark:text-slate-400">Parent Name</p>
            <p class="text-sm font-semibold">{{ student.parentName || "No parent linked" }}</p>
          </div>
        </div>
      </div>

      <div class="flex flex-col sm:flex-row gap-3">
        <button
          @click="openEditModal"
          class="flex-1 flex items-center justify-center gap-2 rounded-xl bg-rose-100 py-2.5 text-sm font-semibold text-rose-700 transition hover:bg-rose-200 dark:bg-rose-500/15 dark:text-rose-300 dark:hover:bg-rose-500/25"
        >
          <PencilIcon class="w-4 h-4" />
          Edit Profile
        </button>

        <button
          @click="openPasswordModal"
          class="flex-1 flex items-center justify-center gap-2 rounded-xl border border-slate-200 py-2.5 text-sm font-semibold transition hover:bg-slate-50 dark:border-border-dark dark:hover:bg-white/5"
        >
          <KeyIcon class="w-4 h-4" />
          Change Password
        </button>
      </div>

      <transition name="fade">
        <div
          v-if="editModalOpen"
          class="fixed inset-0 z-[90] flex items-center justify-center px-4"
        >
          <div
            class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
            @click="editModalOpen = false"
          />

          <div
            class="relative w-full max-w-lg rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 shadow-2xl"
          >
            <div class="flex items-center justify-between px-6 py-5 border-b border-slate-200 dark:border-slate-700">
              <h2 class="text-xl font-display font-bold">Edit Profile</h2>

              <button
                @click="editModalOpen = false"
                class="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              >
                <XMarkIcon class="w-5 h-5" />
              </button>
            </div>

            <div class="p-6 space-y-5">
              <div>
                <label class="block text-sm font-medium mb-2">Full Name</label>
                <input
                  v-model="editForm.name"
                  type="text"
                  class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-2">Phone</label>
                <input
                  v-model="editForm.phone"
                  type="text"
                  class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-2">School</label>
                <input
                  v-model="editForm.school"
                  type="text"
                  class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
              </div>
            </div>

            <div class="flex justify-end gap-3 px-6 py-5 border-t border-slate-200 dark:border-slate-700">
              <button
                @click="editModalOpen = false"
                class="rounded-xl border border-slate-300 dark:border-slate-700 px-5 py-2.5 font-medium hover:bg-slate-50 dark:hover:bg-slate-800 transition"
              >
                Cancel
              </button>

              <button
                @click="saveProfile"
                class="rounded-xl bg-rose-100 px-5 py-2.5 font-medium text-rose-700 transition hover:bg-rose-200 dark:bg-rose-500/15 dark:text-rose-300 dark:hover:bg-rose-500/25"
              >
                Save Changes
              </button>
            </div>
          </div>
        </div>
      </transition>

      <transition name="fade">
        <div
          v-if="passwordModalOpen"
          class="fixed inset-0 z-[90] flex items-center justify-center px-4"
        >
          <div
            class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
            @click="passwordModalOpen = false"
          />

          <div
            class="relative w-full max-w-lg rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 shadow-2xl"
          >
            <div class="flex items-center justify-between px-6 py-5 border-b border-slate-200 dark:border-slate-700">
              <h2 class="text-xl font-display font-bold">Change Password</h2>

              <button
                @click="passwordModalOpen = false"
                class="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              >
                <XMarkIcon class="w-5 h-5" />
              </button>
            </div>

            <div class="p-6 space-y-5">
              <div>
                <label class="block text-sm font-medium mb-2">Current Password</label>
                <input
                  v-model="passwordForm.currentPassword"
                  type="password"
                  placeholder="Enter current password"
                  class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-2">New Password</label>
                <input
                  v-model="passwordForm.newPassword"
                  type="password"
                  placeholder="Enter new password"
                  class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-2">Confirm Password</label>
                <input
                  v-model="passwordForm.confirmPassword"
                  type="password"
                  placeholder="Confirm new password"
                  class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
              </div>
            </div>

            <div class="flex justify-end gap-3 px-6 py-5 border-t border-slate-200 dark:border-slate-700">
              <button
                @click="changePassword"
                class="rounded-xl border border-slate-200 px-5 py-2.5 font-medium transition hover:bg-slate-50 dark:border-border-dark dark:hover:bg-white/5"
              >
                Update Password
              </button>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>