import { ref } from 'vue'

const isDark = ref(false)

function applyTheme() {
  const root = document.documentElement
  if (isDark.value) {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
  localStorage.setItem('learnathome-theme', isDark.value ? 'dark' : 'light')
}

function initTheme() {
  const stored = localStorage.getItem('learnathome-theme')
  if (stored) {
    isDark.value = stored === 'dark'
  } else {
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  applyTheme()
}

function toggleTheme() {
  isDark.value = !isDark.value
  applyTheme()
}

export function useTheme() {
  return { isDark, initTheme, toggleTheme }
}
