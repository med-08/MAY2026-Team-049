<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue"
import { useRouter } from "vue-router"
import AuthNavbar from "../components/layout/AuthNavbar.vue"
import { authApi } from "../services/authApi"

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

const isDark = ref(false)

// ============================================================
// ROLES
// ============================================================

const roles = [
  {
    name: "Student",
    value: "Student",
    icon: "🎓"
  },
  {
    name: "Tutor",
    value: "Tutor",
    icon: "👩‍🏫"
  }
]

// ============================================================
// FORM
// ============================================================

const form = ref({
  fullName: "",
  email: "",
  mobile: "",
  school: "",
  password: "",
  confirmPassword: "",

  // Parent
  parentEmail: "",
  parentName: "",
  parentPassword: "",
  parentConfirmPassword: "",
  parentPhone: "",

  // Tutor
  bio: "",
  experience: "",
  education: "",
  hourlyRate: "",
  availability: "",
  teachingLanguages: ""
})

// ============================================================
// PARENT EMAIL CHECK
// ============================================================

const parentCheckStatus = ref("idle")
const parentCheckMessage = ref("")
const foundParentName = ref("")

const EMAIL_RE = /^[\w.-]+@[\w.-]+\.\w+$/

function resetParentCheck() {
  parentCheckStatus.value = "idle"
  parentCheckMessage.value = ""
  foundParentName.value = ""
}

async function checkParentEmail() {
  const email = form.value.parentEmail.trim()

  if (!email) {
    resetParentCheck()
    return
  }

  if (!EMAIL_RE.test(email)) {
    parentCheckStatus.value = "error"
    parentCheckMessage.value =
      "Please enter a valid parent email address."
    return
  }

  parentCheckStatus.value = "checking"
  parentCheckMessage.value = ""

  try {
    const data = await authApi.checkParentEmail(email)

    if (data.exists) {
      parentCheckStatus.value = "found"
      foundParentName.value =
        data.parent?.parent_name || ""
    } else {
      parentCheckStatus.value = "not_found"
      foundParentName.value = ""
    }
  } catch (err) {
    parentCheckStatus.value = "error"
    parentCheckMessage.value =
      err.message ||
      "Could not check parent email right now."
  }
}

// ============================================================
// SUBJECTS
// ============================================================

function toggleSubject(id) {
  const idx = selectedSubjectIds.value.indexOf(id)

  if (idx === -1) {
    selectedSubjectIds.value.push(id)
  } else {
    selectedSubjectIds.value.splice(idx, 1)
  }
}

onMounted(async () => {
  try {
    const data = await authApi.getSubjects()
    subjects.value = data.data || []
  } catch {
    subjects.value = []
  } finally {
    subjectsLoading.value = false
  }

  checkTheme()

  themeObserver = new MutationObserver(() => {
    checkTheme()
  })

  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["class"]
  })

  themeObserver.observe(document.body, {
    attributes: true,
    attributeFilter: ["class"]
  })

  window.addEventListener("storage", checkTheme)
})

// ============================================================
// THEME
// ============================================================

let themeObserver = null

const checkTheme = () => {
  const htmlDark =
    document.documentElement.classList.contains("dark")

  const bodyDark =
    document.body.classList.contains("dark")

  const savedTheme =
    localStorage.getItem("learnathome-theme")

  isDark.value =
    htmlDark ||
    bodyDark ||
    savedTheme === "dark"
}

onBeforeUnmount(() => {
  if (themeObserver) {
    themeObserver.disconnect()
  }

  window.removeEventListener("storage", checkTheme)
})

// ============================================================
// REGISTRATION
// ============================================================

const register = async () => {
  authError.value = ""
  authSuccess.value = ""
  showLogoutPrompt.value = false

  if (
    !form.value.fullName.trim() ||
    !form.value.email.trim() ||
    !form.value.password ||
    !form.value.confirmPassword
  ) {
    authError.value =
      "Please fill all required fields."
    return
  }

  if (
    form.value.password !==
    form.value.confirmPassword
  ) {
    authError.value =
      "Passwords do not match."
    return
  }

  let payload

  // ==========================================================
  // STUDENT
  // ==========================================================

  if (selectedRole.value === "Student") {
    if (!selectedSubjectIds.value.length) {
      authError.value =
        "Please select at least one subject."
      return
    }

    if (!form.value.parentEmail.trim()) {
      authError.value =
        "Please enter the Parent Email."
      return
    }

    if (
      parentCheckStatus.value === "idle" ||
      parentCheckStatus.value === "checking"
    ) {
      await checkParentEmail()
    }

    if (parentCheckStatus.value === "error") {
      authError.value =
        parentCheckMessage.value ||
        "Please enter a valid parent email address."
      return
    }

    const parentAlreadyExists =
      parentCheckStatus.value === "found"

    if (!parentAlreadyExists) {
      if (
        !form.value.parentName.trim() ||
        !form.value.parentPassword ||
        !form.value.parentConfirmPassword
      ) {
        authError.value =
          "Please fill in the new Parent account details."
        return
      }

      if (
        form.value.parentPassword !==
        form.value.parentConfirmPassword
      ) {
        authError.value =
          "Parent passwords do not match."
        return
      }
    }

    payload = {
      student: {
        name: form.value.fullName,
        email: form.value.email,
        password: form.value.password,
        confirm_password:
          form.value.confirmPassword,
        phone_no: form.value.mobile,
        school: form.value.school.trim(),
        subject_ids: selectedSubjectIds.value
      },

      parent: parentAlreadyExists
        ? {
            email: form.value.parentEmail
          }
        : {
            email: form.value.parentEmail,
            name: form.value.parentName,
            password: form.value.parentPassword,
            confirm_password:
              form.value.parentConfirmPassword,
            phone_no: form.value.parentPhone
          }
    }
  }

  // ==========================================================
  // TUTOR
  // ==========================================================

  else {
    if (!selectedSubjectIds.value.length) {
      authError.value =
        "Please select at least one subject you can teach."
      return
    }

    payload = {
      name: form.value.fullName,
      email: form.value.email,
      role: selectedRole.value,
      password: form.value.password,
      confirm_password:
        form.value.confirmPassword,
      phone_no: form.value.mobile,

      bio: form.value.bio.trim(),

      experience_years:
        form.value.experience,

      education:
        form.value.education.trim(),

      hourly_rate:
        form.value.hourlyRate.trim(),

      availability:
        form.value.availability.trim(),

      subject_ids:
        selectedSubjectIds.value,

      languages:
        form.value.teachingLanguages
          .split(",")
          .map((lang) => lang.trim())
          .filter(Boolean)
    }
  }

  submitting.value = true

  try {
    const data =
      await authApi.register(payload)

    if (data.success) {
      authSuccess.value =
        data.message ||
        "Registration successful! Please log in."

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
        parentPhone: "",

        bio: "",
        experience: "",
        education: "",
        hourlyRate: "",
        availability: "",
        teachingLanguages: ""
      }

      selectedSubjectIds.value = []

      resetParentCheck()

      setTimeout(() => {
        router.push("/login")
      }, 1200)
    } else {
      authError.value =
        data.message ||
        "Registration failed."
    }
  } catch (err) {
    if (err.status === 409) {
      authError.value =
        err.message ||
        "You're already logged in. Please log out before creating a new account."

      showLogoutPrompt.value = true
    } else {
      authError.value =
        err.message ||
        "Registration failed. Please try again."
    }
  } finally {
    submitting.value = false
  }
}

