<template>
  <section class="view on">
    <div class="grid g2col reveal" style="grid-template-columns:1fr 1fr">
      <div class="card glass">
        <div class="profile-hero">
          <div class="profile-avatar">{{ tutor.initials }}</div>
          <div><h3 style="font-size:20px">{{ tutor.name }}</h3><div class="s" style="font-size:12.5px;color:var(--muted);margin-top:4px">{{ tutor.bio }}</div></div>
        </div>
      </div>
      <div class="card glass">
        <div class="ch"><h3>Teaching profile</h3></div>
        <div class="row"><div class="g1"><div class="t">Experience</div><div class="s">{{ tutor.experience }}</div></div><span class="badge done">{{ tutor.hourlyRate }}</span></div>
        <div class="row"><div class="g1"><div class="t">Education</div><div class="s">{{ tutor.education }}</div></div></div>
        <div class="row"><div class="g1"><div class="t">Availability</div><div class="s">{{ tutor.availability }}</div></div></div>
      </div>
    </div>
    <div class="grid g2col reveal" style="grid-template-columns:1fr 1fr;margin-top:18px">
      <div class="card glass">
        <div class="ch"><h3>Subjects</h3></div>
        <div class="chips"><span v-for="subject in tutor.subjects" :key="subject" class="badge live">{{ subject }}</span></div>
      </div>
      <div class="card glass">
        <div class="ch"><h3>Teaching languages</h3></div>
        <div class="chips"><span v-for="language in tutor.languages" :key="language" class="badge">{{ language }}</span></div>
      </div>
    </div>
    <div class="card glass reveal" style="margin-top:18px">
      <div class="ch"><h3>Certificates</h3></div>
      <div class="chips"><span v-for="certificate in tutor.certificates" :key="certificate" class="badge done">{{ certificate }}</span></div>
    </div>
  </section>
</template>

<script setup>
defineProps({ tutor: { type: Object, required: true } })
</script>
