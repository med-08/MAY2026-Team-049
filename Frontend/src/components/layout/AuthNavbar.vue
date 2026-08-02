<script setup>
import { ref, onMounted } from "vue"

const isDarkMode = ref(false)

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  document.documentElement.classList.toggle('dark', isDarkMode.value)
  localStorage.setItem('darkMode', isDarkMode.value)
}

// Check for saved dark mode preference on mount
onMounted(() => {
  const savedDarkMode = localStorage.getItem('darkMode') === 'true'
  isDarkMode.value = savedDarkMode
  document.documentElement.classList.toggle('dark', savedDarkMode)
})
</script>

<template>
  <nav class="w-full bg-white dark:bg-slate-900 shadow-sm px-6 py-4 flex justify-between items-center transition-colors duration-300">

    <!-- Logo -->
    <router-link 
      to="/" 
      class="text-2xl font-bold text-emerald-600 dark:text-emerald-400"
    >
      🎓 LearnAtHome
    </router-link>


    <div class="flex gap-4 items-center">

      <!-- Dark Mode Toggle Button -->
      <button
        @click="toggleDarkMode"
        class="p-2 rounded-lg bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-yellow-400 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors duration-300"
        :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
      >
        <span v-if="!isDarkMode" class="text-xl">🌙</span>
        <span v-else class="text-xl">☀️</span>
      </button>

      <router-link
        to="/login"
        class="text-slate-600 dark:text-slate-300 hover:text-emerald-600 dark:hover:text-emerald-400 font-medium transition-colors duration-300"
      >
        Login
      </router-link>


      <router-link
        to="/register"
        class="px-5 py-2 rounded-xl bg-emerald-500 dark:bg-emerald-600 text-white font-semibold hover:bg-emerald-600 dark:hover:bg-emerald-700 transition-colors duration-300"
      >
        Register
      </router-link>

    </div>

  </nav>
</template>

<style scoped>
/* Smooth transitions for dark mode */
nav {
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
}
</style>