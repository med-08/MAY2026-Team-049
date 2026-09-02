<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue"
import { useRouter } from "vue-router"
import AuthNavbar from "../components/layout/AuthNavbar.vue"
import { authApi } from "../services/authApi"

const router = useRouter()

const selectedRole = ref("Student")
const authError = ref("")
const isDark = ref(false)

const roles = [
  { name: "Student", value: "Student", icon: "🎓" },
  { name: "Tutor", value: "Tutor", icon: "👩‍🏫" },
  { name: "Parent", value: "Parent", icon: "👨‍👩‍👧" },
  { name: "Admin", value: "Admin", icon: "⚙️" }
]

const form = ref({
  email: "",
  password: ""
})

const rememberMe = ref(false)


// ============================================================
// THEME DETECTION
// ============================================================

let themeObserver = null

const checkTheme = () => {
  const htmlDark = document.documentElement.classList.contains("dark")
  const bodyDark = document.body.classList.contains("dark")

  const savedTheme = localStorage.getItem("learnathome-theme")

  isDark.value =
    htmlDark ||
    bodyDark ||
    savedTheme === "dark"
}

onMounted(() => {
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

onBeforeUnmount(() => {
  if (themeObserver) {
    themeObserver.disconnect()
  }

  window.removeEventListener("storage", checkTheme)
})


// ============================================================
// LOGIN FUNCTIONALITY
// ============================================================

function clearAuthStorage() {
  localStorage.removeItem("user")
  localStorage.removeItem("token")
  localStorage.removeItem("role")
  localStorage.removeItem("user_id")
  localStorage.removeItem("username")
  localStorage.removeItem("parent_id")
  localStorage.removeItem("student_id")
  localStorage.removeItem("tutor_id")
}

const login = async () => {
  authError.value = ""

  if (!form.value.email || !form.value.password) {
    authError.value = "Please enter both Email and Password."
    return
  }

  try {
    const data = await authApi.login(
      form.value.email,
      form.value.password,
      rememberMe.value,
      selectedRole.value
    )

    if (!data || !data.success) {
      authError.value = data?.message || "Login failed"
      return
    }

    clearAuthStorage()

    if (data.token) {
      localStorage.setItem("token", data.token)
    }

    if (data.role) {
      localStorage.setItem("role", data.role)
    }

    if (data.user_id !== undefined && data.user_id !== null) {
      localStorage.setItem("user_id", String(data.user_id))
    }

    if (data.username) {
      localStorage.setItem("username", data.username)
    }

    if (data.parent_id !== undefined && data.parent_id !== null) {
      localStorage.setItem("parent_id", String(data.parent_id))
    }

    if (data.student_id !== undefined && data.student_id !== null) {
      localStorage.setItem("student_id", String(data.student_id))
    }

    if (data.tutor_id !== undefined && data.tutor_id !== null) {
      localStorage.setItem("tutor_id", String(data.tutor_id))
    }

    localStorage.setItem(
      "user",
      JSON.stringify({
        role: data.role,
        username: data.username || form.value.email,
        token: data.token || "",
        user_id: data.user_id ?? null,
        parent_id: data.parent_id ?? null,
        student_id: data.student_id ?? null,
        tutor_id: data.tutor_id ?? null
      })
    )

    const roleLower = (data.role || "")
      .toString()
      .trim()
      .toLowerCase()

    if (!roleLower) {
      clearAuthStorage()

      authError.value =
        "Login succeeded but no account role was returned. Please try again."

      return
    }

    let target = "/"

    if (roleLower === "student") {
      target = "/student/dashboard"
    } else if (roleLower === "tutor") {
      target = "/tutor/dashboard"
    } else if (roleLower === "parent") {
      target = "/parent"
    } else if (roleLower === "admin") {
      target = "/admin"
    }

    await router.push(target)

  } catch (err) {
    authError.value =
      err.message || "Something went wrong during login."
  }
}
</script>


<template>
  <!--
    IMPORTANT:
    The local "dark" class makes this page independent from
    Tailwind's dark-mode configuration.
  -->
  <div
    class="login-page"
    :class="{ dark: isDark }"
  >

    <AuthNavbar />


    <!-- ======================================================
         MAIN LOGIN AREA
    ======================================================= -->

    <main class="login-main">

      <div class="login-box">


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
              Learning feels
              <br />
              <span>better together.</span>
            </h1>


            <p>
              A simple space where students, tutors and parents
              can stay connected throughout the learning journey.
            </p>


            <!-- Small abstract illustration -->
            <div class="illustration">

              <div class="illustration-window">

                <div class="window-top">
                  <div class="window-dot"></div>
                  <div class="window-line"></div>
                  <div class="window-menu">•••</div>
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
                <div class="mini-icon">✓</div>
                <div>
                  <strong>Organised</strong>
                  <small>Everything together</small>
                </div>
              </div>


              <div class="mini-card mini-two">
                <div class="mini-icon">✦</div>
                <div>
                  <strong>Connected</strong>
                  <small>Learn together</small>
                </div>
              </div>

            </div>

          </div>

        </section>



        <!-- ==================================================
             RIGHT SIDE
        =================================================== -->

        <section class="form-side">

          <div class="form-container">


            <!-- Welcome -->
            <div class="form-heading">

              <div class="hello-icon">
                👋
              </div>

              <h2>
                Welcome Back
              </h2>

              <p>
                Sign in to continue to LearnAtHome
              </p>

            </div>


            <!-- Role selection -->
            <div class="role-area">

              <div class="field-title">
                CONTINUE AS
              </div>


              <div class="roles">

                <button
                  v-for="r in roles"
                  :key="r.value"
                  type="button"
                  class="role"
                  :class="{
                    active: selectedRole === r.value
                  }"
                  @click="selectedRole = r.value"
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
                 FORM
            ================================================== -->

            <form
              class="login-form"
              @submit.prevent="login"
            >


              <!-- Email -->
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
                    autocomplete="username"
                  />

                </div>

              </div>



              <!-- Password -->
              <div class="input-group">

                <label>
                  Password
                </label>

                <div class="input-box">

                  <span class="input-symbol password-symbol">
                    •••
                  </span>

                  <input
                    v-model="form.password"
                    type="password"
                    placeholder="Enter your password"
                    autocomplete="current-password"
                  />

                </div>

              </div>



              <!-- Remember -->
              <label class="remember">

                <input
                  v-model="rememberMe"
                  type="checkbox"
                />

                <span class="checkbox"></span>

                <span>
                  Remember Me
                </span>

              </label>



              <!-- Login -->
              <button
                type="submit"
                class="login-button"
              >

                <span>
                  Login as {{ selectedRole }}
                </span>

                <span class="button-arrow">
                  →
                </span>

              </button>


              <!-- Error -->
              <p
                v-if="authError"
                class="error"
              >
                {{ authError }}
              </p>

            </form>



            <!-- Register -->
            <p class="register">

              Don't have an account?

              <router-link to="/register">
                Create Account
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
   GLOBAL PAGE
============================================================ */

.login-page {
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

.login-main {
  min-height: calc(100vh - 72px);

  display: flex;
  align-items: center;
  justify-content: center;

  padding: 28px 24px 35px;
}


.login-box {
  width: 100%;
  max-width: 1120px;

  min-height: 590px;

  display: grid;
  grid-template-columns: 48% 52%;

  overflow: hidden;

  border-radius: 27px;

  background: #ffffff;

  box-shadow:
    0 20px 60px rgba(15, 23, 42, 0.10);

  transition:
    background 0.3s ease,
    box-shadow 0.3s ease;

  animation: appear 0.55s ease both;
}


/* ============================================================
   LEFT
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

  transition: background 0.3s ease;
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

  background: rgba(255,255,255,0.72);

  border: 1px solid rgba(16,185,129,0.15);

  color: #087c63;

  font-size: 11px;

  font-weight: 800;

  letter-spacing: .04em;
}


.platform-pill span {
  width: 7px;
  height: 7px;

  border-radius: 50%;

  background: #10b981;

  box-shadow:
    0 0 0 4px rgba(16,185,129,.10);

  animation: pulse 2s infinite;
}


.welcome-side h1 {
  margin: 25px 0 14px;

  color: #13233e;

  font-size: 48px;

  line-height: 1.03;

  letter-spacing: -.045em;

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
  max-width: 450px;

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

  height: 230px;

  margin-top: 35px;
}


.illustration-window {
  position: absolute;

  left: 13%;
  right: 7%;
  bottom: 0;

  height: 175px;

  border-radius: 21px;

  background: rgba(255,255,255,.76);

  border: 1px solid rgba(255,255,255,.9);

  box-shadow:
    0 18px 40px rgba(30,100,100,.12);

  backdrop-filter: blur(12px);

  animation: float 5s ease-in-out infinite;
}


.window-top {
  height: 38px;

  display: flex;

  align-items: center;

  gap: 8px;

  padding: 0 14px;

  border-bottom: 1px solid rgba(100,116,139,.10);
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
  height: 94px;

  display: flex;

  align-items: center;

  justify-content: center;

  gap: 22px;
}


.main-circle {
  width: 65px;
  height: 65px;

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
    0 0 0 7px rgba(16,185,129,.08),
    0 10px 25px rgba(16,185,129,.18);
}


.fake-text {
  width: 110px;
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

  background: rgba(255,255,255,.93);

  border: 1px solid rgba(255,255,255,.95);

  box-shadow:
    0 12px 25px rgba(30,80,90,.13);

  backdrop-filter: blur(10px);
}


.mini-one {
  top: 20px;
  left: 0;

  animation: miniFloat 4s ease-in-out infinite;
}


.mini-two {
  right: 0;
  bottom: 17px;

  animation: miniFloat 4.5s ease-in-out infinite reverse;
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
   DECORATIVE CIRCLES
============================================================ */

.background-circle {
  position: absolute;

  border-radius: 50%;

  filter: blur(45px);

  opacity: .35;
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
   RIGHT FORM
============================================================ */

.form-side {
  display: flex;

  align-items: center;

  justify-content: center;

  padding: 38px 48px;

  background: #ffffff;

  transition: background .3s ease;
}


.form-container {
  width: 100%;

  max-width: 490px;
}


.form-heading {
  text-align: center;

  margin-bottom: 23px;
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

  animation: wave 3s infinite;
}


.form-heading h2 {
  margin: 0;

  color: #18243a;

  font-size: 32px;

  letter-spacing: -.035em;

  font-weight: 900;
}


.form-heading p {
  margin: 6px 0 0;

  color: #8292a7;

  font-size: 14px;
}


/* ============================================================
   ROLES
============================================================ */

.field-title {
  margin-bottom: 9px;

  color: #687990;

  font-size: 11px;

  font-weight: 800;

  letter-spacing: .06em;
}


.roles {
  display: grid;

  grid-template-columns:
    repeat(4, 1fr);

  gap: 8px;
}


.role {
  position: relative;

  height: 78px;

  display: flex;

  flex-direction: column;

  align-items: center;

  justify-content: center;

  gap: 6px;

  border: 1px solid #e1e8ef;

  border-radius: 14px;

  background: #f8fafc;

  color: #53647b;

  cursor: pointer;

  transition:
    transform .2s ease,
    background .2s ease,
    border-color .2s ease,
    box-shadow .2s ease;
}


.role:hover {
  transform: translateY(-2px);

  border-color: #a7dfce;

  box-shadow:
    0 7px 18px rgba(16,185,129,.08);
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
    0 8px 20px rgba(16,185,129,.10);
}


.role-emoji {
  font-size: 22px;

  line-height: 1;
}


.role-label {
  font-size: 11px;

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

.login-form {
  margin-top: 21px;
}


.input-group {
  margin-bottom: 15px;
}


.input-group label {
  display: block;

  margin-bottom: 7px;

  color: #394960;

  font-size: 12px;

  font-weight: 800;
}


.input-box {
  position: relative;
}


.input-symbol {
  position: absolute;

  left: 13px;
  top: 50%;

  transform: translateY(-50%);

  width: 30px;
  height: 30px;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 8px;

  background: #edf9f6;

  color: #059669;

  font-size: 13px;

  font-weight: 900;
}


.password-symbol {
  font-size: 9px;

  letter-spacing: 1px;
}


.input-box input {
  width: 100%;

  height: 53px;

  padding:
    0 14px 0 54px;

  border: 1px solid #dce4ec;

  border-radius: 13px;

  outline: none;

  background: #ffffff;

  color: #1e293b;

  font-size: 13px;

  transition:
    border .2s ease,
    box-shadow .2s ease,
    background .2s ease;
}


.input-box input::placeholder {
  color: #9baabe;
}


.input-box input:focus {
  border-color: #10b981;

  box-shadow:
    0 0 0 3px rgba(16,185,129,.09);
}


/* ============================================================
   REMEMBER
============================================================ */

.remember {
  display: inline-flex;

  align-items: center;

  gap: 8px;

  margin: 0 0 17px;

  color: #75859a;

  font-size: 12px;

  cursor: pointer;
}


.remember input {
  position: absolute;

  opacity: 0;
}


.checkbox {
  width: 17px;
  height: 17px;

  border: 1px solid #cbd5e1;

  border-radius: 4px;

  background: #ffffff;

  position: relative;
}


.remember input:checked + .checkbox {
  background: #10b981;

  border-color: #10b981;
}


.remember input:checked + .checkbox::after {
  content: "✓";

  position: absolute;

  left: 3px;
  top: -2px;

  color: white;

  font-size: 12px;

  font-weight: 900;
}


/* ============================================================
   BUTTON
============================================================ */

.login-button {
  width: 100%;

  height: 52px;

  display: flex;

  align-items: center;

  justify-content: center;

  gap: 10px;

  border: none;

  border-radius: 13px;

  background:
    linear-gradient(
      100deg,
      #10b981,
      #0891b2
    );

  color: white;

  font-size: 13px;

  font-weight: 800;

  cursor: pointer;

  box-shadow:
    0 10px 22px rgba(16,185,129,.18);

  transition:
    transform .2s ease,
    box-shadow .2s ease;
}


.login-button:hover {
  transform: translateY(-2px);

  box-shadow:
    0 14px 27px rgba(16,185,129,.25);
}


.login-button:active {
  transform: scale(.99);
}


.button-arrow {
  font-size: 18px;

  transition: transform .2s ease;
}


.login-button:hover .button-arrow {
  transform: translateX(4px);
}


/* ============================================================
   ERROR
============================================================ */

.error {
  margin: 10px 0 0;

  padding: 8px 10px;

  border-radius: 8px;

  background: #fff7ed;

  color: #c2410c;

  text-align: center;

  font-size: 11px;

  font-weight: 600;
}


/* ============================================================
   REGISTER
============================================================ */

.register {
  margin: 17px 0 0;

  text-align: center;

  color: #8291a5;

  font-size: 12px;
}


.register a {
  color: #059669;

  font-weight: 800;

  text-decoration: none;
}


.register a:hover {
  color: #047857;
}


/* ============================================================
   DARK MODE
   THIS IS THE IMPORTANT PART
============================================================ */

.login-page.dark {
  background:
    radial-gradient(
      circle at 10% 20%,
      rgba(16,185,129,.08),
      transparent 32%
    ),
    radial-gradient(
      circle at 90% 85%,
      rgba(14,165,233,.07),
      transparent 30%
    ),
    #070d19;

  color: #e6edf6;
}


.login-page.dark .login-box {
  background: #111a2a;

  box-shadow:
    0 25px 65px rgba(0,0,0,.40);
}


/* LEFT DARK */

.login-page.dark .welcome-side {
  background:
    linear-gradient(
      145deg,
      #102f2d,
      #102a32 55%,
      #10243a
    );
}


.login-page.dark .platform-pill {
  background: rgba(10,30,39,.78);

  border-color: rgba(52,211,153,.18);

  color: #6ee7b7;
}


.login-page.dark .welcome-side h1 {
  color: #f1f6fc;
}


.login-page.dark .welcome-side h1 span {
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


.login-page.dark .welcome-side p {
  color: #a4b7ca;
}


.login-page.dark .illustration-window {
  background: rgba(18,35,48,.82);

  border-color: rgba(148,163,184,.10);

  box-shadow:
    0 18px 40px rgba(0,0,0,.25);
}


.login-page.dark .window-top {
  border-bottom-color: rgba(148,163,184,.10);
}


.login-page.dark .window-line {
  background: #35485a;
}


.login-page.dark .fake-text span {
  background: #35485a;
}


.login-page.dark .window-bottom div {
  background: #263b4c;
}


.login-page.dark .mini-card {
  background: rgba(20,36,49,.95);

  border-color: rgba(148,163,184,.10);

  box-shadow:
    0 12px 25px rgba(0,0,0,.30);
}


.login-page.dark .mini-card strong {
  color: #e5edf6;
}


.login-page.dark .mini-card small {
  color: #879bb0;
}


.login-page.dark .mini-icon {
  background: rgba(16,185,129,.13);

  color: #6ee7b7;
}


/* RIGHT DARK */

.login-page.dark .form-side {
  background: #111a2a;
}


.login-page.dark .form-heading h2 {
  color: #f1f5fb;
}


.login-page.dark .form-heading p {
  color: #91a5ba;
}


.login-page.dark .hello-icon {
  background: #182b40;
}


.login-page.dark .field-title {
  color: #93a6bb;
}


.login-page.dark .role {
  background: #182337;

  border-color: #2a394d;

  color: #afbdd0;
}


.login-page.dark .role:hover {
  background: #1c2a3e;

  border-color: #397866;
}


.login-page.dark .role.active {
  background:
    linear-gradient(
      145deg,
      #12372f,
      #12343b
    );

  border-color: #10b981;

  color: #6ee7b7;

  box-shadow:
    0 8px 20px rgba(16,185,129,.10);
}


.login-page.dark .input-group label {
  color: #c5d1df;
}


.login-page.dark .input-box input {
  background: #182337;

  border-color: #2c3c51;

  color: #edf4fc;
}


.login-page.dark .input-box input::placeholder {
  color: #71859b;
}


.login-page.dark .input-box input:focus {
  background: #1a293d;

  border-color: #10b981;

  box-shadow:
    0 0 0 3px rgba(16,185,129,.10);
}


.login-page.dark .input-symbol {
  background: rgba(16,185,129,.12);

  color: #6ee7b7;
}


.login-page.dark .remember {
  color: #91a4b9;
}


.login-page.dark .checkbox {
  background: #182337;

  border-color: #405066;
}


.login-page.dark .register {
  color: #8ea1b6;
}


.login-page.dark .register a {
  color: #6ee7b7;
}


.login-page.dark .error {
  background: rgba(154,52,18,.16);

  border: 1px solid rgba(251,146,60,.12);

  color: #fdba74;
}


/* ============================================================
   ANIMATIONS
============================================================ */

@keyframes appear {

  from {
    opacity: 0;

    transform:
      translateY(18px)
      scale(.985);
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
      0 0 0 4px rgba(16,185,129,.10);
  }

  50% {
    box-shadow:
      0 0 0 7px rgba(16,185,129,.03);
  }

}


@keyframes wave {

  0%,
  100% {
    transform: rotate(0);
  }

  8% {
    transform: rotate(10deg);
  }

  16% {
    transform: rotate(-8deg);
  }

  24% {
    transform: rotate(5deg);
  }

  32% {
    transform: rotate(0);
  }

}


/* ============================================================
   RESPONSIVE
============================================================ */

@media (max-width: 950px) {

  .login-box {
    grid-template-columns: 1fr;

    max-width: 560px;
  }


  .welcome-side {
    min-height: 400px;

    padding: 35px 35px 20px;
  }


  .welcome-side h1 {
    font-size: 42px;
  }


  .illustration {
    height: 180px;

    margin-top: 20px;
  }


  .illustration-window {
    height: 145px;
  }


  .window-body {
    height: 75px;
  }


  .form-side {
    padding: 35px;
  }

}


@media (max-width: 600px) {

  .login-main {
    padding: 14px;
  }


  .login-box {
    border-radius: 21px;
  }


  .welcome-side {
    min-height: 350px;

    padding: 28px 23px 15px;
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
    padding: 30px 20px;
  }


  .roles {
    grid-template-columns:
      repeat(2, 1fr);
  }


  .form-heading h2 {
    font-size: 28px;
  }

}

</style>