// ============================================================
// LOGOUT AND RETRY
// ============================================================

async function logOutAndRetry() {
  loggingOut.value = true

  try {
    await authApi.logout()
  } catch {
    // Best effort logout
  } finally {
    localStorage.removeItem("user")
    localStorage.removeItem("token")
    localStorage.removeItem("role")
    localStorage.removeItem("user_id")
    localStorage.removeItem("username")
    localStorage.removeItem("parent_id")
    localStorage.removeItem("student_id")
    localStorage.removeItem("tutor_id")

    showLogoutPrompt.value = false
    authError.value = ""
    loggingOut.value = false
  }
}

// ============================================================
// ROLE CHANGE
// ============================================================

function changeRole(role) {
  selectedRole.value = role

  authError.value = ""
  authSuccess.value = ""

  selectedSubjectIds.value = []

  resetParentCheck()
}
</script>

<template>
  <div
    class="register-page"
    :class="{ dark: isDark }"
  >
    <AuthNavbar />

    <main class="register-main">
      <div class="register-box">

        <!-- ==================================================
             LEFT SIDE
        =================================================== -->

        <section class="welcome-side">
          <div class="background-circle circle-one"></div>
          <div class="background-circle circle-two"></div>

          <div class="welcome-content">

            <div class="platform-pill">
              <span></span>
              ONE PLATFORM • THREE ROLES
            </div>

            <h1>
              Start your
              <br />
              <span>learning journey.</span>
            </h1>

            <p>
              Create your LearnAtHome account and bring
              students, tutors and parents together in one
              simple learning space.
            </p>

            <!-- ABSTRACT ILLUSTRATION -->

            <div class="illustration">

              <div class="illustration-window">

                <div class="window-top">
                  <div class="window-dot"></div>
                  <div class="window-line"></div>
                  <div class="window-menu">
                    •••
                  </div>
                </div>

                <div class="window-body">

                  <div class="main-circle">
                    ✦
                  </div>

                  <div class="fake-text">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>

                </div>

                <div class="window-bottom">
                  <div></div>
                  <div></div>
                  <div></div>
                </div>

              </div>

              <div class="mini-card mini-one">
                <div class="mini-icon">
                  ✓
                </div>

                <div>
                  <strong>
                    Personalised
                  </strong>

                  <small>
                    Learning together
                  </small>
                </div>
              </div>

              <div class="mini-card mini-two">
                <div class="mini-icon">
                  ✦
                </div>

                <div>
                  <strong>
                    Connected
                  </strong>

                  <small>
                    One learning space
                  </small>
                </div>
              </div>

            </div>

            <!-- BENEFITS -->

            <div class="benefits">

              <div class="benefit">
                <span class="benefit-icon">
                  ✓
                </span>

                <span>
                  Simple & secure registration
                </span>
              </div>

              <div class="benefit">
                <span class="benefit-icon">
                  ✓
                </span>

                <span>
                  Connect with your learning community
                </span>
              </div>

            </div>

          </div>
        </section>


        <!-- ==================================================
             RIGHT SIDE
        =================================================== -->

        <section class="form-side">

          <div class="form-container">

            <!-- HEADER -->

            <div class="form-heading">

              <div class="hello-icon">
                ✨
              </div>

              <h2>
                Create Account
              </h2>

              <p>
                Join LearnAtHome and begin learning
              </p>

            </div>


            <!-- ROLE -->

            <div class="role-area">

              <div class="field-title">
                REGISTER AS
              </div>

              <div class="roles">

                <button
                  v-for="r in roles"
                  :key="r.value"
                  type="button"
                  class="role"
                  :class="{
                    active:
                      selectedRole === r.value
                  }"
                  @click="changeRole(r.value)"
                >

                  <span class="role-emoji">
                    {{ r.icon }}
                  </span>

                  <span class="role-label">
                    {{ r.name }}
                  </span>

                  <span
                    v-if="selectedRole === r.value"
                    class="role-check"
                  >
                    ✓
                  </span>

                </button>

              </div>

            </div>


            <!-- =================================================
                 REGISTRATION FORM
            ================================================== -->

            <form
              class="register-form"
              @submit.prevent="register"
            >

              <!-- BASIC DETAILS -->

              <div class="section-label">
                PERSONAL DETAILS
              </div>

              <!-- NAME -->

              <div class="input-group">

                <label>
                  Full Name
                </label>

                <div class="input-box">

                  <span class="input-symbol">
                    ✦
                  </span>

                  <input
                    v-model="form.fullName"
                    type="text"
                    placeholder="Enter your full name"
                    autocomplete="name"
                  />

                </div>

              </div>


              <!-- EMAIL -->

              <div class="input-group">

                <label>
                  Email Address
                </label>

                <div class="input-box">

                  <span class="input-symbol">
                    @
                  </span>

                  <input
                    v-model="form.email"
                    type="email"
                    placeholder="Enter your email"
                    autocomplete="email"
                  />

                </div>

              </div>


              <!-- MOBILE -->

              <div class="input-group">

                <label>
                  Mobile Number
                </label>

                <div class="input-box">

                  <span class="input-symbol">
                    ☎
                  </span>

                  <input
                    v-model="form.mobile"
                    type="text"
                    placeholder="Enter your mobile number"
                    autocomplete="tel"
                  />

                </div>

              </div>


              <!-- SCHOOL -->

              <div
                v-if="selectedRole === 'Student'"
                class="input-group"
              >

                <label>
                  School
                  <span class="optional">
                    OPTIONAL
                  </span>
                </label>

                <div class="input-box">

                  <span class="input-symbol">
                    ◈
                  </span>

                  <input
                    v-model="form.school"
                    type="text"
                    placeholder="Enter your school name"
                  />

                </div>

              </div>


              <!-- =================================================
                   SUBJECTS
              ================================================== -->

              <div class="section-label subjects-label">
                {{
                  selectedRole === "Student"
                    ? "SUBJECTS YOU'RE INTERESTED IN"
                    : "SUBJECTS YOU TEACH"
                }}
              </div>

              <p class="section-help">

                {{
                  selectedRole === "Student"
                    ? "Choose at least one subject you want help with."
                    : "Choose at least one subject you can teach."
                }}

              </p>

              <div
                v-if="subjectsLoading"
                class="subjects-loading"
              >
                <span class="loading-dot"></span>
                Loading subjects...
              </div>

              <div
                v-else-if="subjects.length"
                class="subjects"
              >

                <button
                  v-for="s in subjects"
                  :key="s.subject_id"
                  type="button"
                  class="subject-chip"
                  :class="{
                    selected:
                      selectedSubjectIds.includes(
                        s.subject_id
                      )
                  }"
                  @click="
                    toggleSubject(
                      s.subject_id
                    )
                  "
                >

                  <span
                    v-if="
                      selectedSubjectIds.includes(
                        s.subject_id
                      )
                    "
                    class="subject-check"
                  >
                    ✓
                  </span>

                  {{ s.subject_name }}

                </button>

              </div>

              <p
                v-else
                class="subjects-error"
              >
                No subjects are available right now.
                Please try again later or contact support.
              </p>


              <!-- =================================================
                   TUTOR PROFILE
              ================================================== -->

              <div
                v-if="selectedRole === 'Tutor'"
                class="profile-section"
              >

                <div class="section-label">
                  TEACHING PROFILE
                </div>

                <p class="section-help">
                  Tell students a little about your
                  teaching background.
                </p>


                <!-- BIO -->

                <div class="input-group">

                  <label>
                    Personal Bio
                    <span class="optional">
                      OPTIONAL
                    </span>
                  </label>

                  <textarea
                    v-model="form.bio"
                    rows="3"
                    placeholder="Tell students a little about yourself..."
                  ></textarea>

                </div>


                <!-- EXPERIENCE + RATE -->

                <div class="two-column">

                  <div class="input-group">

                    <label>
                      Experience
                    </label>

                    <div class="input-box">

                      <span class="input-symbol">
                        ◷
                      </span>

                      <input
                        v-model="form.experience"
                        type="number"
                        min="0"
                        placeholder="Years"
                      />

                    </div>

                  </div>


                  <div class="input-group">

                    <label>
                      Hourly Rate
                    </label>

                    <div class="input-box">

                      <span class="input-symbol">
                        ₹
                      </span>

                      <input
                        v-model="form.hourlyRate"
                        type="text"
                        placeholder="e.g. ₹500/hr"
                      />

                    </div>

                  </div>

                </div>


                <!-- EDUCATION -->

                <div class="input-group">

                  <label>
                    Education
                  </label>

                  <div class="input-box">

                    <span class="input-symbol">
                      ◇
                    </span>

                    <input
                      v-model="form.education"
                      type="text"
                      placeholder="e.g. B.Tech Computer Science"
                    />

                  </div>

                </div>


                <!-- LANGUAGES -->

                <div class="input-group">

                  <label>
                    Teaching Language(s)
                  </label>

                  <div class="input-box">

                    <span class="input-symbol">
                      A
                    </span>

                    <input
                      v-model="
                        form.teachingLanguages
                      "
                      type="text"
                      placeholder="e.g. English, Hindi"
                    />

                  </div>

                  <p class="field-help">
                    Separate multiple languages with commas.
                  </p>

                </div>


                <!-- AVAILABILITY -->

                <div class="input-group">

                  <label>
                    Availability
                  </label>

                  <div class="input-box">

                    <span class="input-symbol">
                      ◷
                    </span>

                    <input
                      v-model="form.availability"
                      type="text"
                      placeholder="e.g. Mon-Fri, 4 PM - 8 PM"
                    />

                  </div>

                </div>

              </div>


              <!-- =================================================
                   PASSWORD
              ================================================== -->

              <div class="section-label password-label">
                ACCOUNT SECURITY
              </div>


              <!-- PASSWORD -->

              <div class="input-group">

                <label>
                  Password
                </label>

                <div class="input-box">

                  <span
                    class="input-symbol password-symbol"
                  >
                    •••
                  </span>

                  <input
                    v-model="form.password"
                    type="password"
                    placeholder="Create a password"
                    autocomplete="new-password"
                  />

                </div>

              </div>


              <!-- CONFIRM -->

              <div class="input-group">

                <label>
                  Confirm Password
                </label>

                <div class="input-box">

                  <span
                    class="input-symbol password-symbol"
                  >
                    •••
                  </span>

                  <input
                    v-model="
                      form.confirmPassword
                    "
                    type="password"
                    placeholder="Confirm your password"
                    autocomplete="new-password"
                  />

                </div>

              </div>


              <!-- =================================================
                   PARENT
              ================================================== -->

              <div
                v-if="selectedRole === 'Student'"
                class="parent-section"
              >

                <div class="section-label">
                  PARENT CONNECTION
                </div>

                <p class="section-help">
                  Link your account with your parent's
                  LearnAtHome account.
                </p>


                <!-- PARENT EMAIL -->

                <div class="input-group">

                  <label>
                    Parent Email
                  </label>

                  <div class="input-box">

                    <span class="input-symbol">
                      @
                    </span>

                    <input
                      v-model="
                        form.parentEmail
                      "
                      type="email"
                      placeholder="Enter your parent's email"
                      autocomplete="email"
                      @blur="checkParentEmail"
                      @input="resetParentCheck"
                    />

                  </div>


                  <!-- CHECKING -->

                  <p
                    v-if="
                      parentCheckStatus ===
                      'checking'
                    "
                    class="status checking"
                  >
                    <span class="status-spinner"></span>
                    Checking parent account...
                  </p>


                  <!-- FOUND -->

                  <p
                    v-else-if="
                      parentCheckStatus ===
                      'found'
                    "
                    class="status found"
                  >
                    ✓ Parent account found
                    {{
                      foundParentName
                        ? `for ${foundParentName}`
                        : ""
                    }}.
                    Your account will be linked.
                  </p>


                  <!-- NOT FOUND -->

                  <p
                    v-else-if="
                      parentCheckStatus ===
                      'not_found'
                    "
                    class="status not-found"
                  >
                    No parent account found.
                    Please create the parent account
                    below.
                  </p>


                  <!-- ERROR -->

                  <p
                    v-else-if="
                      parentCheckStatus ===
                      'error'
                    "
                    class="status error-status"
                  >
                    {{ parentCheckMessage }}
                  </p>

                </div>


                <!-- NEW PARENT -->

                <div
                  v-if="
                    parentCheckStatus ===
                    'not_found'
                  "
                  class="new-parent"
                >

                  <div class="new-parent-heading">
                    <span>+</span>

                    <div>
                      <strong>
                        Create Parent Account
                      </strong>

                      <small>
                        These details will be used
                        for the linked parent account.
                      </small>
                    </div>
                  </div>


                  <!-- PARENT NAME -->

                  <div class="input-group">

                    <label>
                      Parent Name
                    </label>

                    <div class="input-box">

                      <span class="input-symbol">
                        ✦
                      </span>

                      <input
                        v-model="
                          form.parentName
                        "
                        type="text"
                        placeholder="Enter parent's full name"
                      />

                    </div>

                  </div>


                  <!-- PARENT PHONE -->

                  <div class="input-group">

                    <label>
                      Parent Phone
                    </label>

                    <div class="input-box">

                      <span class="input-symbol">
                        ☎
                      </span>

                      <input
                        v-model="
                          form.parentPhone
                        "
                        type="text"
                        placeholder="Enter parent's mobile number"
                      />

                    </div>

                  </div>


                  <!-- PARENT PASSWORD -->

                  <div class="input-group">

                    <label>
                      Parent Password
                    </label>

                    <div class="input-box">

                      <span
                        class="
                          input-symbol
                          password-symbol
                        "
                      >
                        •••
                      </span>

                      <input
                        v-model="
                          form.parentPassword
                        "
                        type="password"
                        placeholder="Create parent password"
                        autocomplete="new-password"
                      />

                    </div>

                  </div>


                  <!-- PARENT CONFIRM -->

                  <div class="input-group">

                    <label>
                      Confirm Parent Password
                    </label>

                    <div class="input-box">

                      <span
                        class="
                          input-symbol
                          password-symbol
                        "
                      >
                        •••
                      </span>

                      <input
                        v-model="
                          form.parentConfirmPassword
                        "
                        type="password"
                        placeholder="Confirm parent password"
                        autocomplete="new-password"
                      />

                    </div>

                  </div>

                </div>

              </div>


              <!-- =================================================
                   SUBMIT
              ================================================== -->

              <button
                type="submit"
                class="register-button"
                :disabled="submitting"
              >

                <span>
                  {{
                    submitting
                      ? "Creating Account..."
                      : `Create ${selectedRole} Account`
                  }}
                </span>

                <span class="button-arrow">
                  →
                </span>

              </button>


              <!-- ERROR -->

              <div
                v-if="authError"
                class="message error-message"
              >
                <span>!</span>
                {{ authError }}
              </div>


              <!-- SUCCESS -->

              <div
                v-if="authSuccess"
                class="message success-message"
              >
                <span>✓</span>
                {{ authSuccess }}
              </div>


              <!-- LOGOUT -->

              <button
                v-if="showLogoutPrompt"
                type="button"
                class="logout-button"
                :disabled="loggingOut"
                @click="logOutAndRetry"
              >
                {{
                  loggingOut
                    ? "Logging out..."
                    : "Log Out & Try Again"
                }}
              </button>

            </form>


            <!-- LOGIN -->

            <p class="login-link">

              Already have an account?

              <router-link to="/login">
                Login
              </router-link>

            </p>

          </div>

        </section>

      </div>
    </main>
  </div>
