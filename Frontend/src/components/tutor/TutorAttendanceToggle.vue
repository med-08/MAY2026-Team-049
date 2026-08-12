<template>
  <div class="toggle" role="radiogroup" :aria-label="`Attendance for ${name}`">
    <span
      class="yes"
      :class="{ on: modelValue === 'Present' }"
      role="radio"
      :aria-checked="modelValue === 'Present'"
      tabindex="0"
      @click="$emit('update:modelValue', 'Present')"
      @keydown.enter.prevent="$emit('update:modelValue', 'Present')"
      @keydown.space.prevent="$emit('update:modelValue', 'Present')"
    >Present</span>
    <span
      class="no"
      :class="{ on: modelValue === 'Absent' }"
      role="radio"
      :aria-checked="modelValue === 'Absent'"
      tabindex="0"
      @click="$emit('update:modelValue', 'Absent')"
      @keydown.enter.prevent="$emit('update:modelValue', 'Absent')"
      @keydown.space.prevent="$emit('update:modelValue', 'Absent')"
    >Absent</span>
  </div>
</template>

<script setup>
defineProps({
  modelValue: { type: String, required: true },
  name: { type: String, default: 'student' }
})

defineEmits(['update:modelValue'])
</script>
