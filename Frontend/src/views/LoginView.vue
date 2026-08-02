<script setup>

import { ref } from "vue"
import { useRouter } from "vue-router"
import AuthNavbar from "../components/layout/AuthNavbar.vue"
import { adminApi } from "../services/adminApi"


const router = useRouter()

const selectedRole = ref("Student")

const authError = ref("")


const roles = [

{
name:"Student",
value:"Student",
icon:"🎓"
},

{
name:"Tutor",
value:"Tutor",
icon:"👩‍🏫"
},

{
name:"Parent",
value:"Parent",
icon:"👨‍👩‍👧"
},

{
name:"Admin",
value:"Admin",
icon:"⚙️"
}

]


const form = ref({

email:"",
password:""

})


const login = async () => {
  authError.value = ""
  if (!form.value.email || !form.value.password) {
    authError.value = "Please enter both Email/Username and Password."
    return
  }
  try {
    const data = await adminApi.login(form.value.email, form.value.password)
    localStorage.clear()
    const userRole = data.role || selectedRole.value
    if (data.token) {
      localStorage.setItem('token', data.token)
    }
    localStorage.setItem('user', JSON.stringify({ role: userRole, username: data.username, token: data.token }))
    const roleTarget = userRole.toLowerCase()
    router.push(`/${roleTarget}`)
  } catch (err) {
    authError.value = err.message || "Wrong Password or Email/Username."
  }
}

</script>



<template>

<div class="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 transition-colors duration-300">


  <!-- Authentication Navbar -->
  <AuthNavbar />



  <div class="flex items-center justify-center p-6">



    <div class="w-full max-w-md bg-white dark:bg-slate-800 rounded-3xl shadow-2xl dark:shadow-slate-900/50 p-8 animate-card">



      <h1 class="text-3xl font-bold text-center text-slate-800 dark:text-white">

        Welcome Back 👋

      </h1>



      <p class="text-center text-slate-500 dark:text-slate-400 mt-2">

        Login to LearnAtHome

      </p>





      <!-- Role Selection -->

      <div class="grid grid-cols-2 gap-4 mt-8">


        <button

          v-for="r in roles"

          :key="r.value"

          type="button"

          @click="selectedRole=r.value"

          :class="
          selectedRole===r.value
          ? 'bg-emerald-500 text-white'
          : 'bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300'
          "

          class="
          rounded-xl 
          p-4 
          transition 
          duration-300 
          hover:scale-105
          "

        >


          <div class="text-3xl">

            {{r.icon}}

          </div>



          <div class="mt-2 font-semibold">

            {{r.name}}

          </div>


        </button>


      </div>






      <form 
        @submit.prevent="login"
        class="space-y-5 mt-8"
      >




        <!-- Email -->


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






        <!-- Password -->


        <div>


          <label class="font-medium text-slate-700 dark:text-slate-300">

            Password

          </label>



          <input

            v-model="form.password"

            type="password"

            placeholder="Enter your password"

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







        <!-- Remember + Forgot -->


        <div class="flex justify-between items-center text-sm">


          <label class="flex items-center text-slate-600 dark:text-slate-400">


            <input
              type="checkbox"
              class="mr-2 accent-emerald-500"
            >


            Remember Me


          </label>



          <a
            href="#"
            class="text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 font-medium transition-colors duration-300"
          >

            Forgot Password?

          </a>



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

          Login as {{selectedRole}}

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

          class="
          text-emerald-600 
          dark:text-emerald-400
          font-semibold
          hover:text-emerald-700
          dark:hover:text-emerald-300
          transition-colors duration-300
          "

        >

          Create Account


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

color:#1e293b;

}



input::placeholder{

color:#94a3b8;

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


.max-w-md{

padding:24px;

}


h1{

font-size:2rem;

}


}


</style>