</template>

<style scoped>
/* ============================================================
   PAGE
============================================================ */

.register-page {
  min-height: 100vh;

  background:
    radial-gradient(
      circle at 10% 20%,
      rgba(16, 185, 129, 0.10),
      transparent 32%
    ),
    radial-gradient(
      circle at 90% 85%,
      rgba(14, 165, 233, 0.08),
      transparent 30%
    ),
    #f7fafc;

  color: #18263d;

  transition:
    background 0.3s ease,
    color 0.3s ease;
}


/* ============================================================
   MAIN
============================================================ */

.register-main {
  min-height: calc(100vh - 72px);

  display: flex;
  align-items: center;
  justify-content: center;

  padding: 28px 24px 40px;
}


.register-box {
  width: 100%;
  max-width: 1160px;

  display: grid;
  grid-template-columns: 45% 55%;

  overflow: hidden;

  border-radius: 27px;

  background: #ffffff;

  box-shadow:
    0 20px 60px rgba(15, 23, 42, 0.10);

  animation: appear 0.55s ease both;
}


/* ============================================================
   LEFT SIDE
============================================================ */

.welcome-side {
  position: relative;
  overflow: hidden;

  background:
    linear-gradient(
      145deg,
      #d8f8ec,
      #e5f9f5 55%,
      #e7f5fb
    );

  padding: 48px 46px;
}


