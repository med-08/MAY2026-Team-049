<template>
  <section class="view on">
    <div class="tiles" style="margin-bottom:18px">
      <TutorStatTile :value="48" label="Sessions this month" icon="<rect x='3' y='4.5' width='18' height='16' rx='2'/>" :active-key="activeKey" :reduce-motion="reduceMotion" />
      <TutorStatTile :value="500" label="Your rate" icon="<path d='M12 3v18M7 8h7a2.5 2.5 0 0 1 0 5H8'/>" :active-key="activeKey" :reduce-motion="reduceMotion"><template #prefix>₹</template><template #suffix><span class="u">/hr</span></template></TutorStatTile>
      <div class="tile glass reveal" data-tilt><div class="ti"><svg viewBox="0 0 24 24"><path d="M4 19V5M4 18h16M8 15l3-4 3 2.5L20 7"/></svg></div><div class="val">₹24k</div><div class="cap">This month</div></div>
      <div class="tile glass reveal" data-tilt><div class="ti"><svg viewBox="0 0 24 24"><path d="M9 11.5 11 13.5l4-4.5"/><circle cx="12" cy="12" r="9"/></svg></div><div class="val" style="color:var(--lime);font-size:24px">Paid</div><div class="cap">Payout status</div></div>
    </div>
    <div class="card glass reveal">
      <div class="ch"><h3>Payout history</h3><span class="lnk">Download slips</span></div>
      <table>
        <thead><tr><th>Month</th><th>Sessions</th><th>Amount</th><th>Status</th></tr></thead>
        <tbody>
          <tr v-for="row in history" :key="row.month"><td>{{ row.month }}</td><td class="mono">{{ row.sessions }}</td><td class="mono">{{ row.amount }}</td><td><span class="badge done">{{ row.status }}</span></td></tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
import TutorStatTile from '../../components/tutor/TutorStatTile.vue'
defineProps({
  history: { type: Array, required: true },
  activeKey: { type: String, required: true },
  reduceMotion: { type: Boolean, required: true }
})
</script>
