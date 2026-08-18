<script setup>
import { ref, reactive, computed, onMounted } from "vue"
import {
  PencilSquareIcon,
  KeyIcon,
  UserCircleIcon,
  EnvelopeIcon,
  ShieldCheckIcon,
  ClockIcon,
  CalendarDaysIcon,
  CheckCircleIcon,
  XMarkIcon,
} from "@heroicons/vue/24/outline"

import { adminApi } from "../../services/adminApi"
import { useToast } from "../../composables/useToast"
import EmptyState from "../../components/ui/EmptyState.vue"

const { showToast } = useToast()

const loading = ref(true)
const loadError = ref(null)

const adminProfile = reactive({
  name: "",
  email: "",
  role: "",
  username: "",
  memberSince: "",
  lastLoggedIn: "",
})

function formatDateTime(iso) {
  if (!iso) return "—"

  return new Date(iso).toLocaleString("en-US", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

function formatDate(iso) {
  if (!iso) return "—"

  return new Date(iso).toLocaleDateString("en-US", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  })
}

async function loadProfile() {
  loading.value = true
  loadError.value = null

  try {
    const { data } = await adminApi.getProfile()

    adminProfile.name = data.admin_name
    adminProfile.email = data.email || ""
    adminProfile.role = data.role || "Admin"
    adminProfile.username = data.username || ""
    adminProfile.memberSince = formatDate(data.registered_at)
    adminProfile.lastLoggedIn = formatDateTime(data.last_login_at)
  } catch (e) {
    loadError.value = e.message || "Failed to load your profile."
  } finally {
    loading.value = false
  }
}

onMounted(loadProfile)

const editing = ref(false)
const savingProfile = ref(false)

const draft = reactive({
  name: "",
  email: "",
})

const draftErrors = reactive({
  name: "",
  email: "",
})

function validateDraft() {
  draftErrors.name = draft.name.trim()
    ? ""
    : "Name cannot be empty."

  draftErrors.email =
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(draft.email.trim())
      ? ""
      : "Enter a valid email address."

  return !draftErrors.name && !draftErrors.email
}

const draftIsDirty = computed(
  () =>
    draft.name.trim() !== adminProfile.name ||
    draft.email.trim() !== adminProfile.email
)

function startEdit() {
  draft.name = adminProfile.name
  draft.email = adminProfile.email
  draftErrors.name = ""
  draftErrors.email = ""
  editing.value = true
}

function cancelEdit() {
  editing.value = false
  draftErrors.name = ""
  draftErrors.email = ""
}

async function saveEdit() {
  if (!validateDraft()) return

  if (!draftIsDirty.value) {
    editing.value = false
    return
  }

  savingProfile.value = true

  try {
    const { data } = await adminApi.updateProfile({
      admin_name: draft.name.trim(),
      email: draft.email.trim(),
    })

    adminProfile.name = data.admin_name
    adminProfile.email = data.email || ""

    editing.value = false

    showToast("Profile updated successfully.", "success")
  } catch (e) {
    showToast(e.message || "Failed to update profile.", "error")
  } finally {
    savingProfile.value = false
  }
}

const passwordModalOpen = ref(false)
const savingPassword = ref(false)

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

function closePasswordModal() {
  if (savingPassword.value) return

  passwordModalOpen.value = false
  pwError.value = ""
}

async function savePassword() {
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

  savingPassword.value = true
  pwError.value = ""

  try {
    await adminApi.changePassword({
      current_password: pw.current,
      new_password: pw.next,
      confirm_password: pw.confirm,
    })

    passwordModalOpen.value = false

    showToast("Password changed successfully.", "success")
  } catch (e) {
    pwError.value = e.message || "Failed to change password."
  } finally {
    savingPassword.value = false
  }
}
</script>

<template>
  <div class="min-h-full">

    <!-- ========================= -->
    <!-- PAGE HEADING -->
    <!-- ========================= -->

    <div class="mb-7">
      <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">

        <div>
          <div class="flex items-center gap-2 mb-2">
            <span
              class="
                inline-flex items-center justify-center
                w-8 h-8 rounded-lg
                bg-blue-50 dark:bg-blue-500/10
                text-blue-600 dark:text-blue-400
              "
            >
              <UserCircleIcon class="w-5 h-5" />
            </span>

            <span
              class="
                text-xs font-bold uppercase tracking-wider
                text-blue-600 dark:text-blue-400
              "
            >
              Account
            </span>
          </div>

          <h2
            class="
              text-2xl sm:text-3xl
              font-display font-bold
              text-slate-900 dark:text-white
            "
          >
            Admin Profile
          </h2>

          <p
            class="
              mt-1
              text-sm
              text-slate-500 dark:text-slate-400
            "
          >
            Manage your personal details and account security.
          </p>
        </div>

        <div
          v-if="!loading && !loadError"
          class="
            inline-flex items-center gap-2
            self-start sm:self-auto
            px-3 py-2
            rounded-xl
            border
            border-emerald-200 dark:border-emerald-800
            bg-emerald-50 dark:bg-emerald-500/10
            text-xs font-semibold
            text-emerald-700 dark:text-emerald-400
          "
        >
          <span
            class="
              w-2 h-2 rounded-full
              bg-emerald-500
              shadow-[0_0_7px_rgba(16,185,129,0.6)]
            "
          ></span>

          Account Active
        </div>

      </div>
    </div>

    <!-- ========================= -->
    <!-- ERROR -->
    <!-- ========================= -->

    <div
      v-if="loadError"
      class="mx-auto max-w-4xl"
    >
      <EmptyState
        title="Couldn't load your profile"
        :message="loadError"
      />
    </div>

    <!-- ========================= -->
    <!-- LOADING -->
    <!-- ========================= -->

    <div
      v-else-if="loading"
      class="
        mx-auto max-w-4xl
        rounded-3xl
        border
        border-slate-200 dark:border-slate-800
        bg-white dark:bg-[#10182b]
        overflow-hidden
        shadow-sm
        animate-pulse
      "
    >
      <div class="h-32 bg-slate-200 dark:bg-slate-800"></div>

      <div class="px-6 pb-8">

        <div
          class="
            -mt-12
            mx-auto
            w-24 h-24
            rounded-full
            bg-slate-300 dark:bg-slate-700
          "
        ></div>

        <div
          class="
            mx-auto mt-5
            h-5 w-40
            rounded
            bg-slate-200 dark:bg-slate-700
          "
        ></div>

        <div class="mt-8 grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="n in 5"
            :key="n"
            class="h-24 rounded-2xl bg-slate-100 dark:bg-slate-800"
          ></div>
        </div>

      </div>
    </div>

    <!-- ========================= -->
    <!-- PROFILE -->
    <!-- ========================= -->

    <div
      v-else
      class="
        mx-auto
        max-w-4xl
        overflow-hidden
        rounded-3xl
        border
        border-slate-200
        dark:border-slate-800
        bg-white
        dark:bg-[#10182b]
        shadow-sm
      "
    >

      <!-- ========================= -->
      <!-- PROFILE HERO -->
      <!-- ========================= -->

      <div
        class="
          relative
          h-32
          sm:h-36
          overflow-hidden
          bg-gradient-to-br
          from-blue-600
          via-sky-500
          to-cyan-500
          dark:from-blue-900
          dark:via-sky-900
          dark:to-cyan-900
        "
      >

        <!-- Decorative circles -->
        <div
          class="
            absolute
            -right-10
            -top-20
            w-56
            h-56
            rounded-full
            bg-white/10
            blur-sm
          "
        ></div>

        <div
          class="
            absolute
            right-24
            -bottom-20
            w-40
            h-40
            rounded-full
            bg-white/10
          "
        ></div>

        <div
          class="
            absolute
            left-10
            -top-14
            w-32
            h-32
            rounded-full
            bg-cyan-300/10
          "
        ></div>

        <!-- Header label -->
        <div class="absolute top-5 left-6">
          <span
            class="
              inline-flex
              items-center gap-2
              px-3 py-1.5
              rounded-full
              bg-white/15
              border border-white/20
              text-[10px]
              font-bold
              uppercase
              tracking-wider
              text-white
              backdrop-blur-sm
            "
          >
            <ShieldCheckIcon class="w-3.5 h-3.5" />
            Administrator
          </span>
        </div>

      </div>

      <div class="px-5 sm:px-8 pb-8">

        <!-- ========================= -->
        <!-- AVATAR + NAME -->
        <!-- ========================= -->

        <div
          class="
            relative
            -mt-14
            flex
            flex-col
            items-center
            text-center
          "
        >

          <div
            class="
              flex
              h-28
              w-28
              items-center
              justify-center
              rounded-full
              bg-gradient-to-br
              from-blue-500
              via-sky-500
              to-cyan-400
              text-4xl
              font-bold
              text-white
              shadow-xl
              ring-4
              ring-white
              dark:ring-[#10182b]
            "
          >
            {{ adminProfile.name.charAt(0).toUpperCase() }}
          </div>

          <h3
            class="
              mt-4
              text-2xl
              font-display
              font-bold
              text-slate-900
              dark:text-white
            "
          >
            {{ adminProfile.name }}
          </h3>

          <p
            class="
              mt-1
              text-sm
              text-slate-500
              dark:text-slate-400
            "
          >
            @{{ adminProfile.username || "admin" }}
          </p>

          <div
            class="
              mt-3
              inline-flex
              items-center
              gap-1.5
              px-3
              py-1.5
              rounded-full
              bg-blue-50
              dark:bg-blue-500/10
              text-xs
              font-semibold
              text-blue-700
              dark:text-blue-400
            "
          >
            <ShieldCheckIcon class="w-4 h-4" />
            {{ adminProfile.role }}
          </div>

        </div>

        <template v-if="!editing">

          <!-- ========================= -->
          <!-- ACCOUNT INFORMATION -->
          <!-- ========================= -->

          <div class="mt-8">

            <div
              class="
                flex
                items-center
                justify-between
                mb-4
              "
            >
              <div>
                <h4
                  class="
                    text-sm
                    font-bold
                    text-slate-800
                    dark:text-slate-100
                  "
                >
                  Account Information
                </h4>

                <p
                  class="
                    text-xs
                    text-slate-400
                    dark:text-slate-500
                    mt-0.5
                  "
                >
                  Your registered account details
                </p>
              </div>
            </div>

            <div
              class="
                grid
                grid-cols-1
                sm:grid-cols-2
                lg:grid-cols-3
                gap-4
              "
            >

              <!-- Email -->
              <div
                class="
                  group
                  rounded-2xl
                  border
                  border-slate-200
                  dark:border-slate-700
                  bg-slate-50
                  dark:bg-[#0c1425]
                  p-4
                  transition-all
                  hover:border-blue-200
                  dark:hover:border-blue-800
                  hover:shadow-sm
                "
              >
                <div class="flex items-start gap-3">

                  <div
                    class="
                      w-9 h-9
                      rounded-xl
                      flex items-center justify-center
                      bg-blue-50
                      dark:bg-blue-500/10
                      text-blue-600
                      dark:text-blue-400
                      shrink-0
                    "
                  >
                    <EnvelopeIcon class="w-5 h-5" />
                  </div>

                  <div class="min-w-0">
                    <p
                      class="
                        text-[10px]
                        font-bold
                        uppercase
                        tracking-wider
                        text-slate-400
                        dark:text-slate-500
                      "
                    >
                      Email
                    </p>

                    <p
                      class="
                        mt-1
                        break-all
                        text-sm
                        font-semibold
                        text-slate-700
                        dark:text-slate-200
                      "
                    >
                      {{ adminProfile.email || "—" }}
                    </p>
                  </div>

                </div>
              </div>

              <!-- Role -->
              <div
                class="
                  group
                  rounded-2xl
                  border
                  border-slate-200
                  dark:border-slate-700
                  bg-slate-50
                  dark:bg-[#0c1425]
                  p-4
                  transition-all
                  hover:border-emerald-200
                  dark:hover:border-emerald-800
                  hover:shadow-sm
                "
              >
                <div class="flex items-start gap-3">

                  <div
                    class="
                      w-9 h-9
                      rounded-xl
                      flex items-center justify-center
                      bg-emerald-50
                      dark:bg-emerald-500/10
                      text-emerald-600
                      dark:text-emerald-400
                      shrink-0
                    "
                  >
                    <ShieldCheckIcon class="w-5 h-5" />
                  </div>

                  <div>
                    <p
                      class="
                        text-[10px]
                        font-bold
                        uppercase
                        tracking-wider
                        text-slate-400
                        dark:text-slate-500
                      "
                    >
                      Role
                    </p>

                    <p
                      class="
                        mt-1
                        text-sm
                        font-semibold
                        text-slate-700
                        dark:text-slate-200
                      "
                    >
                      {{ adminProfile.role }}
                    </p>
                  </div>

                </div>
              </div>

              <!-- Username -->
              <div
                class="
                  group
                  rounded-2xl
                  border
                  border-slate-200
                  dark:border-slate-700
                  bg-slate-50
                  dark:bg-[#0c1425]
                  p-4
                  transition-all
                  hover:border-violet-200
                  dark:hover:border-violet-800
                  hover:shadow-sm
                "
              >
                <div class="flex items-start gap-3">

                  <div
                    class="
                      w-9 h-9
                      rounded-xl
                      flex items-center justify-center
                      bg-violet-50
                      dark:bg-violet-500/10
                      text-violet-600
                      dark:text-violet-400
                      shrink-0
                    "
                  >
                    <UserCircleIcon class="w-5 h-5" />
                  </div>

                  <div class="min-w-0">
                    <p
                      class="
                        text-[10px]
                        font-bold
                        uppercase
                        tracking-wider
                        text-slate-400
                        dark:text-slate-500
                      "
                    >
                      Username
                    </p>

                    <p
                      class="
                        mt-1
                        break-all
                        text-sm
                        font-semibold
                        text-slate-700
                        dark:text-slate-200
                      "
                    >
                      {{ adminProfile.username || "—" }}
                    </p>
                  </div>

                </div>
              </div>

              <!-- Last Login -->
              <div
                class="
                  group
                  rounded-2xl
                  border
                  border-slate-200
                  dark:border-slate-700
                  bg-slate-50
                  dark:bg-[#0c1425]
                  p-4
                  transition-all
                  hover:border-amber-200
                  dark:hover:border-amber-800
                  hover:shadow-sm
                "
              >
                <div class="flex items-start gap-3">

                  <div
                    class="
                      w-9 h-9
                      rounded-xl
                      flex items-center justify-center
                      bg-amber-50
                      dark:bg-amber-500/10
                      text-amber-600
                      dark:text-amber-400
                      shrink-0
                    "
                  >
                    <ClockIcon class="w-5 h-5" />
                  </div>

                  <div>
                    <p
                      class="
                        text-[10px]
                        font-bold
                        uppercase
                        tracking-wider
                        text-slate-400
                        dark:text-slate-500
                      "
                    >
                      Last Login
                    </p>

                    <p
                      class="
                        mt-1
                        text-sm
                        font-semibold
                        text-slate-700
                        dark:text-slate-200
                      "
                    >
                      {{ adminProfile.lastLoggedIn }}
                    </p>
                  </div>

                </div>
              </div>

              <!-- Member Since -->
              <div
                class="
                  group
                  rounded-2xl
                  border
                  border-slate-200
                  dark:border-slate-700
                  bg-slate-50
                  dark:bg-[#0c1425]
                  p-4
                  transition-all
                  hover:border-cyan-200
                  dark:hover:border-cyan-800
                  hover:shadow-sm
                "
              >
                <div class="flex items-start gap-3">

                  <div
                    class="
                      w-9 h-9
                      rounded-xl
                      flex items-center justify-center
                      bg-cyan-50
                      dark:bg-cyan-500/10
                      text-cyan-600
                      dark:text-cyan-400
                      shrink-0
                    "
                  >
                    <CalendarDaysIcon class="w-5 h-5" />
                  </div>

                  <div>
                    <p
                      class="
                        text-[10px]
                        font-bold
                        uppercase
                        tracking-wider
                        text-slate-400
                        dark:text-slate-500
                      "
                    >
                      Member Since
                    </p>

                    <p
                      class="
                        mt-1
                        text-sm
                        font-semibold
                        text-slate-700
                        dark:text-slate-200
                      "
                    >
                      {{ adminProfile.memberSince }}
                    </p>
                  </div>

                </div>
              </div>

              <!-- Account Status -->
              <div
                class="
                  group
                  rounded-2xl
                  border
                  border-slate-200
                  dark:border-slate-700
                  bg-slate-50
                  dark:bg-[#0c1425]
                  p-4
                  transition-all
                  hover:border-emerald-200
                  dark:hover:border-emerald-800
                  hover:shadow-sm
                "
              >
                <div class="flex items-start gap-3">

                  <div
                    class="
                      w-9 h-9
                      rounded-xl
                      flex items-center justify-center
                      bg-emerald-50
                      dark:bg-emerald-500/10
                      text-emerald-600
                      dark:text-emerald-400
                      shrink-0
                    "
                  >
                    <CheckCircleIcon class="w-5 h-5" />
                  </div>

                  <div>
                    <p
                      class="
                        text-[10px]
                        font-bold
                        uppercase
                        tracking-wider
                        text-slate-400
                        dark:text-slate-500
                      "
                    >
                      Status
                    </p>

                    <p
                      class="
                        mt-1
                        text-sm
                        font-semibold
                        text-emerald-600
                        dark:text-emerald-400
                      "
                    >
                      Active
                    </p>
                  </div>

                </div>
              </div>

            </div>
          </div>

          <!-- ========================= -->
          <!-- ACTIONS -->
          <!-- ========================= -->

          <div
            class="
              mt-7
              pt-6
              border-t
              border-slate-100
              dark:border-slate-800
            "
          >

            <div
              class="
                flex
                flex-col
                sm:flex-row
                items-stretch
                sm:items-center
                justify-center
                gap-3
              "
            >

              <button
                class="
                  inline-flex
                  items-center
                  justify-center
                  gap-2
                  rounded-xl
                  bg-gradient-to-r
                  from-blue-600
                  to-sky-500
                  px-5
                  py-2.5
                  text-sm
                  font-semibold
                  text-white
                  shadow-sm
                  shadow-blue-500/20
                  transition-all
                  duration-200
                  hover:from-blue-700
                  hover:to-sky-600
                  hover:shadow-md
                  active:scale-[0.98]
                "
                @click="startEdit"
              >
                <PencilSquareIcon class="h-4 w-4" />
                Edit Profile
              </button>

              <button
                class="
                  inline-flex
                  items-center
                  justify-center
                  gap-2
                  rounded-xl
                  border
                  border-violet-200
                  dark:border-violet-800
                  bg-violet-50
                  dark:bg-violet-500/10
                  px-5
                  py-2.5
                  text-sm
                  font-semibold
                  text-violet-700
                  dark:text-violet-400
                  transition-all
                  duration-200
                  hover:bg-violet-100
                  dark:hover:bg-violet-500/15
                  hover:shadow-sm
                  active:scale-[0.98]
                "
                @click="openPasswordModal"
              >
                <KeyIcon class="h-4 w-4" />
                Change Password
              </button>

            </div>
          </div>

        </template>

        <!-- ========================= -->
        <!-- EDIT PROFILE -->
        <!-- ========================= -->

        <template v-else>

          <div
            class="
              mx-auto
              mt-8
              max-w-xl
              rounded-2xl
              border
              border-blue-100
              dark:border-blue-900/50
              bg-slate-50
              dark:bg-[#0c1425]
              p-5
              sm:p-6
            "
          >

            <div class="mb-6 text-center">

              <div
                class="
                  mx-auto
                  w-10 h-10
                  rounded-xl
                  bg-blue-50
                  dark:bg-blue-500/10
                  text-blue-600
                  dark:text-blue-400
                  flex
                  items-center
                  justify-center
                  mb-3
                "
              >
                <PencilSquareIcon class="w-5 h-5" />
              </div>

              <h3
                class="
                  text-lg
                  font-display
                  font-bold
                  text-slate-900
                  dark:text-white
                "
              >
                Edit Profile
              </h3>

              <p
                class="
                  text-xs
                  text-slate-400
                  dark:text-slate-500
                  mt-1
                "
              >
                Update your name and email address.
              </p>

            </div>

            <div class="space-y-5">

              <!-- Name -->
              <div>
                <label
                  class="
                    mb-1.5
                    block
                    text-xs
                    font-bold
                    text-slate-600
                    dark:text-slate-300
                  "
                >
                  Name
                </label>

                <input
                  v-model="draft.name"
                  type="text"
                  class="input-field"
                  :class="draftErrors.name && 'ring-1 ring-rose-400'"
                  placeholder="Enter your name"
                  @blur="validateDraft"
                />

                <p
                  v-if="draftErrors.name"
                  class="mt-1.5 text-xs text-rose-500"
                >
                  {{ draftErrors.name }}
                </p>
              </div>

              <!-- Email -->
              <div>
                <label
                  class="
                    mb-1.5
                    block
                    text-xs
                    font-bold
                    text-slate-600
                    dark:text-slate-300
                  "
                >
                  Email Address
                </label>

                <input
                  v-model="draft.email"
                  type="email"
                  class="input-field"
                  :class="draftErrors.email && 'ring-1 ring-rose-400'"
                  placeholder="Enter your email"
                  @blur="validateDraft"
                />

                <p
                  v-if="draftErrors.email"
                  class="mt-1.5 text-xs text-rose-500"
                >
                  {{ draftErrors.email }}
                </p>
              </div>

            </div>

            <!-- Edit Actions -->
            <div
              class="
                mt-7
                flex
                flex-col-reverse
                sm:flex-row
                justify-center
                gap-3
              "
            >

              <button
                class="btn-secondary"
                @click="cancelEdit"
              >
                Cancel
              </button>

              <button
                class="
                  inline-flex
                  items-center
                  justify-center
                  gap-2
                  rounded-xl
                  bg-blue-600
                  px-5
                  py-2.5
                  text-sm
                  font-semibold
                  text-white
                  shadow-sm
                  transition
                  hover:bg-blue-700
                  disabled:cursor-not-allowed
                  disabled:opacity-50
                "
                :disabled="
                  savingProfile ||
                  !!draftErrors.name ||
                  !!draftErrors.email ||
                  !draftIsDirty
                "
                @click="saveEdit"
              >
                <CheckCircleIcon
                  v-if="!savingProfile"
                  class="w-4 h-4"
                />

                {{ savingProfile ? "Saving..." : "Save Changes" }}
              </button>

            </div>

            <p
              v-if="!draftIsDirty && !draftErrors.name && !draftErrors.email"
              class="
                mt-3
                text-center
                text-[11px]
                text-slate-400
                dark:text-slate-500
              "
            >
              No changes have been made.
            </p>

          </div>

        </template>

      </div>
    </div>

    <!-- ========================= -->
    <!-- PASSWORD MODAL -->
    <!-- ========================= -->

    <transition name="fade">

      <div
        v-if="passwordModalOpen"
        class="
          fixed
          inset-0
          z-[90]
          flex
          items-center
          justify-center
          px-4
          py-6
        "
      >

        <!-- Backdrop -->
        <div
          class="
            absolute
            inset-0
            bg-slate-950/60
            dark:bg-black/70
            backdrop-blur-sm
          "
          @click="closePasswordModal"
        ></div>

        <!-- Modal -->
        <div
          class="
            relative
            z-10
            w-full
            max-w-md
            max-h-[90vh]
            overflow-y-auto
            rounded-3xl
            border
            border-slate-200
            dark:border-slate-700
            bg-white
            dark:bg-[#10182b]
            shadow-2xl
          "
        >

          <!-- Modal Header -->
          <div
            class="
              px-6
              py-5
              border-b
              border-slate-100
              dark:border-slate-800
            "
          >

            <div class="flex items-start gap-3">

              <div
                class="
                  w-10 h-10
                  rounded-xl
                  bg-violet-50
                  dark:bg-violet-500/10
                  text-violet-600
                  dark:text-violet-400
                  flex
                  items-center
                  justify-center
                  shrink-0
                "
              >
                <KeyIcon class="w-5 h-5" />
              </div>

              <div class="flex-1">

                <h3
                  class="
                    text-base
                    font-bold
                    text-slate-900
                    dark:text-white
                  "
                >
                  Change Password
                </h3>

                <p
                  class="
                    mt-0.5
                    text-xs
                    text-slate-400
                    dark:text-slate-500
                  "
                >
                  Keep your administrator account secure.
                </p>

              </div>

              <button
                type="button"
                class="
                  w-8 h-8
                  rounded-lg
                  flex items-center justify-center
                  text-slate-400
                  hover:text-slate-700
                  dark:hover:text-white
                  hover:bg-slate-100
                  dark:hover:bg-slate-800
                  transition
                "
                :disabled="savingPassword"
                @click="closePasswordModal"
              >
                <XMarkIcon class="w-5 h-5" />
              </button>

            </div>

          </div>

          <!-- Modal Form -->
          <div class="px-6 py-5">

            <div class="space-y-4">

              <!-- Current -->
              <div>
                <label
                  class="
                    mb-1.5
                    block
                    text-xs
                    font-bold
                    text-slate-600
                    dark:text-slate-300
                  "
                >
                  Current Password
                </label>

                <input
                  v-model="pw.current"
                  type="password"
                  class="input-field"
                  placeholder="Enter current password"
                />
              </div>

              <!-- New -->
              <div>
                <label
                  class="
                    mb-1.5
                    block
                    text-xs
                    font-bold
                    text-slate-600
                    dark:text-slate-300
                  "
                >
                  New Password
                </label>

                <input
                  v-model="pw.next"
                  type="password"
                  class="input-field"
                  placeholder="Enter new password"
                />

                <p
                  class="
                    mt-1.5
                    text-[11px]
                    text-slate-400
                    dark:text-slate-500
                  "
                >
                  Minimum 6 characters.
                </p>
              </div>

              <!-- Confirm -->
              <div>
                <label
                  class="
                    mb-1.5
                    block
                    text-xs
                    font-bold
                    text-slate-600
                    dark:text-slate-300
                  "
                >
                  Confirm Password
                </label>

                <input
                  v-model="pw.confirm"
                  type="password"
                  class="input-field"
                  placeholder="Confirm new password"
                />
              </div>

              <!-- Error -->
              <div
                v-if="pwError"
                class="
                  flex
                  items-start
                  gap-2
                  rounded-xl
                  border
                  border-rose-200
                  dark:border-rose-900/50
                  bg-rose-50
                  dark:bg-rose-500/10
                  px-3
                  py-2.5
                  text-xs
                  text-rose-600
                  dark:text-rose-400
                "
              >
                <span
                  class="
                    w-4 h-4
                    rounded-full
                    bg-rose-500
                    text-white
                    flex
                    items-center
                    justify-center
                    text-[9px]
                    font-bold
                    shrink-0
                  "
                >
                  !
                </span>

                <span>{{ pwError }}</span>
              </div>

            </div>

            <!-- Modal Buttons -->
            <div
              class="
                mt-6
                flex
                flex-col-reverse
                sm:flex-row
                justify-end
                gap-2
              "
            >

              <button
                class="btn-secondary"
                :disabled="savingPassword"
                @click="closePasswordModal"
              >
                Cancel
              </button>

              <button
                class="
                  inline-flex
                  items-center
                  justify-center
                  gap-2
                  rounded-xl
                  bg-violet-600
                  px-5
                  py-2.5
                  text-sm
                  font-semibold
                  text-white
                  shadow-sm
                  transition
                  hover:bg-violet-700
                  disabled:cursor-not-allowed
                  disabled:opacity-50
                "
                :disabled="savingPassword"
                @click="savePassword"
              >
                <KeyIcon
                  v-if="!savingPassword"
                  class="w-4 h-4"
                />

                {{ savingPassword ? "Saving..." : "Update Password" }}
              </button>

            </div>

          </div>

        </div>
      </div>

    </transition>

  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-from > div:last-child {
  transform: translateY(10px) scale(0.98);
}

.fade-leave-to > div:last-child {
  transform: translateY(10px) scale(0.98);
}
</style>