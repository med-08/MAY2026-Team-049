<template>
  <div class="empty">
    <svg viewBox="0 0 24 24"><path d="M4 6h16v11H8l-4 3.5V6Z"/><path d="M9 10h6M9 14h4"/></svg>
    <div class="t">{{ title }}</div>
    <div class="s">{{ message }}</div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  message: { type: String, default: 'Try adjusting the filters.' }
})
</script>
