<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import AuthNavbar from "../components/layout/AuthNavbar.vue"
import { authApi } from "../services/authApi"

const router = useRouter()

const selectedRole = ref("Student")
const authError = ref("")

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

const login = async () => {
  authError.value = ""

  if (!form.value.email || !form.value.password) {
    authError.value = "Please enter both Email and Password."
    return
  }

  try {
    const data = await authApi.login(form.value.email, form.value.password, rememberMe.value)

    if (!data || !data.success) {
      authError.value = data?.message || "Login failed"
      return
    }

    localStorage.clear()

    if (data.token) localStorage.setItem("token", data.token)
    if (data.role) localStorage.setItem("role", data.role)
    if (data.user_id !== undefined && data.user_id !== null) {
      localStorage.setItem("user_id", String(data.user_id))
    }
    if (data.username) localStorage.setItem("username", data.username)
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

    const roleLower = (data.role || selectedRole.value).toLowerCase()

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
    authError.value = err.message || "Something went wrong during login."
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 transition-colors duration-300">
    <AuthNavbar />

    <div class="flex items-center justify-center p-6">
      <div class="w-full max-w-md bg-white dark:bg-slate-800 rounded-3xl shadow-2xl dark:shadow-slate-900/50 p-8 animate-card">
        <h1 class="text-3xl font-bold text-center text-slate-800 dark:text-white">
          Welcome Back 👋
        </h1>

        <p class="text-center text-slate-500 dark:text-slate-400 mt-2">
          Login to LearnAtHome
        </p>

        <div class="grid grid-cols-2 gap-4 mt-8">
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
            <div class="mt-2 font-semibold">{{ r.name }}</div>
          </button>
        </div>

        <form @submit.prevent="login" class="space-y-5 mt-8">
          <div>
            <label class="font-medium text-slate-700 dark:text-slate-300">
              Email Address
            </label>
            <input
              v-model="form.email"
              type="email"
              placeholder="Enter your email"
              autocomplete="username"
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
              placeholder="Enter your password"
              autocomplete="current-password"
              class="w-full mt-2 rounded-xl border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-700 text-slate-800 dark:text-white placeholder:text-slate-400 dark:placeholder:text-slate-500 p-3 focus:outline-none focus:border-emerald-500 dark:focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100 dark:focus:ring-emerald-900 transition-colors duration-300"
            />
          </div>

          <div class="flex justify-between items-center text-sm">
            <label class="flex items-center text-slate-600 dark:text-slate-400">
              <input v-model="rememberMe" type="checkbox" class="mr-2 accent-emerald-500" />
              Remember Me
            </label>
          </div>

          <button
            type="submit"
            class="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-blue-500 dark:from-emerald-600 dark:to-blue-600 text-white font-semibold hover:scale-105 transition"
          >
            Login as {{ selectedRole }}
          </button>

          <p
            v-if="authError"
            class="text-center text-sm text-amber-600 dark:text-amber-400 font-medium"
          >
            {{ authError }}
          </p>
        </form>

        <p class="text-center mt-6 text-slate-700 dark:text-slate-300">
          Don't have an account?
          <router-link
            to="/register"
            class="text-emerald-600 dark:text-emerald-400 font-semibold hover:text-emerald-700 dark:hover:text-emerald-300 transition-colors duration-300"
          >
            Create Account
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
input {
  outline: none;
  transition: .3s;
  font-size: 15px;
  color: #1e293b;
}

input::placeholder {
  color: #94a3b8;
}

button {
  cursor: pointer;
  transition: .3s ease;
}

button:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(16,185,129,.20);
}

button:active {
  transform: scale(.97);
}

button.bg-emerald-500 {
  box-shadow: 0 12px 30px rgba(16,185,129,.25);
}

.animate-card {
  animation: fadeUp .8s ease;
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(35px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>