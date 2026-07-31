<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import ToastStack from '../ui/ToastStack.vue'
import { globalSearch } from '../../composables/useSearch'

const mobileOpen = ref(false)
const route = useRoute()

watch(
  () => route.name,
  () => {
    mobileOpen.value = false
    globalSearch.value = ''
  }
)
</script>

<template>
  <div class="min-h-screen bg-grad-page-light dark:bg-grad-page-dark transition-colors duration-300">
    <Sidebar :mobile-open="mobileOpen" @close="mobileOpen = false" />
    <div class="lg:pl-64 flex flex-col min-h-screen">
      <Navbar @open-sidebar="mobileOpen = true" />
      <main class="flex-1 p-4 sm:p-6">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
    <ToastStack />
  </div>
</template>

<style scoped>
.page-enter-active, .page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(6px);
}
.page-leave-to {
  opacity: 0;
}
</style>
