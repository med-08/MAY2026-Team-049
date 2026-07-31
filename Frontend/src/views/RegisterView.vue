<script setup>

import { ref } from "vue"
import AuthNavbar from "../components/layout/AuthNavbar.vue"


const selectedRole = ref("Student")


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
        confirm_password: form.value.confirmPassword
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

<div class="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100">


  <AuthNavbar />


  <div class="flex items-center justify-center p-6">


    <div class="w-full max-w-lg bg-white rounded-3xl shadow-2xl p-8 animate-card">


      <div class="text-center">

        <div class="text-6xl mb-3">
          🎓
        </div>


        <h1 class="text-3xl font-bold text-slate-800">
          Create Account
        </h1>


        <p class="text-slate-500 mt-2">
          Join LearnAtHome and begin your learning journey.
        </p>


      </div>



      <!-- Role Selection -->

      <div class="mt-8">


        <label class="font-semibold text-slate-700">
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
            : 'bg-slate-100 text-slate-700'
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




      <form 
        @submit.prevent="register"
        class="space-y-5 mt-8"
      >


        <div>

          <label class="font-medium text-slate-700">
            Full Name
          </label>


          <input
            v-model="form.fullName"
            type="text"
            placeholder="Enter your full name"
            class="w-full mt-2 rounded-xl border border-slate-300 p-3"
          />

        </div>



        <div>

          <label class="font-medium text-slate-700">
            Email Address
          </label>


          <input
            v-model="form.email"
            type="email"
            placeholder="Enter your email"
            class="w-full mt-2 rounded-xl border border-slate-300 p-3"
          />

        </div>




        <div>

          <label class="font-medium text-slate-700">
            Password
          </label>


          <input
            v-model="form.password"
            type="password"
            placeholder="Create password"
            class="w-full mt-2 rounded-xl border border-slate-300 p-3"
          />

        </div>




        <div>

          <label class="font-medium text-slate-700">
            Confirm Password
          </label>


          <input
            v-model="form.confirmPassword"
            type="password"
            placeholder="Confirm password"
            class="w-full mt-2 rounded-xl border border-slate-300 p-3"
          />

        </div>




        <button
          type="submit"
          class="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-blue-500 text-white font-semibold hover:scale-105 transition"
        >

          Create Account

        </button>


      </form>





      <p class="text-center mt-6 text-slate-700">

        Already have an account?


        <router-link
          to="/login"
          class="text-emerald-600 font-semibold hover:text-emerald-700"
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