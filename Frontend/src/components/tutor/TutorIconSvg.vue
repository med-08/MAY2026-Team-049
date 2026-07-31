<template>
  <svg :viewBox="viewBox" v-html="path"></svg>
</template>

<script setup>
defineProps({
  path: { type: String, required: true },
  viewBox: { type: String, default: '0 0 24 24' }
})
</script>
