<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import ToastStack from '../ui/ToastStack.vue'
import GlobalSearchModal from './GlobalSearchModal.vue'

const mobileOpen = ref(false)
const searchOpen = ref(false)
const route = useRoute()

// NOTE: resetting/pre-filling the per-page search box (`globalSearch`) now
// happens in the router's beforeEach guard, which runs before this page's
// components mount -- see router/index.js. That's the single source of
// truth so a Quick Search jump (`?q=...`) can't get clobbered by a race
// between this watcher and the destination page reading the value.
watch(
  () => route.name,
  () => {
    mobileOpen.value = false
  }
)

function openSearch() {
  searchOpen.value = true
}

// Cmd/Ctrl+K opens the dashboard-wide Quick Search from anywhere.
function onKeydown(e) {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    searchOpen.value = true
  }
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <div class="min-h-screen bg-grad-page-light dark:bg-grad-page-dark transition-colors duration-300">
    <Sidebar :mobile-open="mobileOpen" @close="mobileOpen = false" />
    <div class="lg:pl-64 flex flex-col min-h-screen">
      <Navbar @open-sidebar="mobileOpen = true" @open-search="openSearch" />
      <main class="flex-1 p-4 sm:p-6">
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
    <ToastStack />
    <GlobalSearchModal :open="searchOpen" @close="searchOpen = false" />
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
