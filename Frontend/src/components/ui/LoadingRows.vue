<script setup>
defineProps({
  rows: { type: Number, default: 5 },
  cols: { type: Number, default: 6 }
})
</script>

<template>
  <tr v-for="r in rows" :key="r">
    <td v-for="c in cols" :key="c" class="px-4 py-3">
      <div class="h-3.5 rounded bg-slate-100 dark:bg-slate-800 animate-pulse" :style="{ width: c === 1 ? '60%' : '85%' }" />
    </td>
  </tr>
</template>
