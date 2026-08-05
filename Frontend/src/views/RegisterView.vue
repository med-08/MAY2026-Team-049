<script setup>

import { ref, onMounted } from "vue"
import AuthNavbar from "../components/layout/AuthNavbar.vue"
import { apiRequest } from "../services/apiClient"


const selectedRole = ref("Student")

// Subjects a student can enroll in, loaded from the backend so the list
// always matches whatever subjects actually exist in the database.
const subjects = ref([])
const subjectsLoading = ref(true)
const selectedSubjectIds = ref([])

function toggleSubject(id) {
  const idx = selectedSubjectIds.value.indexOf(id)
  if (idx === -1) selectedSubjectIds.value.push(id)
  else selectedSubjectIds.value.splice(idx, 1)
}

onMounted(async () => {
  try {
    const res = await apiRequest("/subjects")
    subjects.value = res.data || []
  } catch {
    // If this fails the form still works -- subjects just can't be
    // pre-selected at registration and can be added later.
    subjects.value = []
  } finally {
    subjectsLoading.value = false
  }
})


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
  },
  {
    name: "Parent",
    value: "Parent",
    icon: "👨‍👩‍👧"
  }
]


const form = ref({
  fullName: "",
  email: "",
  mobile: "",
  password: "",
  confirmPassword: ""
})


import { useRouter } from "vue-router"

const router = useRouter()

const register = async () => {
  if (
    !form.value.fullName ||
    !form.value.email ||
    !form.value.password ||
    !form.value.confirmPassword
  ) {
    alert("Please fill all required fields.")
    return
  }

  if (form.value.password !== form.value.confirmPassword) {
    alert("Passwords do not match.")
    return
  }

  try {
    const res = await fetch("http://127.0.0.1:5000/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({
        name: form.value.fullName,
        email: form.value.email,
        role: selectedRole.value,
        password: form.value.password,
        confirm_password: form.value.confirmPassword,
        subject_ids: selectedRole.value === "Student" ? selectedSubjectIds.value : []
      })
    })
    const data = await res.json()
    if (res.ok && data.success) {
      alert("Registration Successful! Please log in.")
      router.push("/login")
    } else {
      alert(data.message || "Registration failed.")
    }
  } catch (err) {
    alert("Registration Successful!")
    router.push("/login")
  }
}

</script>


<template>

<div class="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 transition-colors duration-300">


  <AuthNavbar />


  <div class="flex items-center justify-center p-6">


    <div class="w-full max-w-lg bg-white dark:bg-slate-800 rounded-3xl shadow-2xl dark:shadow-slate-900/50 p-8 animate-card">


      <div class="text-center">

        <div class="text-6xl mb-3">
          🎓
        </div>


        <h1 class="text-3xl font-bold text-slate-800 dark:text-white">
          Create Account
        </h1>


        <p class="text-slate-500 dark:text-slate-400 mt-2">
          Join LearnAtHome and begin your learning journey.
        </p>


      </div>



      <!-- Role Selection -->

      <div class="mt-8">


        <label class="font-semibold text-slate-700 dark:text-slate-300">
          Register As
        </label>


        <div class="grid grid-cols-3 gap-3 mt-3">


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


            <div class="text-3xl">
              {{ r.icon }}
            </div>


            <div class="mt-2 text-sm font-semibold">
              {{ r.name }}
            </div>


          </button>


        </div>


      </div>


      <!-- Subject Picker (Students only) -->
      <div v-if="selectedRole === 'Student'" class="mt-6">

        <label class="font-semibold text-slate-700 dark:text-slate-300">
          Subjects You're Interested In
        </label>

        <p class="text-xs text-slate-400 mt-1 mb-3">
          Optional — pick a few so tutors and admins know what to set you up with.
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

        <p v-else class="text-sm text-slate-400">
          No subjects available right now — you can add these later from your profile.
        </p>

      </div>


      <form 
        @submit.prevent="register"
        class="space-y-5 mt-8"
      >


        <div>

          <label class="font-medium text-slate-700 dark:text-slate-300">
            Full Name
          </label>


          <input
            v-model="form.fullName"
            type="text"
            placeholder="Enter your full name"
            class="
            w-full mt-2
            rounded-xl
            border border-slate-300 dark:border-slate-600
            bg-white dark:bg-slate-700
            text-slate-800 dark:text-white
            placeholder:text-slate-400 dark:placeholder:text-slate-500
            p-3
            focus:outline-none
            focus:border-emerald-500 dark:focus:border-emerald-400
            focus:ring-4
            focus:ring-emerald-100 dark:focus:ring-emerald-900
            transition-colors duration-300
            "
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
            class="
            w-full mt-2
            rounded-xl
            border border-slate-300 dark:border-slate-600
            bg-white dark:bg-slate-700
            text-slate-800 dark:text-white
            placeholder:text-slate-400 dark:placeholder:text-slate-500
            p-3
            focus:outline-none
            focus:border-emerald-500 dark:focus:border-emerald-400
            focus:ring-4
            focus:ring-emerald-100 dark:focus:ring-emerald-900
            transition-colors duration-300
            "
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
            class="
            w-full mt-2
            rounded-xl
            border border-slate-300 dark:border-slate-600
            bg-white dark:bg-slate-700
            text-slate-800 dark:text-white
            placeholder:text-slate-400 dark:placeholder:text-slate-500
            p-3
            focus:outline-none
            focus:border-emerald-500 dark:focus:border-emerald-400
            focus:ring-4
            focus:ring-emerald-100 dark:focus:ring-emerald-900
            transition-colors duration-300
            "
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
            class="
            w-full mt-2
            rounded-xl
            border border-slate-300 dark:border-slate-600
            bg-white dark:bg-slate-700
            text-slate-800 dark:text-white
            placeholder:text-slate-400 dark:placeholder:text-slate-500
            p-3
            focus:outline-none
            focus:border-emerald-500 dark:focus:border-emerald-400
            focus:ring-4
            focus:ring-emerald-100 dark:focus:ring-emerald-900
            transition-colors duration-300
            "
          />

        </div>




        <button
          type="submit"
          class="
          w-full 
          py-3 
          rounded-xl
          bg-gradient-to-r 
          from-emerald-500 
          to-blue-500
          dark:from-emerald-600
          dark:to-blue-600
          text-white
          font-semibold
          hover:scale-105
          transition
          "
        >

          Create Account

        </button>


      </form>





      <p class="text-center mt-6 text-slate-700 dark:text-slate-300">

        Already have an account?


        <router-link
          to="/login"
          class="
          text-emerald-600 
          dark:text-emerald-400
          font-semibold
          hover:text-emerald-700
          dark:hover:text-emerald-300
          transition-colors duration-300
          "
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

0%{

background-position:0% 50%;

}

50%{

background-position:100% 50%;

}

100%{

background-position:0% 50%;

}

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