import { ref } from 'vue'

const toasts = ref([])
let uid = 0

function showToast(message, type = 'success') {
  const id = ++uid
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }, 3200)
}

function dismissToast(id) {
  toasts.value = toasts.value.filter((t) => t.id !== id)
}

export function useToast() {
  return { toasts, showToast, dismissToast }
}
