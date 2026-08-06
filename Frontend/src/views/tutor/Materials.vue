<template>
  <section class="view on">
    <div class="grid g2col reveal" style="grid-template-columns:1.4fr 1fr">
      <div class="card glass">
        <div class="ch"><h3>Uploaded materials</h3><span class="lnk">by topic</span></div>
        <TutorEmptyState v-if="!resources.length" title="No materials" />
        <div v-for="resource in pagedResources" :key="resource.resourceId" class="row">
          <div class="av" :style="{ background: resource.gradient }"><svg width="16" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" v-html="resource.icon"></svg></div>
          <div class="g1"><div class="t">{{ resource.title }}</div><div class="s">{{ resource.description }}</div></div>
          <button class="btn sm" type="button" @click="$emit('toast', 'Shared with students')">Share</button>
          <button class="btn sm" type="button" @click="$emit('confirm-action', `Delete ${resource.title}?`)">Delete</button>
        </div>
        <TutorPagination v-if="resources.length" v-model:page="page" :total-pages="totalPages" />
      </div>
      <div class="card glass">
        <div class="ch"><h3>Upload material</h3></div>
        <div class="field" style="border-style:dashed;text-align:center;padding:32px 14px;color:var(--muted);margin-bottom:12px">Drop files here or browse</div>
        <label class="lab" for="resource-topic">Subject / topic</label><input id="resource-topic" class="field" style="margin-bottom:12px" placeholder="Maths · Quadratics">
        <div v-if="uploading" class="uploadbar"><i :style="{ width: `${progress}%` }"></i></div>
        <div v-if="uploading" class="eyebrow" style="margin-bottom:10px">Uploading… {{ progress }}%</div>
        <button class="btn grad magnetic" type="button" style="width:100%;justify-content:center" @click="startUpload">Upload &amp; notify students</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'
import TutorEmptyState from '../../components/tutor/TutorEmptyState.vue'
import TutorPagination from '../../components/tutor/TutorPagination.vue'

const props = defineProps({ resources: { type: Array, required: true } })
const emit = defineEmits(['toast', 'confirm-action'])
const page = ref(1)
const progress = ref(0)
const uploading = ref(false)
const pageSize = 3
const totalPages = computed(() => Math.max(1, Math.ceil(props.resources.length / pageSize)))
const pagedResources = computed(() => props.resources.slice((page.value - 1) * pageSize, page.value * pageSize))
function startUpload() {
  if (uploading.value) return
  uploading.value = true
  progress.value = 0
  const steps = [25, 50, 75, 100]
  steps.forEach((step, index) => {
    setTimeout(() => {
      progress.value = step
      if (step === 100) {
        emit('toast', 'Uploaded · students notified')
        setTimeout(() => { uploading.value = false }, 400)
      }
    }, (index + 1) * 350)
  })
}
</script>
