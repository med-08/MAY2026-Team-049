<template>
  <div class="pager">
    <button class="btn sm" type="button" :disabled="page <= 1" @click="$emit('update:page', page - 1)">Prev</button>
    <span class="mono">{{ page }} / {{ totalPages }}</span>
    <button class="btn sm" type="button" :disabled="page >= totalPages" @click="$emit('update:page', page + 1)">Next</button>
  </div>
</template>

<script setup>
defineProps({
  page: { type: Number, required: true },
  totalPages: { type: Number, required: true }
})
defineEmits(['update:page'])
</script>
