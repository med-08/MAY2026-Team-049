<script setup>
import { ref, onMounted } from "vue"
import AuthNavbar from "../components/layout/AuthNavbar.vue"
import { authApi } from "../services/authApi"
import { useRouter } from "vue-router"

const router = useRouter()

const selectedRole = ref("Student")
const subjects = ref([])
const subjectsLoading = ref(true)
const selectedSubjectIds = ref([])
const authError = ref("")
const authSuccess = ref("")
const submitting = ref(false)
const showLogoutPrompt = ref(false)
const loggingOut = ref(false)

function toggleSubject(id) {
  const idx = selectedSubjectIds.value.indexOf(id)
  if (idx === -1) selectedSubjectIds.value.push(id)
  else selectedSubjectIds.value.splice(idx, 1)
}

onMounted(async () => {
  try {
    // Use the shared authApi/apiClient helper (which respects
    // VITE_API_BASE_URL) instead of a hardcoded localhost URL, so the
    // subject picker still works when the frontend is not being served
    // from 127.0.0.1 (e.g. staging/production, or Docker service names).
    const data = await authApi.getSubjects()
    subjects.value = data.data || []
  } catch {
    subjects.value = []
  } finally {
    subjectsLoading.value = false
  }
})

// "Parent" is no longer its own registerable role - parent details are now
// collected as part of Student registration (see parent email lookup below).
const roles = [
  { name: "Student", value: "Student", icon: "🎓" },
  { name: "Tutor", value: "Tutor", icon: "👩‍🏫" }
]

const form = ref({
  fullName: "",
  email: "",
  mobile: "",
  school: "",
  password: "",
  confirmPassword: "",
  parentEmail: "",
  parentName: "",
  parentPassword: "",
  parentConfirmPassword: "",
  parentPhone: ""
})

// Parent-email lookup state: 'idle' | 'checking' | 'found' | 'not_found' | 'error'
const parentCheckStatus = ref("idle")
const parentCheckMessage = ref("")
const foundParentName = ref("")

const EMAIL_RE = /^[\w.-]+@[\w.-]+\.\w+$/

function resetParentCheck() {
  parentCheckStatus.value = "idle"
  parentCheckMessage.value = ""
  foundParentName.value = ""
}

// Called when the Parent Email field loses focus. Looks the email up on the
// backend so we can either confirm the existing parent account or reveal
// the "new parent" fields dynamically.
async function checkParentEmail() {
  const email = form.value.parentEmail.trim()

  if (!email) {
    resetParentCheck()
    return
  }

  if (!EMAIL_RE.test(email)) {
    parentCheckStatus.value = "error"
    parentCheckMessage.value = "Please enter a valid parent email address."
    return
  }

  parentCheckStatus.value = "checking"
  parentCheckMessage.value = ""

  try {
    const data = await authApi.checkParentEmail(email)

    if (data.exists) {
      parentCheckStatus.value = "found"
      foundParentName.value = data.parent?.parent_name || ""
    } else {
      parentCheckStatus.value = "not_found"
      foundParentName.value = ""
    }
  } catch (err) {
    parentCheckStatus.value = "error"
    parentCheckMessage.value = err.message || "Could not check parent email right now."
  }
}

