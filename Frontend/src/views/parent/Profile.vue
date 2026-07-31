<script setup>
import { ref, reactive, computed } from 'vue'
import {
  PencilSquareIcon,
  KeyIcon,
  XMarkIcon,
  AcademicCapIcon
} from '@heroicons/vue/24/outline'

import { parents, students } from '../../data/parentMockData'
import { useToast } from '../../composables/useToast'

const { showToast } = useToast()

// parent_id 1 = the logged-in parent's session (same demo id used across the portal)
const profile = parents[0]
const children = computed(() => students.filter((s) => s.parent_id === profile.parent_id))

const editing = ref(false)
const draft = reactive({ ...profile })

function startEdit() {
  draft.parent_name = profile.parent_name
  draft.email = profile.email
  draft.phone_no = profile.phone_no
  editing.value = true
}

function saveEdit() {
  profile.parent_name = draft.parent_name
  profile.email = draft.email
  profile.phone_no = draft.phone_no

  editing.value = false
  showToast('Profile updated successfully.', 'success')
}

const passwordModalOpen = ref(false)
const pw = reactive({ current: '', next: '', confirm: '' })
const pwError = ref('')

function openPasswordModal() {
  pw.current = ''
  pw.next = ''
  pw.confirm = ''
  pwError.value = ''
  passwordModalOpen.value = true
}

function savePassword() {
  if (!pw.current || !pw.next || !pw.confirm) {
    pwError.value = 'Please fill in all fields.'
    return
  }
  if (pw.next.length < 6) {
    pwError.value = 'New password must be at least 6 characters.'
    return
  }
  if (pw.next !== pw.confirm) {
    pwError.value = 'New password and confirmation do not match.'
    return
  }

  passwordModalOpen.value = false
  showToast('Password changed successfully.', 'success')
}
</script>

<template>
<div>
  <div class="card max-w-3xl mx-auto overflow-hidden rounded-2xl">
    <div class="h-36 bg-gradient-to-r from-emerald-100 via-blue-50 to-purple-100 dark:from-emerald-800/30 dark:via-blue-800/20 dark:to-purple-800/30"></div>

    <div class="px-8 pb-8">
      <!-- Avatar -->
      <div class="-mt-16 flex flex-col items-center">
        <div class="w-28 h-28 rounded-full bg-gradient-to-br from-brand-green-400 via-brand-blue-400 to-brand-purple-400 flex items-center justify-center text-white text-4xl font-bold leading-none shadow-lg ring-4 ring-white dark:ring-slate-900">
          {{ profile.parent_name.charAt(0).toUpperCase() }}
        </div>

        <h3 class="mt-5 text-2xl font-display font-bold text-slate-800 dark:text-slate-100">
          {{ profile.parent_name }}
        </h3>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Parent Account</p>
      </div>

      <template v-if="!editing">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5 mt-8">
          <div class="rounded-2xl bg-sky-50 dark:bg-sky-900/20 border border-sky-100 dark:border-sky-800 p-5">
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-500">Email ID</p>
            <p class="mt-2 text-sm font-medium break-all text-slate-700 dark:text-slate-200">{{ profile.email }}</p>
          </div>

          <div class="rounded-2xl bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-100 dark:border-emerald-800 p-5">
            <p class="text-xs font-semibold uppercase tracking-wider text-slate-500">Phone Number</p>
            <p class="mt-2 text-sm font-semibold text-slate-700 dark:text-slate-200">{{ profile.phone_no }}</p>
          </div>
        </div>

        <!-- Linked children -->
        <div class="mt-6">
          <p class="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
            <AcademicCapIcon class="w-4 h-4" />
            Linked Children
          </p>
          <div class="grid sm:grid-cols-2 gap-3">
            <div
              v-for="child in children"
              :key="child.student_id"
              class="rounded-xl bg-violet-50 dark:bg-violet-900/20 border border-violet-100 dark:border-violet-800 p-4"
            >
              <p class="text-sm font-semibold text-slate-800 dark:text-slate-100">{{ child.student_name }}</p>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">{{ child.school }}</p>
            </div>
          </div>
        </div>

        <!-- Buttons -->
        <div class="flex justify-center gap-4 mt-8">
          <button
            class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-amber-900 font-medium shadow-md transition-all duration-300 bg-gradient-to-r from-amber-100 via-yellow-100 to-orange-100 hover:from-amber-200 hover:via-yellow-200 hover:to-orange-200 hover:shadow-lg"
            @click="startEdit"
          >
            <PencilSquareIcon class="w-4 h-4" />
            Edit Profile
          </button>

          <button class="btn-secondary" @click="openPasswordModal">
            <KeyIcon class="w-4 h-4" />
            Change Password
          </button>
        </div>
      </template>

      <template v-else>
        <div class="max-w-xl mx-auto mt-8 rounded-2xl bg-gradient-to-br from-orange-50 via-amber-50 to-orange-100 dark:from-orange-900/20 dark:via-amber-900/10 dark:to-orange-900/20 border border-orange-100 dark:border-orange-800 p-6">
          <h3 class="text-xl font-display font-semibold text-center text-slate-800 dark:text-slate-100 mb-6">
            Edit Profile
          </h3>

          <div class="space-y-5">
            <div>
              <label class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block">Name</label>
              <input v-model="draft.parent_name" type="text" class="input-field" />
            </div>

            <div>
              <label class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block">Email ID</label>
              <input v-model="draft.email" type="email" class="input-field" />
            </div>

            <div>
              <label class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block">Phone Number</label>
              <input v-model="draft.phone_no" type="tel" class="input-field" />
            </div>
          </div>

          <div class="flex justify-center gap-3 mt-8">
            <button class="btn-primary" @click="saveEdit">Save Changes</button>
            <button class="btn-secondary" @click="editing = false">Cancel</button>
          </div>
        </div>
      </template>
    </div>

    <!-- Password Modal -->
    <transition name="fade">
      <div v-if="passwordModalOpen" class="fixed inset-0 z-[90] flex items-center justify-center px-4">
        <div class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm" @click="passwordModalOpen = false" />

        <div class="relative card w-full max-w-md p-6 shadow-soft-lg rounded-2xl">
          <div class="flex items-center justify-between mb-5">
            <h3 class="text-lg font-display font-semibold text-slate-800 dark:text-slate-100">Change Password</h3>
            <button class="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200" @click="passwordModalOpen = false">
              <XMarkIcon class="w-5 h-5" />
            </button>
          </div>

          <div class="space-y-4">
            <div>
              <label class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block">Current Password</label>
              <input v-model="pw.current" type="password" class="input-field" placeholder="••••••••" />
            </div>
            <div>
              <label class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block">New Password</label>
              <input v-model="pw.next" type="password" class="input-field" placeholder="••••••••" />
            </div>
            <div>
              <label class="text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1 block">Confirm Password</label>
              <input v-model="pw.confirm" type="password" class="input-field" placeholder="••••••••" />
            </div>
            <p v-if="pwError" class="text-xs text-rose-500">{{ pwError }}</p>
          </div>

          <div class="flex justify-end gap-3 mt-6">
            <button class="btn-secondary" @click="passwordModalOpen = false">Cancel</button>
            <button class="btn-primary" @click="savePassword">Save</button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