.welcome-content {
  position: relative;
  z-index: 3;
}


.platform-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;

  padding: 8px 13px;

  border-radius: 999px;

  background: rgba(255, 255, 255, 0.72);

  border: 1px solid rgba(16, 185, 129, 0.15);

  color: #087c63;

  font-size: 11px;
  font-weight: 800;

  letter-spacing: 0.04em;
}


.platform-pill span {
  width: 7px;
  height: 7px;

  border-radius: 50%;

  background: #10b981;

  box-shadow:
    0 0 0 4px rgba(16, 185, 129, 0.10);

  animation: pulse 2s infinite;
}


.welcome-side h1 {
  margin: 25px 0 14px;

  color: #13233e;

  font-size: 46px;
  line-height: 1.04;

  letter-spacing: -0.045em;

  font-weight: 900;
}


.welcome-side h1 span {
  background:
    linear-gradient(
      90deg,
      #059669,
      #0891b2
    );

  -webkit-background-clip: text;
  background-clip: text;

  color: transparent;
}


.welcome-side p {
  max-width: 440px;

  margin: 0;

  color: #60768d;

  font-size: 15px;
  line-height: 1.65;

  font-weight: 500;
}


/* ============================================================
   ILLUSTRATION
============================================================ */

.illustration {
  position: relative;

  width: 100%;
  height: 220px;

  margin-top: 32px;
}


