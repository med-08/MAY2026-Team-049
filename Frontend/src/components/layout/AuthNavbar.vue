<template>
  <nav class="w-full bg-white shadow-sm px-6 py-4 flex justify-between items-center">

    <!-- Logo -->
    <router-link 
      to="/" 
      class="text-2xl font-bold text-emerald-600"
    >
      🎓 LearnAtHome
    </router-link>


    <div class="flex gap-4 items-center">

      <router-link
        to="/login"
        class="text-slate-600 hover:text-emerald-600 font-medium"
      >
        Login
      </router-link>


      <router-link
        to="/register"
        class="px-5 py-2 rounded-xl bg-emerald-500 text-white font-semibold hover:bg-emerald-600"
      >
        Register
      </router-link>

    </div>

  </nav>
</template>