const register = async () => {
  authError.value = ""
  authSuccess.value = ""
  showLogoutPrompt.value = false

  if (
    !form.value.fullName ||
    !form.value.email ||
    !form.value.password ||
    !form.value.confirmPassword
  ) {
    authError.value = "Please fill all required fields."
    return
  }

  if (form.value.password !== form.value.confirmPassword) {
    authError.value = "Passwords do not match."
    return
  }

  let payload

  if (selectedRole.value === "Student") {
    if (!selectedSubjectIds.value.length) {
      authError.value = "Please select at least one subject."
      return
    }

    if (!form.value.parentEmail) {
      authError.value = "Please enter the Parent Email."
      return
    }

    if (parentCheckStatus.value === "idle" || parentCheckStatus.value === "checking") {
      // Make sure we know whether this parent already exists before submitting.
      await checkParentEmail()
    }

    if (parentCheckStatus.value === "error") {
      authError.value = parentCheckMessage.value || "Please enter a valid parent email address."
      return
    }

    const parentAlreadyExists = parentCheckStatus.value === "found"

    if (!parentAlreadyExists) {
      if (
        !form.value.parentName ||
        !form.value.parentPassword ||
        !form.value.parentConfirmPassword
      ) {
        authError.value = "Please fill in the new Parent account details."
        return
      }

      if (form.value.parentPassword !== form.value.parentConfirmPassword) {
        authError.value = "Parent passwords do not match."
        return
      }
    }

    payload = {
      student: {
        name: form.value.fullName,
        email: form.value.email,
        password: form.value.password,
        confirm_password: form.value.confirmPassword,
        phone_no: form.value.mobile,
        school: form.value.school.trim(),
        subject_ids: selectedSubjectIds.value
      },
      parent: parentAlreadyExists
        ? { email: form.value.parentEmail }
        : {
            email: form.value.parentEmail,
            name: form.value.parentName,
            password: form.value.parentPassword,
            confirm_password: form.value.parentConfirmPassword,
            phone_no: form.value.parentPhone
          }
    }
  } else {
    payload = {
      name: form.value.fullName,
      email: form.value.email,
      role: selectedRole.value,
      password: form.value.password,
      confirm_password: form.value.confirmPassword,
      phone_no: form.value.mobile
    }
  }

  submitting.value = true

  try {
    const data = await authApi.register(payload)

    if (data.success) {
      authSuccess.value = data.message || "Registration Successful! Please log in."

      form.value = {
        fullName: "",
        email: "",
        mobile: "",
        school: "",
        password: "",
        confirmPassword: "",
        parentEmail: "",
        parentName: "",
        parentPassword: "",
        parentConfirmPassword: "",
        parentPhone: ""
      }
      selectedSubjectIds.value = []
      resetParentCheck()

      setTimeout(() => {
        router.push("/login")
      }, 1200)
    } else {
      authError.value = data.message || "Registration failed."
    }
  } catch (err) {
    if (err.status === 409) {
      // The browser already holds an active session for a different
      // account. Give the person a direct way to clear it instead of
      // just telling them "already logged in" with no next step.
      authError.value = err.message || "You're already logged in. Please log out before creating a new account."
      showLogoutPrompt.value = true
    } else {
      authError.value = err.message || "Registration failed. Please try again."
    }
  } finally {
    submitting.value = false
  }
}