.illustration-window {
  position: absolute;

  left: 10%;
  right: 5%;
  bottom: 0;

  height: 170px;

  border-radius: 21px;

  background: rgba(255, 255, 255, 0.76);

  border: 1px solid rgba(255, 255, 255, 0.9);

  box-shadow:
    0 18px 40px rgba(30, 100, 100, 0.12);

  backdrop-filter: blur(12px);

  animation: float 5s ease-in-out infinite;
}


.window-top {
  height: 38px;

  display: flex;
  align-items: center;

  gap: 8px;

  padding: 0 14px;

  border-bottom:
    1px solid rgba(100, 116, 139, 0.10);
}


.window-dot {
  width: 7px;
  height: 7px;

  border-radius: 50%;

  background: #aebdc7;
}


.window-line {
  width: 60px;
  height: 6px;

  border-radius: 20px;

  background: #d7e2e7;
}


.window-menu {
  margin-left: auto;

  color: #a6b5bd;

  font-size: 11px;
  letter-spacing: 2px;
}


.window-body {
  height: 91px;

  display: flex;
  align-items: center;
  justify-content: center;

  gap: 22px;
}


.main-circle {
  width: 63px;
  height: 63px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 50%;

  background:
    linear-gradient(
      145deg,
      #10b981,
      #0891b2
    );

  color: white;

  font-size: 27px;

  box-shadow:
    0 0 0 7px rgba(16, 185, 129, 0.08),
    0 10px 25px rgba(16, 185, 129, 0.18);
}


.fake-text {
  width: 105px;
}


.fake-text span {
  display: block;

  height: 7px;

  margin: 10px 0;

  border-radius: 20px;

  background: #d9e5e9;
}


.fake-text span:nth-child(2) {
  width: 75%;
}


.fake-text span:nth-child(3) {
  width: 50%;
}


.window-bottom {
  display: flex;
  gap: 8px;

  padding: 0 18px;
}


.window-bottom div {
  height: 24px;

  flex: 1;

  border-radius: 7px;

  background: #e6f1f1;
}


/* ============================================================
   MINI CARDS
============================================================ */

.mini-card {
  position: absolute;
  z-index: 5;

  display: flex;
  align-items: center;

  gap: 9px;

  padding: 10px 12px;

  border-radius: 14px;

  background: rgba(255, 255, 255, 0.93);

  border:
    1px solid rgba(255, 255, 255, 0.95);

  box-shadow:
    0 12px 25px rgba(30, 80, 90, 0.13);

  backdrop-filter: blur(10px);
}


.mini-one {
  top: 16px;
  left: 0;

  animation:
    miniFloat 4s ease-in-out infinite;
}


.mini-two {
  right: 0;
  bottom: 14px;

  animation:
    miniFloat 4.5s ease-in-out infinite reverse;
}


.mini-icon {
  width: 28px;
  height: 28px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 8px;

  background: #dcfce7;

  color: #059669;

  font-size: 13px;
  font-weight: 900;
}


.mini-card strong {
  display: block;

  color: #334155;

  font-size: 10px;
}


.mini-card small {
  display: block;

  margin-top: 2px;

  color: #94a3b8;

  font-size: 8px;
}


/* ============================================================
   BENEFITS
============================================================ */

.benefits {
  display: flex;
  flex-direction: column;

  gap: 9px;

  margin-top: 5px;
}


.benefit {
  display: flex;
  align-items: center;

  gap: 9px;

  color: #557087;

  font-size: 11px;
  font-weight: 600;
}


.benefit-icon {
  width: 20px;
  height: 20px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 50%;

  background: rgba(16, 185, 129, 0.12);

  color: #059669;

  font-size: 10px;
  font-weight: 900;
}


/* ============================================================
   DECORATIVE CIRCLES
============================================================ */

.background-circle {
  position: absolute;

  border-radius: 50%;

  filter: blur(45px);

  opacity: 0.35;
}


.circle-one {
  width: 180px;
  height: 180px;

  top: -90px;
  left: -50px;

  background: #a7f3d0;
}


.circle-two {
  width: 180px;
  height: 180px;

  right: -80px;
  bottom: -80px;

  background: #bae6fd;
}


/* ============================================================
   RIGHT SIDE
============================================================ */

.form-side {
  display: flex;
  justify-content: center;

  padding: 38px 48px;

  background: #ffffff;
}


.form-container {
  width: 100%;
  max-width: 500px;
}


.form-heading {
  text-align: center;

  margin-bottom: 22px;
}


