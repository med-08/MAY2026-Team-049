<script setup>
import { ref, onMounted } from 'vue'
import { parentApi } from '../../services/parentApi'
import { useParentPortal } from '../../composables/useParentPortal'
import { useToast } from '../../composables/useToast'
const { parentId }=useParentPortal(); const {showToast}=useToast(); const rows=ref([]); const loading=ref(true)
function niceTime(t){if(!t)return '';const [h,m]=t.split(':');const x=Number(h);return `${x%12||12}:${m} ${x>=12?'PM':'AM'}`}
// Regular=blue / One-to-One=violet — same convention as the tutor schedule
// and student session pages, applied here for a consistent app-wide look.
function isOneToOne(m){return (m.session_type||m.session_type_label||'').toLowerCase().includes('one')}
function typeBadgeClasses(m){return isOneToOne(m)?'bg-violet-50 text-violet-700 dark:bg-violet-900/20 dark:text-violet-300':'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300'}
function statusBadgeClasses(status){
  const s=(status||'').toLowerCase()
  if(s.includes('started')&&!s.includes('not'))return 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300'
  if(s.includes('completed')||s.includes('ended'))return 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300'
  if(s.includes('pending')||s.includes('awaiting'))return 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300'
  if(s.includes('declined')||s.includes('denied')||s.includes('cancelled'))return 'bg-rose-50 text-rose-700 dark:bg-rose-900/20 dark:text-rose-300'
  if(s.includes('approved')||s.includes('accepted'))return 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300'
  return 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300'
}
async function load(){try{const r=await parentApi.getAllMeetings(parentId.value);rows.value=r.data?.meetings||[]}catch(e){showToast(e.message||'Unable to load meetings','error')}finally{loading.value=false}}
onMounted(load)
</script>
<template><div class="space-y-5"><div><h2 class="font-display text-xl font-bold">All Meetings</h2><p class="mt-1 text-xs text-slate-500">A compact overview of every meeting connected to your family.</p></div><div v-if="loading" class="card p-8 text-center text-sm text-slate-500">Loading...</div><div v-else class="card overflow-hidden"><div v-if="!rows.length" class="p-8 text-center text-sm text-slate-500">No meetings found.</div><div v-else class="divide-y divide-slate-100 dark:divide-slate-800"><div v-for="m in rows" :key="m.meeting_id" class="grid gap-3 p-4 lg:grid-cols-[1.3fr_1.5fr_1.2fr_1fr_1fr_auto] lg:items-center"><div><span class="inline-block rounded-full px-2 py-0.5 text-[11px] font-bold" :class="typeBadgeClasses(m)">{{m.session_type_label}}</span><div class="mt-1 text-[11px] text-slate-500">{{m.meeting_type.replaceAll('_',' ')}}</div></div><div class="min-w-0"><div class="text-sm font-semibold truncate">{{m.topic}}</div><div class="text-xs text-slate-500 truncate">Reason: {{m.reason}}</div></div><div class="text-xs text-slate-500"><div>{{m.created_by_label}}</div><div v-if="m.student_name">Child: {{m.student_name}}</div><div v-if="m.tutor_name">Tutor: {{m.tutor_name}}</div></div><div class="text-xs text-slate-500"><div>📅 {{m.date}}</div><div>🕐 {{niceTime(m.start_time)}}–{{niceTime(m.end_time)}}</div></div><div><span class="rounded-full px-2 py-1 text-[10px] font-bold" :class="statusBadgeClasses(m.meeting_status)">{{m.meeting_status}}</span><div class="mt-1 text-[10px] text-slate-400">Approval: {{m.approval_status}}</div></div><div><button v-if="m.can_join&&m.meeting_url" class="btn-primary whitespace-nowrap" @click="window.open(m.meeting_url,'_blank')">Join</button><span v-else class="text-[11px] font-semibold text-slate-400">Not started</span></div></div></div></div></div></template>