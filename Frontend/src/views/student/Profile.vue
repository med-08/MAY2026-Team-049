<script setup>
import { ref, reactive } from "vue"
import PageHeader from "../../components/student/PageHeader.vue"
import InitialsAvatar from "../../components/student/InitialsAvatar.vue"

import {
  EnvelopeIcon,
  BuildingLibraryIcon,
  UserGroupIcon,
  PencilIcon,
  KeyIcon,
  XMarkIcon,
} from "@heroicons/vue/24/outline"

import { student } from "../../data/studentMockData"

const editModalOpen = ref(false)
const passwordModalOpen = ref(false)

const editForm = reactive({
  name: student.name,
  email: student.email,
  school: student.school,
  parentName: student.parentName,
})

const passwordForm = reactive({
  currentPassword: "",
  newPassword: "",
  confirmPassword: "",
})

function openEditModal() {
  editForm.name = student.name
  editForm.email = student.email
  editForm.school = student.school
  editForm.parentName = student.parentName

  editModalOpen.value = true
}

function saveProfile() {
  student.name = editForm.name
  student.email = editForm.email
  student.school = editForm.school
  student.parentName = editForm.parentName

  editModalOpen.value = false
  alert("Profile updated successfully.")
}

function openPasswordModal() {
  passwordForm.currentPassword = ""
  passwordForm.newPassword = ""
  passwordForm.confirmPassword = ""

  passwordModalOpen.value = true
}

function changePassword() {
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

  passwordModalOpen.value = false

  passwordForm.currentPassword = ""
  passwordForm.newPassword = ""
  passwordForm.confirmPassword = ""

  alert("Password changed successfully.")
}
</script>

<template>
  <div>
    <PageHeader
      title="Profile"
      subtitle="Your personal and academic information."
    />

    <div class="card max-w-2xl p-6 md:p-8">
      <!-- Header -->
      <div
        class="flex flex-col sm:flex-row items-center sm:items-start gap-5 mb-8"
      >
        <InitialsAvatar
          :initials="student.initials"
          size="lg"
        />

        <div class="text-center sm:text-left">
          <h2 class="font-display font-bold text-xl">
            {{ student.name }}
          </h2>

          <p class="text-sm text-ink-soft dark:text-slate-400">
            {{ student.school }}
          </p>

          <div
            class="flex flex-wrap justify-center sm:justify-start gap-2 mt-3"
          >
            <span
              v-for="subject in student.subjects"
              :key="subject"
              class="rounded-full bg-brand-blue/10 px-3 py-1 text-xs font-semibold text-brand-blue"
            >
              {{ subject }}
            </span>
          </div>
        </div>
      </div>

      <!-- Information -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-8">
        <div class="flex items-start gap-3">
          <EnvelopeIcon
            class="w-5 h-5 text-brand-blue mt-0.5 shrink-0"
          />

          <div>
            <p class="text-xs text-ink-soft dark:text-slate-400">
              Email
            </p>

            <p class="text-sm font-semibold">
              {{ student.email }}
            </p>
          </div>
        </div>

        <div class="flex items-start gap-3">
          <BuildingLibraryIcon
            class="w-5 h-5 text-brand-blue mt-0.5 shrink-0"
          />

          <div>
            <p class="text-xs text-ink-soft dark:text-slate-400">
              School
            </p>

            <p class="text-sm font-semibold">
              {{ student.school }}
            </p>
          </div>
        </div>

        <div class="flex items-start gap-3 sm:col-span-2">
          <UserGroupIcon
            class="w-5 h-5 text-brand-blue mt-0.5 shrink-0"
          />

          <div>
            <p class="text-xs text-ink-soft dark:text-slate-400">
              Parent Name
            </p>

            <p class="text-sm font-semibold">
              {{ student.parentName }}
            </p>
          </div>
        </div>
      </div>

      <!-- Buttons -->
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
            <!-- Edit Profile Modal -->
      <transition name="fade">
        <div
          v-if="editModalOpen"
          class="fixed inset-0 z-[90] flex items-center justify-center px-4"
        >
          <!-- Backdrop -->
          <div
            class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
            @click="editModalOpen = false"
          />

          <!-- Modal -->
          <div
            class="relative w-full max-w-lg rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 shadow-2xl"
          >
            <!-- Header -->
            <div
              class="flex items-center justify-between px-6 py-5 border-b border-slate-200 dark:border-slate-700"
            >
              <h2 class="text-xl font-display font-bold">
                Edit Profile
              </h2>

              <button
                @click="editModalOpen = false"
                class="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              >
                <XMarkIcon class="w-5 h-5" />
              </button>
            </div>

            <!-- Form -->
            <div class="p-6 space-y-5">
              <div>
                <label class="block text-sm font-medium mb-2">
                  Full Name
                </label>

                <input
                  v-model="editForm.name"
                  type="text"
                  class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-2">
                  Email Address
                </label>

                <input
                  v-model="editForm.email"
                  type="email"
                  class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-2">
                  School
                </label>

                <input
                  v-model="editForm.school"
                  type="text"
                  class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-2">
                  Parent Name
                </label>

                <input
                  v-model="editForm.parentName"
                  type="text"
                  class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
              </div>
            </div>

            <!-- Footer -->
            <div
              class="flex justify-end gap-3 px-6 py-5 border-t border-slate-200 dark:border-slate-700"
            >
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
            <!-- Change Password Modal -->
      <transition name="fade">
        <div
          v-if="passwordModalOpen"
          class="fixed inset-0 z-[90] flex items-center justify-center px-4"
        >
          <!-- Backdrop -->
          <div
            class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
            @click="passwordModalOpen = false"
          />

          <!-- Modal -->
          <div
            class="relative w-full max-w-lg rounded-3xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 shadow-2xl"
          >
            <!-- Header -->
            <div
              class="flex items-center justify-between px-6 py-5 border-b border-slate-200 dark:border-slate-700"
            >
              <h2 class="text-xl font-display font-bold">
                Change Password
              </h2>

              <button
                @click="passwordModalOpen = false"
                class="rounded-lg p-2 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              >
                <XMarkIcon class="w-5 h-5" />
              </button>
            </div>

            <!-- Form -->
            <div class="p-6 space-y-5">
              <div>
                <label class="block text-sm font-medium mb-2">
                  Current Password
                </label>

                <input
                  v-model="passwordForm.currentPassword"
                  type="password"
                  placeholder="Enter current password"
                  class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-2">
                  New Password
                </label>

                <input
                  v-model="passwordForm.newPassword"
                  type="password"
                  placeholder="Enter new password"
                  class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-2">
                  Confirm Password
                </label>

                <input
                  v-model="passwordForm.confirmPassword"
                  type="password"
                  placeholder="Confirm new password"
                  class="w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-blue"
                />
              </div>
            </div>

            <!-- Footer -->
            <div
              class="flex justify-end gap-3 px-6 py-5 border-t border-slate-200 dark:border-slate-700"
            >
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