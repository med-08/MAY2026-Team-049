<script setup>
import {ref,onMounted} from 'vue';import PageHeader from '../../components/student/PageHeader.vue';import {studentApi} from '../../services/studentApi'
const tips=ref([]),loading=ref(true),error=ref('');onMounted(async()=>{try{const r=await studentApi.getStudyTips();tips.value=r.data?.studyTips||[]}catch(e){error.value=e.message}finally{loading.value=false}})
</script>
<template><div><PageHeader title="Study Tips" subtitle="Tips recorded by your tutor for you."/><p v-if="loading">Loading tips...</p><p v-else-if="error" class="text-red-500">{{error}}</p><div v-else-if="!tips.length" class="card p-8 text-center text-slate-500">No study tips yet.</div><div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4"><div v-for="t in tips" :key="t.id" class="card p-5"><p class="text-xs text-brand-blue">{{t.subject}}</p><p class="text-sm mt-2">{{t.tip}}</p></div></div></div></template>