.hello-icon {
  width: 46px;
  height: 46px;

  display: flex;
  align-items: center;
  justify-content: center;

  margin: 0 auto 10px;

  border-radius: 14px;

  background: #eef7ff;

  font-size: 23px;

  animation: sparkle 3s infinite;
}


.form-heading h2 {
  margin: 0;

  color: #18243a;

  font-size: 31px;

  letter-spacing: -0.035em;

  font-weight: 900;
}


.form-heading p {
  margin: 6px 0 0;

  color: #8292a7;

  font-size: 13px;
}


/* ============================================================
   ROLES
============================================================ */

.field-title,
.section-label {
  color: #687990;

  font-size: 10px;

  font-weight: 900;

  letter-spacing: 0.07em;
}


.role-area {
  margin-bottom: 20px;
}


.roles {
  display: grid;

  grid-template-columns:
    repeat(2, 1fr);

  gap: 9px;

  margin-top: 9px;
}


.role {
  position: relative;

  height: 66px;

  display: flex;
  align-items: center;
  justify-content: center;

  gap: 9px;

  border:
    1px solid #e1e8ef;

  border-radius: 14px;

  background: #f8fafc;

  color: #53647b;

  cursor: pointer;

  transition:
    transform 0.2s ease,
    background 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}


.role:hover {
  transform: translateY(-2px);

  border-color: #a7dfce;

  box-shadow:
    0 7px 18px rgba(16, 185, 129, 0.08);
}


.role.active {
  background:
    linear-gradient(
      145deg,
      #effcf7,
      #e8faf5
    );

  border-color: #10b981;

  color: #087c63;

  box-shadow:
    0 8px 20px rgba(16, 185, 129, 0.10);
}


.role-emoji {
  font-size: 23px;
}


.role-label {
  font-size: 12px;
  font-weight: 800;
}


.role-check {
  position: absolute;

  top: 5px;
  right: 5px;

  width: 17px;
  height: 17px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 50%;

  background: #10b981;

  color: white;

  font-size: 9px;
  font-weight: 900;
}


/* ============================================================
   FORM
============================================================ */

.register-form {
  margin-top: 5px;
}


.section-label {
  margin-top: 21px;
  margin-bottom: 8px;
}


.section-label:first-child {
  margin-top: 0;
}


.section-help {
  margin: -2px 0 11px;

  color: #8b9aab;

  font-size: 11px;

  line-height: 1.5;
}


.input-group {
  margin-bottom: 13px;
}


.input-group label {
  display: block;

  margin-bottom: 6px;

  color: #394960;

  font-size: 11px;

  font-weight: 800;
}


.optional {
  margin-left: 5px;

  color: #a0adba;

  font-size: 8px;

  font-weight: 800;

  letter-spacing: 0.05em;
}


/* ============================================================
   INPUT
============================================================ */

.input-box {
  position: relative;
}


.input-symbol {
  position: absolute;

  left: 12px;
  top: 50%;

  transform:
    translateY(-50%);

  width: 29px;
  height: 29px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 8px;

  background: #edf9f6;

  color: #059669;

  font-size: 12px;

  font-weight: 900;

  pointer-events: none;
}


.password-symbol {
  font-size: 8px;
  letter-spacing: 1px;
}


.input-box input,
textarea {
  width: 100%;

  border:
    1px solid #dce4ec;

  border-radius: 12px;

  outline: none;

  background: #ffffff;

  color: #1e293b;

  font-size: 12px;

  transition:
    border 0.2s ease,
    box-shadow 0.2s ease,
    background 0.2s ease;
}


.input-box input {
  height: 48px;

  padding:
    0 13px 0 52px;
}


textarea {
  min-height: 80px;

  resize: vertical;

  padding: 12px 13px;

  line-height: 1.5;
}


.input-box input::placeholder,
textarea::placeholder {
  color: #9baabe;
}


.input-box input:focus,
textarea:focus {
  border-color: #10b981;

  box-shadow:
    0 0 0 3px rgba(16, 185, 129, 0.09);
}


/* ============================================================
   SUBJECTS
============================================================ */

.subjects-label {
  margin-top: 20px;
}


.subjects {
  display: flex;

  flex-wrap: wrap;

  gap: 7px;

  margin-bottom: 12px;
}


.subject-chip {
  min-height: 32px;

  display: inline-flex;
  align-items: center;

  gap: 5px;

  padding: 6px 11px;

  border:
    1px solid #e1e8ef;

  border-radius: 999px;

  background: #f8fafc;

  color: #53647b;

  font-size: 10px;

  font-weight: 700;

  cursor: pointer;

  transition:
    transform 0.18s ease,
    background 0.18s ease,
    border-color 0.18s ease,
    color 0.18s ease;
}


.subject-chip:hover {
  transform: translateY(-1px);

  border-color: #a7dfce;

  color: #087c63;
}


.subject-chip.selected {
  background:
    linear-gradient(
      100deg,
      #10b981,
      #0891b2
    );

  border-color: transparent;

  color: white;

  box-shadow:
    0 5px 12px rgba(16, 185, 129, 0.16);
}


.subject-check {
  font-size: 9px;
}


.subjects-loading {
  display: flex;
  align-items: center;

  gap: 8px;

  padding: 10px 0;

  color: #8b9aab;

  font-size: 11px;
}


.loading-dot {
  width: 8px;
  height: 8px;

  border-radius: 50%;

  border:
    2px solid #10b981;

  border-top-color: transparent;

  animation: spin 0.8s linear infinite;
}


.subjects-error {
  padding: 9px 11px;

  border-radius: 9px;

  background: #fff7ed;

  color: #c2410c;

  font-size: 10px;

  line-height: 1.5;
}


/* ============================================================
   TUTOR
============================================================ */

.profile-section {
  margin-top: 5px;

  padding-top: 4px;
}


.two-column {
  display: grid;

  grid-template-columns:
    repeat(2, 1fr);

  gap: 10px;
}


.field-help {
  margin: 5px 0 0;

  color: #9aa8b7;

  font-size: 9px;
}


/* ============================================================
   PARENT
============================================================ */

.parent-section {
  margin-top: 5px;

  padding-top: 3px;
}


.status {
  margin: 6px 0 0;

  font-size: 10px;

  line-height: 1.45;
}


