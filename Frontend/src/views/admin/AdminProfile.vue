<script setup>
import { ref, reactive } from "vue"
import {
  PencilSquareIcon,
  KeyIcon,
} from "@heroicons/vue/24/outline"

import { adminProfile } from "../../data/mockData"
import { useToast } from "../../composables/useToast"

const { showToast } = useToast()

const editing = ref(false)

const draft = reactive({
  ...adminProfile,
})

function startEdit() {
  draft.name = adminProfile.name
  draft.email = adminProfile.email
  editing.value = true
}

function saveEdit() {
  adminProfile.name = draft.name
  adminProfile.email = draft.email

  editing.value = false
  showToast("Profile updated successfully.", "success")
}

const passwordModalOpen = ref(false)

const pw = reactive({
  current: "",
  next: "",
  confirm: "",
})

const pwError = ref("")

function openPasswordModal() {
  pw.current = ""
  pw.next = ""
  pw.confirm = ""
  pwError.value = ""
  passwordModalOpen.value = true
}

function savePassword() {
  if (!pw.current || !pw.next || !pw.confirm) {
    pwError.value = "Please fill in all fields."
    return
  }

  if (pw.next.length < 6) {
    pwError.value = "New password must be at least 6 characters."
    return
  }

  if (pw.next !== pw.confirm) {
    pwError.value = "New password and confirmation do not match."
    return
  }

  passwordModalOpen.value = false
  showToast("Password changed successfully.", "success")
}
</script>

