<template>
  <div class="modal-scrim" :class="{ on: open }" @click.self="$emit('cancel')">
    <div class="confirm glass">
      <div class="ch"><h3>{{ title }}</h3></div>
      <p>{{ message }}</p>
      <div style="display:flex;gap:10px;justify-content:flex-end;margin-top:18px">
        <button class="btn sm" type="button" @click="$emit('cancel')">Cancel</button>
        <button class="btn grad sm magnetic" type="button" @click="$emit('confirm')">Confirm</button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  open: { type: Boolean, required: true },
  title: { type: String, default: 'Confirm action' },
  message: { type: String, default: 'This action cannot be undone.' }
})
defineEmits(['cancel', 'confirm'])
</script>
