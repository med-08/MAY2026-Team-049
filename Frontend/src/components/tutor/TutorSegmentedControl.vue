<template>
  <div class="seg" role="tablist">
    <span
      v-for="option in options"
      :key="option"
      :class="{ on: modelValue === option }"
      role="tab"
      :aria-selected="modelValue === option"
      tabindex="0"
      @click="$emit('update:modelValue', option)"
      @keydown.enter.prevent="$emit('update:modelValue', option)"
      @keydown.space.prevent="$emit('update:modelValue', option)"
    >{{ option }}</span>
  </div>
</template>

<script setup>
defineProps({
  options: { type: Array, required: true },
  modelValue: { type: String, required: true }
})

defineEmits(['update:modelValue'])
</script>
