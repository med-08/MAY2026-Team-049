<script setup>

import { ref } from "vue"
import { useRouter } from "vue-router"
import AuthNavbar from "../components/layout/AuthNavbar.vue"


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


const login = () => {

authError.value = ""

if(selectedRole.value === "Admin"){
  router.push("/admin")
}
else if(selectedRole.value === "Student"){
  router.push("/student")
}
else if(selectedRole.value === "Parent"){
  router.push("/parent")
}
else if(selectedRole.value === "Tutor"){
  router.push("/tutor")
}
else{
  authError.value = `${selectedRole.value} portal is coming soon.`
}

}

</script>



<template>

<div class="min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100">


  <!-- Authentication Navbar -->
  <AuthNavbar />



  <div class="flex items-center justify-center p-6">



    <div class="w-full max-w-md bg-white rounded-3xl shadow-2xl p-8 animate-card">



      <h1 class="text-3xl font-bold text-center text-slate-800">

        Welcome Back 👋

      </h1>



      <p class="text-center text-slate-500 mt-2">

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
          : 'bg-slate-100 text-slate-700'
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


          <label class="font-medium text-slate-700">

            Email Address

          </label>



          <input

            v-model="form.email"

            type="email"

            placeholder="Enter your email"

            class="
            w-full mt-2
            rounded-xl
            border border-slate-300
            bg-white
            text-slate-800
            placeholder:text-slate-400
            p-3
            focus:outline-none
            focus:border-emerald-500
            focus:ring-4
            focus:ring-emerald-100
            "

          />


        </div>






        <!-- Password -->


        <div>


          <label class="font-medium text-slate-700">

            Password

          </label>



          <input

            v-model="form.password"

            type="password"

            placeholder="Enter your password"

            class="
            w-full mt-2
            rounded-xl
            border border-slate-300
            bg-white
            text-slate-800
            placeholder:text-slate-400
            p-3
            focus:outline-none
            focus:border-emerald-500
            focus:ring-4
            focus:ring-emerald-100
            "

          />


        </div>







        <!-- Remember + Forgot -->


        <div class="flex justify-between items-center text-sm">


          <label class="flex items-center text-slate-600">


            <input
              type="checkbox"
              class="mr-2 accent-emerald-500"
            >


            Remember Me


          </label>



          <a
            href="#"
            class="text-emerald-600 hover:text-emerald-700 font-medium"
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
          class="text-center text-sm text-amber-600 font-medium"
        >
          {{ authError }}
        </p>




      </form>








      <p class="text-center mt-6 text-slate-700">


        Don't have an account?



        <router-link

          to="/register"

          class="
          text-emerald-600 
          font-semibold
          hover:text-emerald-700
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