async function logOutAndRetry() {
  loggingOut.value = true
  try {
    await authApi.logout()
  } catch {
    // Best-effort - clear local state below regardless of API result.
  } finally {
    localStorage.removeItem('user')
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('user_id')
    localStorage.removeItem('username')
    localStorage.removeItem('parent_id')
    localStorage.removeItem('student_id')
    localStorage.removeItem('tutor_id')

    showLogoutPrompt.value = false
    authError.value = ""
    loggingOut.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 transition-colors duration-300">
    <AuthNavbar />

    <div class="flex items-center justify-center p-6">
      <div class="w-full max-w-lg bg-white dark:bg-slate-800 rounded-3xl shadow-2xl dark:shadow-slate-900/50 p-8 animate-card">
        <div class="text-center">
          <div class="text-6xl mb-3">🎓</div>

          <h1 class="text-3xl font-bold text-slate-800 dark:text-white">
            Create Account
          </h1>

          <p class="text-slate-500 dark:text-slate-400 mt-2">
            Join LearnAtHome and begin your learning journey.
          </p>
        </div>

        <div class="mt-8">
          <label class="font-semibold text-slate-700 dark:text-slate-300">
            Register As
          </label>

          <div class="grid grid-cols-2 gap-3 mt-3">
            <button
              v-for="r in roles"
              :key="r.value"
              type="button"
              @click="selectedRole = r.value"
              :class="
                selectedRole === r.value
                  ? 'bg-emerald-500 text-white'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
              "
              class="rounded-xl p-4 transition duration-300 hover:scale-105"
            >
              <div class="text-3xl">{{ r.icon }}</div>
              <div class="mt-2 text-sm font-semibold">{{ r.name }}</div>
            </button>
          </div>
        </div>

        <div v-if="selectedRole === 'Student'" class="mt-6">
          <label class="font-semibold text-slate-700 dark:text-slate-300">
            Subjects You're Interested In <span class="text-rose-500">*</span>
          </label>

          <p class="text-xs text-slate-400 mt-1 mb-3">
            Required — pick at least one so tutors and admins know what to set you up with.
          </p>

          <div v-if="subjectsLoading" class="text-sm text-slate-400">
            Loading subjects…
          </div>

          <div v-else-if="subjects.length" class="flex flex-wrap gap-2">
            <button
              v-for="s in subjects"
              :key="s.subject_id"
              type="button"
              @click="toggleSubject(s.subject_id)"
              :class="
                selectedSubjectIds.includes(s.subject_id)
                  ? 'bg-emerald-500 text-white border-emerald-500'
                  : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 border-slate-200 dark:border-slate-600'
              "
              class="rounded-full px-4 py-1.5 text-sm font-medium border transition duration-200"
            >
              {{ s.subject_name }}
            </button>
          </div>

          <p v-else class="text-sm text-rose-500 dark:text-rose-400">
            No subjects are available right now, so registration can't be completed. Please try again later or contact support.
          </p>
        </div>

        <form @submit.prevent="register" class="space-y-5 mt-8">
          <div>
            <label class="font-medium text-slate-700 dark:text-slate-300">
              Full Name
            </label>

            <input
              v-model="form.fullName"
              type="text"
              placeholder="Enter your full name"
              class="w-full mt-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 p-3 focus:outline-none focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 dark:focus:ring-emerald-900 transition-colors duration-300"
            />
          </div>

          <div>
            <label class="font-medium text-slate-700 dark:text-slate-300">
              Email Address
            </label>

            <input
              v-model="form.email"
              type="email"
              placeholder="Enter your email"
              class="w-full mt-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 p-3 focus:outline-none focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 dark:focus:ring-emerald-900 transition-colors duration-300"
            />
          </div>

          <div>
            <label class="font-medium text-slate-700 dark:text-slate-300">
              Mobile Number
            </label>

            <input
              v-model="form.mobile"
              type="text"
              placeholder="Enter your mobile number"
              class="w-full mt-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 p-3 focus:outline-none focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 dark:focus:ring-emerald-900 transition-colors duration-300"
            />
          </div>

          <div v-if="selectedRole === 'Student'">
            <label class="font-medium text-slate-700 dark:text-slate-300">
              School
            </label>

            <input
              v-model="form.school"
              type="text"
              placeholder="Enter your school name (optional)"
              class="w-full mt-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 p-3 focus:outline-none focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 dark:focus:ring-emerald-900 transition-colors duration-300"
            />
          </div>

          <div>
            <label class="font-medium text-slate-700 dark:text-slate-300">
              Password
            </label>

            <input
              v-model="form.password"
              type="password"
              placeholder="Create password"
              class="w-full mt-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 p-3 focus:outline-none focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 dark:focus:ring-emerald-900 transition-colors duration-300"
            />
          </div>

          <div>
            <label class="font-medium text-slate-700 dark:text-slate-300">
              Confirm Password
            </label>

            <input
              v-model="form.confirmPassword"
              type="password"
              placeholder="Confirm password"
              class="w-full mt-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 p-3 focus:outline-none focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 dark:focus:ring-emerald-900 transition-colors duration-300"
            />
          </div>

          <div v-if="selectedRole === 'Student'" class="pt-2 border-t border-slate-200 dark:border-slate-700">
            <p class="font-semibold text-slate-700 dark:text-slate-300 mt-5 mb-1">
              Parent Details
            </p>
            <p class="text-xs text-slate-400 mb-3">
              We'll link your account to your parent's account.
            </p>

            <div>
              <label class="font-medium text-slate-700 dark:text-slate-300">
                Parent Email
              </label>

              <input
                v-model="form.parentEmail"
                type="email"
                placeholder="Enter your parent's email"
                @blur="checkParentEmail"
                @input="resetParentCheck"
                class="w-full mt-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 p-3 focus:outline-none focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 dark:focus:ring-emerald-900 transition-colors duration-300"
              />

              <p v-if="parentCheckStatus === 'checking'" class="text-xs text-slate-400 mt-2">
                Checking parent email…
              </p>
              <p v-else-if="parentCheckStatus === 'found'" class="text-xs text-emerald-600 dark:text-emerald-400 mt-2">
                ✓ Parent account found{{ foundParentName ? ` for ${foundParentName}` : '' }}. We'll link your account to it.
              </p>
              <p v-else-if="parentCheckStatus === 'not_found'" class="text-xs text-blue-600 dark:text-blue-400 mt-2">
                No parent account found for this email — please fill in the parent details below to create one.
              </p>
              <p v-else-if="parentCheckStatus === 'error'" class="text-xs text-rose-600 dark:text-rose-400 mt-2">
                {{ parentCheckMessage }}
              </p>
            </div>

            <div v-if="parentCheckStatus === 'not_found'" class="space-y-5 mt-5">
              <div>
                <label class="font-medium text-slate-700 dark:text-slate-300">
                  Parent Name
                </label>

                <input
                  v-model="form.parentName"
                  type="text"
                  placeholder="Enter parent's full name"
                  class="w-full mt-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 p-3 focus:outline-none focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 dark:focus:ring-emerald-900 transition-colors duration-300"
                />
              </div>

              <div>
                <label class="font-medium text-slate-700 dark:text-slate-300">
                  Parent Phone
                </label>

                <input
                  v-model="form.parentPhone"
                  type="text"
                  placeholder="Enter parent's mobile number"
                  class="w-full mt-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 p-3 focus:outline-none focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 dark:focus:ring-emerald-900 transition-colors duration-300"
                />
              </div>

              <div>
                <label class="font-medium text-slate-700 dark:text-slate-300">
                  Parent Password
                </label>

                <input
                  v-model="form.parentPassword"
                  type="password"
                  placeholder="Create a password for the parent account"
                  class="w-full mt-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 p-3 focus:outline-none focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 dark:focus:ring-emerald-900 transition-colors duration-300"
                />
              </div>

              <div>
                <label class="font-medium text-slate-700 dark:text-slate-300">
                  Confirm Parent Password
                </label>

                <input
                  v-model="form.parentConfirmPassword"
                  type="password"
                  placeholder="Confirm parent password"
                  class="w-full mt-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 p-3 focus:outline-none focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 dark:focus:ring-emerald-900 transition-colors duration-300"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            :disabled="submitting"
            class="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-blue-500 dark:from-emerald-600 dark:to-blue-600 text-white font-semibold hover:scale-105 transition disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {{ submitting ? 'Creating Account...' : 'Create Account' }}
          </button>

          <p v-if="authError" class="text-center text-sm text-rose-600 dark:text-rose-400 font-medium">
            {{ authError }}
          </p>

          <button
            v-if="showLogoutPrompt"
            type="button"
            :disabled="loggingOut"
            @click="logOutAndRetry"
            class="w-full py-2.5 rounded-xl border border-rose-300 dark:border-rose-700 text-rose-600 dark:text-rose-400 font-semibold hover:bg-rose-50 dark:hover:bg-rose-900/20 transition disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {{ loggingOut ? 'Logging out…' : 'Log Out & Try Again' }}
          </button>

          <p v-if="authSuccess" class="text-center text-sm text-emerald-600 dark:text-emerald-400 font-medium">
            {{ authSuccess }}
          </p>
        </form>

        <p class="text-center mt-6 text-slate-700 dark:text-slate-300">
          Already have an account?
          <router-link
            to="/login"
            class="text-emerald-600 dark:text-emerald-400 font-semibold hover:text-emerald-700 dark:hover:text-emerald-300 transition-colors duration-300"
          >
            Login
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
input{
  outline:none;
  transition:.3s;
  font-size:15px;
}
input:focus{
  border-color:#10b981;
  box-shadow:0 0 0 4px rgba(16,185,129,.15);
}
input.dark\:text-white {
  color-scheme: dark;
}
button{
  cursor:pointer;
  transition:.3s ease;
}
button:hover{
  transform:translateY(-3px);
  box-shadow:0 12px 30px rgba(16,185,129,.20);
}
button:active{
  transform:scale(.97);
}
button.bg-emerald-500{
  box-shadow:0 12px 30px rgba(16,185,129,.25);
}
a{
  transition:.3s;
}
a:hover{
  color:#059669;
}
label{
  display:block;
  margin-bottom:6px;
}
.animate-card{
  animation:fadeUp .8s ease;
}
@keyframes fadeUp{
  from{
    opacity:0;
    transform:translateY(35px);
  }
  to{
    opacity:1;
    transform:translateY(0);
  }
}
.min-h-screen{
  background-size:200% 200%;
  animation:gradientMove 10s linear infinite;
}
@keyframes gradientMove{
  0%{ background-position:0% 50%; }
  50%{ background-position:100% 50%; }
  100%{ background-position:0% 50%; }
}
@media(max-width:640px){
  .max-w-lg{
    padding:24px;
  }
  h1{
    font-size:2rem;
  }
  .grid{
    grid-template-columns:1fr;
  }
}
</style>