.checking {
  display: flex;
  align-items: center;

  gap: 6px;

  color: #8292a7;
}


.status-spinner {
  width: 10px;
  height: 10px;

  border:
    1.5px solid #10b981;

  border-top-color: transparent;

  border-radius: 50%;

  animation: spin 0.8s linear infinite;
}


.found {
  color: #059669;
}


.not-found {
  color: #0284c7;
}


.error-status {
  color: #dc2626;
}


.new-parent {
  margin-top: 13px;

  padding: 15px;

  border:
    1px solid #dcefe9;

  border-radius: 15px;

  background:
    linear-gradient(
      145deg,
      #f7fffc,
      #f5fbff
    );
}


.new-parent-heading {
  display: flex;
  align-items: flex-start;

  gap: 9px;

  margin-bottom: 14px;
}


.new-parent-heading > span {
  width: 24px;
  height: 24px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 7px;

  background: #dcfce7;

  color: #059669;

  font-size: 15px;
  font-weight: 700;
}


.new-parent-heading strong {
  display: block;

  color: #334155;

  font-size: 11px;
}


.new-parent-heading small {
  display: block;

  margin-top: 2px;

  color: #8b9aab;

  font-size: 9px;
}


/* ============================================================
   BUTTON
============================================================ */

.register-button {
  width: 100%;
  height: 51px;

  display: flex;
  align-items: center;
  justify-content: center;

  gap: 10px;

  margin-top: 21px;

  border: none;

  border-radius: 13px;

  background:
    linear-gradient(
      100deg,
      #10b981,
      #0891b2
    );

  color: white;

  font-size: 12px;

  font-weight: 800;

  cursor: pointer;

  box-shadow:
    0 10px 22px rgba(16, 185, 129, 0.18);

  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    opacity 0.2s ease;
}


.register-button:hover:not(:disabled) {
  transform: translateY(-2px);

  box-shadow:
    0 14px 27px rgba(16, 185, 129, 0.25);
}


.register-button:active:not(:disabled) {
  transform: scale(0.99);
}


.register-button:disabled {
  cursor: not-allowed;

  opacity: 0.65;
}


.button-arrow {
  font-size: 18px;

  transition:
    transform 0.2s ease;
}


.register-button:hover:not(:disabled)
.button-arrow {
  transform:
    translateX(4px);
}


/* ============================================================
   MESSAGES
============================================================ */

.message {
  display: flex;
  align-items: center;
  justify-content: center;

  gap: 7px;

  margin-top: 10px;

  padding: 9px 11px;

  border-radius: 9px;

  text-align: center;

  font-size: 10px;

  font-weight: 600;

  line-height: 1.4;
}


.error-message {
  background: #fff7ed;

  color: #c2410c;
}


.error-message span {
  width: 16px;
  height: 16px;

  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 50%;

  background: #fed7aa;

  font-size: 9px;
}


.success-message {
  background: #ecfdf5;

  color: #059669;
}


.success-message span {
  font-weight: 900;
}


.logout-button {
  width: 100%;

  height: 42px;

  margin-top: 9px;

  border:
    1px solid #fecaca;

  border-radius: 11px;

  background: transparent;

  color: #dc2626;

  font-size: 11px;

  font-weight: 800;

  cursor: pointer;

  transition:
    background 0.2s ease,
    transform 0.2s ease;
}


.logout-button:hover:not(:disabled) {
  background: #fef2f2;

  transform: translateY(-1px);
}


.logout-button:disabled {
  opacity: 0.6;

  cursor: not-allowed;
}


/* ============================================================
   LOGIN LINK
============================================================ */

.login-link {
  margin: 18px 0 0;

  text-align: center;

  color: #8291a5;

  font-size: 11px;
}


.login-link a {
  margin-left: 3px;

  color: #059669;

  font-weight: 800;

  text-decoration: none;

  transition: color 0.2s ease;
}


.login-link a:hover {
  color: #047857;
}


/* ============================================================
   DARK MODE
============================================================ */

.register-page.dark {
  background:
    radial-gradient(
      circle at 10% 20%,
      rgba(16, 185, 129, 0.08),
      transparent 32%
    ),
    radial-gradient(
      circle at 90% 85%,
      rgba(14, 165, 233, 0.07),
      transparent 30%
    ),
    #070d19;

  color: #e6edf6;
}


.register-page.dark .register-box {
  background: #111a2a;

  box-shadow:
    0 25px 65px rgba(0, 0, 0, 0.40);
}


/* LEFT */

.register-page.dark .welcome-side {
  background:
    linear-gradient(
      145deg,
      #102f2d,
      #102a32 55%,
      #10243a
    );
}


.register-page.dark .platform-pill {
  background: rgba(10, 30, 39, 0.78);

  border-color:
    rgba(52, 211, 153, 0.18);

  color: #6ee7b7;
}


.register-page.dark .welcome-side h1 {
  color: #f1f6fc;
}


.register-page.dark .welcome-side h1 span {
  background:
    linear-gradient(
      90deg,
      #34d399,
      #22d3ee
    );

  -webkit-background-clip: text;
  background-clip: text;

  color: transparent;
}


.register-page.dark .welcome-side p {
  color: #a4b7ca;
}


.register-page.dark .benefit {
  color: #9eb2c5;
}


.register-page.dark .illustration-window {
  background: rgba(18, 35, 48, 0.82);

  border-color:
    rgba(148, 163, 184, 0.10);

  box-shadow:
    0 18px 40px rgba(0, 0, 0, 0.25);
}


.register-page.dark .window-top {
  border-bottom-color:
    rgba(148, 163, 184, 0.10);
}


.register-page.dark .window-line,
.register-page.dark .fake-text span {
  background: #35485a;
}


.register-page.dark .window-bottom div {
  background: #263b4c;
}


.register-page.dark .mini-card {
  background: rgba(20, 36, 49, 0.95);

  border-color:
    rgba(148, 163, 184, 0.10);

  box-shadow:
    0 12px 25px rgba(0, 0, 0, 0.30);
}


.register-page.dark .mini-card strong {
  color: #e5edf6;
}


