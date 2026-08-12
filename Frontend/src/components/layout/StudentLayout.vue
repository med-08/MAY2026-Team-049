<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import Sidebar from "../student/StudentSidebar.vue"
import Topbar from "../student/StudentTopbar.vue"
import LogoutModal from "../student/LogoutModal.vue"
import ToastStack from "../ui/ToastStack.vue"
import { authApi } from "../../services/authApi"

const sidebarOpen = ref(false)
const logoutOpen = ref(false)
const router = useRouter()

async function confirmLogout() {
  try {
    await authApi.logout()
  } catch (err) {
    console.error("Logout failed:", err)
  } finally {
    localStorage.removeItem("user")
    localStorage.removeItem("token")
    localStorage.removeItem("role")
    localStorage.removeItem("user_id")
    localStorage.removeItem("username")
    localStorage.removeItem("parent_id")
    localStorage.removeItem("student_id")
    localStorage.removeItem("tutor_id")
    logoutOpen.value = false
    router.push("/login")
  }
}
</script>

<template>
  <div class="min-h-screen">
    <Sidebar :open="sidebarOpen" @close="sidebarOpen = false" @logout="logoutOpen = true" />

    <div class="lg:pl-72 min-h-screen flex flex-col">
      <Topbar @toggle-sidebar="sidebarOpen = true" />
      <main class="flex-1 px-4 md:px-8 py-6 max-w-[1400px] w-full mx-auto">
        <router-view v-slot="{ Component, route }">
          <Transition name="page" mode="out-in">
            <component :is="Component" :key="route.path" />
          </Transition>
        </router-view>
      </main>
    </div>

    <LogoutModal :open="logoutOpen" @cancel="logoutOpen = false" @confirm="confirmLogout" />
    <ToastStack />
  </div>
</template>

<style scoped>
.page-enter-active, .page-leave-active { transition: opacity .15s ease; }
.page-enter-from, .page-leave-to { opacity: 0; }
</style>