<template>
  <div>
    <!-- Page Heading -->
    <div class="mb-6 text-center">
      <h2
        class="text-2xl font-display font-bold text-slate-800 dark:text-slate-100"
      >
        Admin Profile
      </h2>

      <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
        Your account details and security settings.
      </p>
    </div>

    <!-- Profile Card -->
    <div class="card mx-auto max-w-3xl overflow-hidden rounded-2xl">
      <!-- Header -->
      <div
        class="h-36 bg-gradient-to-r
        from-sky-100
        via-blue-50
        to-cyan-100
        dark:from-sky-800/30
        dark:via-blue-800/20
        dark:to-cyan-800/30"
      ></div>

      <div class="px-8 pb-8">
        <!-- Avatar -->
        <div class="-mt-16 flex flex-col items-center">
          <div
            class="flex h-28 w-28 items-center justify-center rounded-full
            bg-gradient-to-br
            from-sky-300
            via-sky-400
            to-cyan-400
            text-4xl font-bold text-white
            shadow-lg ring-4 ring-white
            dark:ring-slate-900"
          >
            {{ adminProfile.name.charAt(0).toUpperCase() }}
          </div>

          <!-- Name -->
          <h3
            class="mt-5 text-2xl font-display font-bold text-slate-800 dark:text-slate-100"
          >
            {{ adminProfile.name }}
          </h3>
        </div>

        <template v-if="!editing">
          <!-- Info Cards -->
          <div class="mt-8 grid grid-cols-1 gap-5 md:grid-cols-3">
            <!-- Email -->
            <div
              class="rounded-2xl border border-sky-100 bg-sky-50 p-5 dark:border-sky-800 dark:bg-sky-900/20"
            >
              <p
                class="text-xs font-semibold uppercase tracking-wider text-slate-500"
              >
                Email ID
              </p>

              <p
                class="mt-2 break-all text-sm font-medium text-slate-700 dark:text-slate-200"
              >
                {{ adminProfile.email }}
              </p>
            </div>

            <!-- Role -->
            <div
              class="rounded-2xl border border-emerald-100 bg-emerald-50 p-5 dark:border-emerald-800 dark:bg-emerald-900/20"
            >
              <p
                class="text-xs font-semibold uppercase tracking-wider text-slate-500"
              >
                Role
              </p>

              <p class="mt-2 text-sm font-semibold text-slate-700 dark:text-slate-200">
                {{ adminProfile.role }}
              </p>
            </div>

            <!-- Last Login -->
            <div
              class="rounded-2xl border border-violet-100 bg-violet-50 p-5 dark:border-violet-800 dark:bg-violet-900/20"
            >
              <p
                class="text-xs font-semibold uppercase tracking-wider text-slate-500"
              >
                Last Logged In
              </p>

              <p class="mt-2 text-sm font-semibold text-slate-700 dark:text-slate-200">
                {{ adminProfile.lastLoggedIn }}
              </p>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="mt-8 flex justify-center gap-4">
            <button
              class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r
              from-amber-100 via-yellow-100 to-orange-100
              px-5 py-2.5 font-medium text-amber-900 shadow-md transition-all duration-300
              hover:from-amber-200 hover:via-yellow-200 hover:to-orange-200 hover:shadow-lg"
              @click="startEdit"
            >
              <PencilSquareIcon class="h-4 w-4" />
              Edit Profile
            </button>

            <button
              class="inline-flex items-center gap-2 rounded-xl
              bg-gradient-to-r
              from-violet-100 via-fuchsia-100 to-purple-100
              px-5 py-2.5 font-medium text-violet-900 shadow-md transition-all duration-300
              hover:from-violet-200 hover:via-fuchsia-200 hover:to-purple-200 hover:shadow-lg"
              @click="openPasswordModal"
            >
              <KeyIcon class="h-4 w-4" />
              Change Password
            </button>
          </div>
        </template>

                  <template v-else>
          <!-- Edit Profile Card -->
          <div
            class="mx-auto mt-8 max-w-xl rounded-2xl
            border border-orange-100
            bg-gradient-to-br
            from-orange-50
            via-amber-50
            to-orange-100
            p-6
            dark:border-orange-800
            dark:from-orange-900/20
            dark:via-amber-900/10
            dark:to-orange-900/20"
          >
            <h3
              class="mb-6 text-center text-xl font-display font-semibold
              text-slate-800 dark:text-slate-100"
            >
              Edit Profile
            </h3>

            <div class="space-y-5">
              <!-- Name -->
              <div>
                <label
                  class="mb-1 block text-xs font-semibold
                  text-slate-500 dark:text-slate-400"
                >
                  Name
                </label>

                <input
                  v-model="draft.name"
                  type="text"
                  class="input-field"
                  placeholder="Enter your name"
                />
              </div>

              <!-- Email -->
              <div>
                <label
                  class="mb-1 block text-xs font-semibold
                  text-slate-500 dark:text-slate-400"
                >
                  Email ID
                </label>

                <input
                  v-model="draft.email"
                  type="email"
                  class="input-field"
                  placeholder="Enter your email"
                />
              </div>
            </div>

            <!-- Buttons -->
            <div class="mt-8 flex justify-center gap-3">
              <button
                class="inline-flex items-center justify-center
                rounded-xl
                bg-gradient-to-r
                from-amber-100
                via-yellow-100
                to-orange-100
                px-5 py-2.5
                font-medium
                text-amber-900
                shadow-md
                transition-all
                duration-300
                hover:from-amber-200
                hover:via-yellow-200
                hover:to-orange-200
                hover:shadow-lg"
                @click="saveEdit"
              >
                Save Changes
              </button>

              <button
                class="btn-secondary"
                @click="editing = false"
              >
                Cancel
              </button>
            </div>
          </div>
        </template>
      </div>
    </div>

    <!-- Password Modal -->
     <transition name="fade">
  <div
    v-if="passwordModalOpen"
    class="fixed inset-0 z-[90] flex items-center justify-center px-4"
  >
    <!-- Backdrop -->
    <div
      class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm"
      @click="passwordModalOpen = false"
    ></div>

    <!-- Modal -->
    <div
      class="relative z-10 w-full max-w-md rounded-2xl bg-white dark:bg-slate-900 p-6 shadow-soft-lg"
    >
      <!-- Heading -->
      <div class="mb-6">
        <h3
          class="text-center text-lg font-display font-semibold text-slate-800 dark:text-slate-100"
        >
          Change Password
        </h3>
      </div>

      <!-- Form -->
      <div class="space-y-4">
        <div>
          <label
            class="mb-1 block text-xs font-semibold text-slate-500 dark:text-slate-400"
          >
            Current Password
          </label>

          <input
            v-model="pw.current"
            type="password"
            class="input-field"
            placeholder="••••••••"
          />
        </div>

        <div>
          <label
            class="mb-1 block text-xs font-semibold text-slate-500 dark:text-slate-400"
          >
            New Password
          </label>

          <input
            v-model="pw.next"
            type="password"
            class="input-field"
            placeholder="••••••••"
          />
        </div>

        <div>
          <label
            class="mb-1 block text-xs font-semibold text-slate-500 dark:text-slate-400"
          >
            Confirm Password
          </label>

          <input
            v-model="pw.confirm"
            type="password"
            class="input-field"
            placeholder="••••••••"
          />
        </div>

        <p
          v-if="pwError"
          class="text-sm text-rose-500"
        >
          {{ pwError }}
        </p>
      </div>

      <!-- Buttons -->
      <div class="mt-6 flex justify-end gap-3">
        <button
          class="btn-secondary"
          @click="passwordModalOpen = false"
        >
          Cancel
        </button>

        <button
          class="inline-flex items-center justify-center
          rounded-xl
          bg-gradient-to-r
          from-violet-100
          via-fuchsia-100
          to-purple-100
          px-5 py-2.5
          font-medium
          text-violet-900
          shadow-md
          transition-all
          duration-300
          hover:from-violet-200
          hover:via-fuchsia-200
          hover:to-purple-200
          hover:shadow-lg"
          @click="savePassword"
        >
          Save
        </button>
      </div>
    </div>
  </div>
</transition>
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