.register-page.dark .mini-card small {
  color: #879bb0;
}


.register-page.dark .mini-icon {
  background: rgba(16, 185, 129, 0.13);

  color: #6ee7b7;
}


/* RIGHT */

.register-page.dark .form-side {
  background: #111a2a;
}


.register-page.dark .form-heading h2 {
  color: #f1f5fb;
}


.register-page.dark .form-heading p {
  color: #91a5ba;
}


.register-page.dark .hello-icon {
  background: #182b40;
}


.register-page.dark .field-title,
.register-page.dark .section-label {
  color: #93a6bb;
}


.register-page.dark .section-help {
  color: #8297ad;
}


.register-page.dark .role {
  background: #182337;

  border-color: #2a394d;

  color: #afbdd0;
}


.register-page.dark .role:hover {
  background: #1c2a3e;

  border-color: #397866;
}


.register-page.dark .role.active {
  background:
    linear-gradient(
      145deg,
      #12372f,
      #12343b
    );

  border-color: #10b981;

  color: #6ee7b7;
}


.register-page.dark .input-group label {
  color: #c5d1df;
}


.register-page.dark .optional {
  color: #687c91;
}


.register-page.dark .input-box input,
.register-page.dark textarea {
  background: #182337;

  border-color: #2c3c51;

  color: #edf4fc;
}


.register-page.dark .input-box input::placeholder,
.register-page.dark textarea::placeholder {
  color: #71859b;
}


.register-page.dark .input-box input:focus,
.register-page.dark textarea:focus {
  background: #1a293d;

  border-color: #10b981;

  box-shadow:
    0 0 0 3px rgba(16, 185, 129, 0.10);
}


.register-page.dark .input-symbol {
  background: rgba(16, 185, 129, 0.12);

  color: #6ee7b7;
}


.register-page.dark .subject-chip {
  background: #182337;

  border-color: #2a394d;

  color: #afbdd0;
}


.register-page.dark .subject-chip:hover {
  border-color: #397866;

  color: #6ee7b7;
}


.register-page.dark .subject-chip.selected {
  background:
    linear-gradient(
      100deg,
      #10b981,
      #0891b2
    );

  border-color: transparent;

  color: white;
}


.register-page.dark .new-parent {
  background:
    linear-gradient(
      145deg,
      #13262a,
      #142536
    );

  border-color: #28454a;
}


.register-page.dark .new-parent-heading strong {
  color: #e5edf6;
}


.register-page.dark .new-parent-heading small {
  color: #8499ad;
}


.register-page.dark .login-link {
  color: #8ea1b6;
}


.register-page.dark .login-link a {
  color: #6ee7b7;
}


.register-page.dark .error-message {
  background: rgba(154, 52, 18, 0.16);

  border:
    1px solid rgba(251, 146, 60, 0.12);

  color: #fdba74;
}


.register-page.dark .success-message {
  background: rgba(16, 185, 129, 0.10);

  color: #6ee7b7;
}


.register-page.dark .logout-button {
  border-color: #7f3030;

  color: #fca5a5;
}


.register-page.dark .logout-button:hover:not(:disabled) {
  background: rgba(127, 29, 29, 0.18);
}


/* ============================================================
   ANIMATIONS
============================================================ */

@keyframes appear {
  from {
    opacity: 0;

    transform:
      translateY(18px)
      scale(0.985);
  }

  to {
    opacity: 1;

    transform:
      translateY(0)
      scale(1);
  }
}


@keyframes float {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-6px);
  }
}


@keyframes miniFloat {
  0%,
  100% {
    transform: translateY(0);
  }

  50% {
    transform: translateY(-6px);
  }
}


@keyframes pulse {
  0%,
  100% {
    box-shadow:
      0 0 0 4px
      rgba(16, 185, 129, 0.10);
  }

  50% {
    box-shadow:
      0 0 0 7px
      rgba(16, 185, 129, 0.03);
  }
}


@keyframes sparkle {
  0%,
  100% {
    transform: rotate(0);
  }

  50% {
    transform: rotate(5deg) scale(1.04);
  }
}


@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}


/* ============================================================
   RESPONSIVE
============================================================ */

@media (max-width: 1000px) {
  .register-box {
    grid-template-columns: 1fr;

    max-width: 650px;
  }

  .welcome-side {
    min-height: 390px;

    padding:
      38px 38px 25px;
  }

  .welcome-side h1 {
    font-size: 42px;
  }

  .illustration {
    height: 175px;

    margin-top: 20px;
  }

  .illustration-window {
    height: 145px;
  }

  .window-body {
    height: 70px;
  }

  .benefits {
    display: none;
  }

  .form-side {
    padding:
      35px;
  }
}


@media (max-width: 650px) {
  .register-main {
    padding: 14px;
  }

  .register-box {
    border-radius: 21px;
  }

  .welcome-side {
    min-height: 350px;

    padding:
      28px 23px 15px;
  }

  .platform-pill {
    font-size: 9px;
  }

  .welcome-side h1 {
    font-size: 35px;

    margin-top: 20px;
  }

  .welcome-side p {
    font-size: 13px;
  }

  .illustration {
    height: 145px;
  }

  .illustration-window {
    left: 10%;

    height: 120px;
  }

  .main-circle {
    width: 48px;
    height: 48px;

    font-size: 20px;
  }

  .fake-text {
    width: 80px;
  }

  .mini-card {
    padding: 7px 9px;
  }

  .mini-card strong {
    font-size: 8px;
  }

  .mini-card small {
    font-size: 7px;
  }

  .mini-icon {
    width: 23px;
    height: 23px;
  }

  .form-side {
    padding:
      30px 20px;
  }

  .form-heading h2 {
    font-size: 28px;
  }

  .two-column {
    grid-template-columns: 1fr;
    gap: 0;
  }
}


@media (max-width: 430px) {
  .roles {
    gap: 7px;
  }

  .role {
    height: 60px;
  }

  .role-emoji {
    font-size: 20px;
  }

  .role-label {
    font-size: 10px;
  }

  .new-parent {
    padding: 12px;
  }

  .register-button {
    height: 49px;
  }
}
</style>