<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { CalendarDaysIcon, ClockIcon, VideoCameraIcon } from '@heroicons/vue/24/outline'
import { parentApi } from '../../services/parentApi'
import { useParentPortal } from '../../composables/useParentPortal'
import { useToast } from '../../composables/useToast'

const { parentId, children, loadProfile } = useParentPortal()
const { showToast } = useToast()
const rows = ref([]); const loading = ref(true); const saving = ref(false)
const form = ref({ student_id: '', date: '', start_time: '', end_time: '', reason: '' })
const selectedChild = computed(() => children.value.find(c => String(c.student_id) === String(form.value.student_id)))
function labelStatus(s){ return s.meeting_lifecycle || 'Meeting Not Started' }
async function load(){ if(!parentId.value)return; loading.value=true; try{ const r=await parentApi.getSchedule(parentId.value); rows.value=r.data||[] }catch(e){showToast(e.message||'Unable to load meetings','error')}finally{loading.value=false} }
function reset(){ form.value={ student_id: children.value[0]?.student_id ? String(children.value[0].student_id):'', date:'', start_time:'', end_time:'', reason:'' } }
async function create(){ const f=form.value; if(!f.student_id||!f.date||!f.start_time||!f.end_time||!f.reason.trim()){showToast('Child, date, start time, end time and reason are required.','error');return} saving.value=true; try{await parentApi.createChildMeeting({parent_id:parentId.value,student_id:Number(f.student_id),preferred_date:f.date,preferred_time:f.start_time,preferred_end_time:f.end_time,reason:f.reason});showToast('One-on-one session scheduled. No tutor approval is required.','success');reset();await load()}catch(e){showToast(e.message||'Unable to schedule session','error')}finally{saving.value=false} }
async function start(s){try{const r=await parentApi.startScheduleSession(s.session_id);const url=r.data?.meeting_url||s.meeting_url;if(url)window.open(url,'_blank','noopener,noreferrer');await load();showToast('Meeting started. Your child can join now.','success')}catch(e){showToast(e.message||'Unable to start meeting','error')}}
watch(()=>form.value.student_id,()=>{ if(selectedChild.value){} })
onMounted(async()=>{try{await loadProfile()}catch{};reset();await load()})
</script>
<template><div class="space-y-5">
  <div class="flex items-end justify-between gap-3"><div><h2 class="font-display text-xl font-bold text-slate-800 dark:text-white">Connect with Your Child</h2><p class="mt-1 text-xs text-slate-500">Schedule a private one-on-one session directly with your child. Tutor approval is not involved.</p></div><span class="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-600">{{ rows.length }} sessions</span></div>
  <div class="card p-5"><div class="mb-4"><h3 class="font-display font-semibold">Schedule a one-on-one session</h3><p class="mt-1 text-xs text-slate-500">The child will see the meeting immediately. They can join after you press Start Meeting.</p></div>
    <div class="grid gap-3 md:grid-cols-2 lg:grid-cols-5">
      <div><label class="text-xs font-semibold text-slate-500">Child</label><select v-model="form.student_id" class="input-field mt-1"><option value="" disabled>Select child</option><option v-for="c in children" :key="c.student_id" :value="String(c.student_id)">{{ c.student_name }}</option></select></div>
      <div><label class="text-xs font-semibold text-slate-500">Date</label><input v-model="form.date" type="date" class="input-field mt-1"/></div>
      <div><label class="text-xs font-semibold text-slate-500">Start time</label><input v-model="form.start_time" type="time" class="input-field mt-1"/></div>
      <div><label class="text-xs font-semibold text-slate-500">End time</label><input v-model="form.end_time" type="time" class="input-field mt-1"/></div>
      <div><label class="text-xs font-semibold text-slate-500">Reason</label><input v-model="form.reason" class="input-field mt-1" placeholder="Why are you meeting?"/></div>
    </div>
    <button class="btn-primary mt-4" :disabled="saving" @click="create">{{ saving?'Scheduling...':'Schedule Session' }}</button>
  </div>
  <div v-if="loading" class="card p-8 text-center text-sm text-slate-500">Loading meetings...</div>
  <div v-else-if="!rows.length" class="card border-dashed p-8 text-center text-sm text-slate-500">No parent-created child sessions yet.</div>
  <div v-else class="space-y-2.5"><div v-for="s in rows" :key="s.session_id" class="card flex items-center gap-4 p-4">
    <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-teal-500 text-white"><VideoCameraIcon class="h-5 w-5"/></div>
    <div class="min-w-0 flex-1"><div class="flex flex-wrap items-center gap-2"><span class="font-bold">One-on-One Session</span><span class="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-bold">{{ labelStatus(s) }}</span></div><div class="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500"><span>Created by {{ s.creator_type || 'Parent' }}</span><span>Child: {{s.student_name}}</span><span>Topic: {{s.subject}}</span><span>📅 {{s.date}}</span><span>🕐 {{s.start_time}}–{{s.end_time}}</span></div><p class="mt-1 truncate text-xs text-slate-500">Reason: {{s.meeting_reason || 'Reason not specified'}}</p></div>
    <div class="shrink-0"> <button v-if="s.can_start && s.creator_type !== 'Student'" class="btn-primary" @click="start(s)">Start Meeting</button><a v-else-if="s.can_join && s.creator_type !== 'Student' && s.meeting_url" :href="s.meeting_url" target="_blank" class="btn-primary">Join Meeting</a><span v-else class="rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-500">Meeting Not Started</span></div>
  </div></div>
</div></template>