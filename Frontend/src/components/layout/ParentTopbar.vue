<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Bars3Icon, BellIcon, SunIcon, MoonIcon } from '@heroicons/vue/24/outline'
import { useTheme } from '../../composables/useTheme'
import { useParentPortal } from '../../composables/useParentPortal'

const emit = defineEmits(['open-sidebar'])
const route = useRoute()
const router = useRouter()
const { isDark, toggleTheme } = useTheme()

const {
  parent,
  parentNotifications,
  unreadNotificationCount,
  loadNotifications,
  markNotificationRead,
  markAllNotificationsRead
} = useParentPortal()

const pageTitle = computed(() => route.meta?.title || 'Dashboard')
const bellOpen = ref(false)
const clockLabel = ref('')
let notificationTimer = null
let clockTimer = null

function formatDateTime(dateStr) {
  return new Date(dateStr).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
}

async function openNotification(n) {
  try { await markNotificationRead(n.notification_id ?? n.id) } catch {}
  bellOpen.value = false
  if (n.action_url) router.push(n.action_url)
}

function updateClock() {
  clockLabel.value = new Date().toLocaleString('en-IN', { weekday: 'short', day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true })
}

onMounted(async () => {
  updateClock()
  clockTimer = window.setInterval(updateClock, 1000)
  await loadNotifications()
  notificationTimer = window.setInterval(loadNotifications, 30000)
})

onUnmounted(() => {
  if (clockTimer) window.clearInterval(clockTimer)
  if (notificationTimer) window.clearInterval(notificationTimer)
})

function goToProfile() {
  bellOpen.value = false
  router.push('/parent/profile')
}
</script>

<template>
  <header class="sticky top-0 z-30 bg-white/80 dark:bg-slate-900/70 backdrop-blur-md border-b border-slate-100 dark:border-slate-800">
    <div class="flex items-center justify-between gap-4 px-4 sm:px-6 h-16">
      <div class="flex items-center gap-3 min-w-0">
        <button class="lg:hidden text-slate-500 dark:text-slate-400" @click="emit('open-sidebar')">
          <Bars3Icon class="w-6 h-6" />
        </button>
        <div class="min-w-0">
          <p class="text-[11px] font-semibold text-brand-blue-600 dark:text-brand-blue-400">{{ clockLabel }}</p>
          <h1 class="font-display font-bold text-slate-800 dark:text-slate-100 leading-tight truncate">
            {{ pageTitle }}
          </h1>
          <p class="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">
            Welcome back, {{ parent?.parent_name?.split(' ')[0] || 'Parent' }} 👋
          </p>
        </div>
      </div>

      <div class="flex items-center gap-3 shrink-0 relative">
        <button
          class="w-9 h-9 rounded-lg flex items-center justify-center bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
          @click="toggleTheme"
          aria-label="Toggle dark mode"
        >
          <SunIcon v-if="isDark" class="w-5 h-5" />
          <MoonIcon v-else class="w-5 h-5" />
        </button>

        <div class="relative">
          <button
            class="relative w-9 h-9 rounded-lg flex items-center justify-center bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700 transition-colors"
            @click="bellOpen = !bellOpen"
            aria-label="Notifications"
          >
            <BellIcon class="w-5 h-5" />
            <span
              v-if="unreadNotificationCount > 0"
              class="absolute -top-1 -right-1 min-w-[18px] h-[18px] px-1 rounded-full bg-rose-500 text-white text-[10px] font-bold flex items-center justify-center"
            >
              {{ unreadNotificationCount }}
            </span>
          </button>

          <transition name="fade">
            <div
              v-if="bellOpen"
              class="absolute right-0 mt-2 w-80 max-h-96 overflow-y-auto card p-2 shadow-soft-lg z-40"
            >
              <div class="flex items-center justify-between px-2 py-1.5">
                <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Notifications</p>
                <button class="text-xs font-semibold text-brand-blue-600 dark:text-brand-blue-400 hover:underline" @click="markAllNotificationsRead">
                  Mark all read
                </button>
              </div>
              <div v-if="parentNotifications.length" class="space-y-1">
                <button
                  v-for="n in parentNotifications"
                  :key="n.id ?? n.notification_id"
                  class="w-full text-left flex items-start gap-2.5 p-2.5 rounded-lg transition-colors"
                  :class="n.is_read ? 'hover:bg-slate-50 dark:hover:bg-slate-800/60' : 'bg-brand-blue-50 dark:bg-brand-blue-500/10 hover:bg-brand-blue-100 dark:hover:bg-brand-blue-500/20'"
                  @click="openNotification(n)"
                >
                  <span class="w-2 h-2 rounded-full mt-1.5 shrink-0" :class="n.is_read ? 'bg-slate-300 dark:bg-slate-600' : 'bg-brand-blue-500'"></span>
                  <span class="min-w-0">
                    <span class="block text-sm font-semibold text-slate-800 dark:text-slate-100 truncate">{{ n.title }}</span>
                    <span class="block text-xs text-slate-500 dark:text-slate-400 mt-0.5">{{ n.message }}</span>
                    <span class="block text-[11px] text-slate-400 mt-1">{{ formatDateTime(n.created_at) }}</span>
                  </span>
                </button>
              </div>
              <p v-else class="text-sm text-slate-400 text-center py-6">You're all caught up</p>
            </div>
          </transition>
        </div>

        <button class="flex items-center gap-2.5" @click="goToProfile">
          <div class="w-9 h-9 rounded-full bg-gradient-to-br from-brand-green-500 via-brand-blue-500 to-brand-purple-500 flex items-center justify-center text-white text-sm font-semibold shadow-soft">
            {{ parent?.parent_name?.charAt(0) || 'P' }}
          </div>
          <span class="text-sm font-semibold text-slate-700 dark:text-slate-200 hidden sm:inline">{{ parent?.parent_name }}</span>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
