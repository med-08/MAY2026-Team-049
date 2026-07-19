<template>
  <div class="top">
    <div class="top-intro">
      <button class="icbtn menubtn glass" type="button" aria-label="Open menu" :aria-expanded="mobileOpen" @click="$emit('toggle-menu')">
        <svg viewBox="0 0 24 24" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
      </button>
      <div class="hello">
        <div class="k mono">{{ clockLabel }}</div>
        <h1>{{ title.prefix }}<span class="gr">{{ title.highlight }}</span></h1>
      </div>
    </div>
    <div class="tools">
      <button class="srch glass" type="button" @click="$emit('open-command')">
        <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
        <span class="search-label" style="flex:1;text-align:left">Search</span><span class="kbd">&#8984;K</span>
      </button>
      <TutorNotificationDropdown
        :open="notificationsOpen"
        :notifications="notifications"
        @toggle="$emit('toggle-notifications')"
        @close="$emit('close-notifications')"
        @select="$emit('select-notification', $event)"
      />
      <button class="ava" type="button" aria-label="Tutor account" @click="$emit('open-profile')">AM</button>
    </div>
  </div>
</template>

<script setup>
import TutorNotificationDropdown from './TutorNotificationDropdown.vue'

defineProps({
  title: { type: Object, required: true },
  clockLabel: { type: String, required: true },
  mobileOpen: { type: Boolean, required: true },
  notificationsOpen: { type: Boolean, required: true },
  notifications: { type: Array, required: true }
})

defineEmits(['toggle-menu', 'open-command', 'toggle-notifications', 'close-notifications', 'select-notification', 'open-profile'])
</script>
