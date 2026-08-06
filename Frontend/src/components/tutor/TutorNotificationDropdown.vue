<template>
  <div ref="wrapRef" class="bellwrap">
    <button class="icbtn glass" aria-label="Notifications" :aria-expanded="open" @click.stop="$emit('toggle')">
      <svg viewBox="0 0 24 24"><path d="M6 9a6 6 0 0 1 12 0c0 5 2 6 2 6H4s2-1 2-6ZM10 20a2 2 0 0 0 4 0"/></svg>
      <span v-if="hasUnread" class="pip"></span>
    </button>
    <div class="dd glass" :class="{ on: open }">
      <div class="ddh">Notifications</div>
      <button
        v-for="item in notifications"
        :key="item.notificationId"
        class="ni"
        type="button"
        @click="$emit('select', item)"
      >
        <span class="nd" :style="{ background: item.color }"></span>
        <div>
          <div class="nt">{{ item.title }}</div>
          <div class="ns">{{ item.message }}</div>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'

const props = defineProps({
  open: { type: Boolean, required: true },
  notifications: { type: Array, required: true }
})

const emit = defineEmits(['toggle', 'select', 'close'])
const wrapRef = ref(null)
const hasUnread = computed(() => props.notifications.some((item) => !item.isRead))

function onDocumentClick(event) {
  if (props.open && wrapRef.value && !wrapRef.value.contains(event.target)) emit('close')
}

onMounted(() => document.addEventListener('click', onDocumentClick))
onUnmounted(() => document.removeEventListener('click', onDocumentClick))
</script>
