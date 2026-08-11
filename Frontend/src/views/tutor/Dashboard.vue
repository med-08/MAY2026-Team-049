<template>
  <section class="view on">
    <div class="card glass reveal">
      <div class="ch">
        <h3>Today's Overview</h3>
        <span class="eyebrow">priority signals</span>
      </div>

      <div class="overview">
        <button
          v-for="item in overview"
          :key="item.id"
          class="ov magnetic"
          :class="item.tone"
          type="button"
          @click="$emit('navigate', item.go)"
        >
          <div class="num">{{ item.value }}</div>
          <div class="lbl">{{ item.label }}</div>
        </button>
      </div>
    </div>

    <div class="tiles" style="margin-bottom:18px">
      <TutorStatTile
        v-for="stat in stats"
        :key="stat.id"
        :value="stat.value"
        :label="stat.label"
        :icon="stat.icon"
        :spark="stat.spark"
        :active-key="activeKey"
        :reduce-motion="reduceMotion"
      />
    </div>

    <div
      class="grid g2col reveal"
      style="grid-template-columns:1.6fr 1fr"
    >
      <div class="card glass">
        <div class="ch">
          <h3>Today's classes</h3>

          <button
            class="lnk"
            type="button"
            @click="$emit('navigate', 'schedule')"
          >
            Full schedule →
          </button>
        </div>

        <div class="tl">
          <div
            v-for="session in sessions"
            :key="session.sessionId"
            class="ev"
            :class="session.status"
          >
            <div class="dot"></div>

            <div class="tm">
              {{ session.time }}
            </div>

            <div class="bd">
              <div class="t">
                {{ session.subject }} · {{ session.classLevel }}
              </div>

              <div class="s">
                {{ session.summary }}
              </div>
            </div>

            <!--
              Existing functionality is preserved.
              This button already triggers the existing
              "Class started · students notified" behavior.
              Only the visible label has been changed.
            -->
            <button
              v-if="session.action"
              class="btn grad sm magnetic"
              type="button"
              @click="$emit('toast', 'Class started · students notified')"
            >
              Notify Student
            </button>

            <span
              v-else
              class="badge"
              :class="session.status"
            >
              {{ session.badge }}
            </span>
          </div>
        </div>
      </div>

      <div class="card earn glass">
        <div class="ch">
          <h3>This month</h3>

          <button
            class="lnk"
            type="button"
            @click="$emit('navigate', 'earnings')"
          >
            Earnings →
          </button>
        </div>

        <div class="eyebrow">
          Payout · paid
        </div>

        <div
          class="big"
          style="color:var(--lime)"
        >
          ₹24,000
        </div>

        <div
          class="s"
          style="font-size:12.5px;color:var(--muted);margin-top:4px"
        >
          48 sessions · ₹500/hr
        </div>

        <TutorAreaChart
          :data="[42,55,60,52,78,70,92]"
          :active-key="activeKey"
          :reduce-motion="reduceMotion"
        />

        <div
          class="eyebrow"
          style="margin-top:10px"
        >
          Jan — Jun
        </div>
      </div>
    </div>

    <div
      class="card glass reveal"
      style="margin-top:18px"
    >
      <div class="ch">
        <h3>Quick actions</h3>
      </div>

      <div class="qa">
        <button
          v-for="action in quickActions"
          :key="action.view"
          class="qact magnetic"
          type="button"
          @click="$emit('navigate', action.view)"
        >
          <TutorIconSvg :path="action.icon" />

          <div class="t">
            {{ action.title }}
          </div>

          <div class="s">
            {{ action.subtitle }}
          </div>
        </button>
      </div>
    </div>

    <div
      class="grid g2col reveal"
      style="grid-template-columns:1.25fr 1fr;margin-top:18px"
    >
      <div class="card glass">
        <div class="ch">
          <h3>Recent activity</h3>
          <span class="eyebrow">newest first</span>
        </div>

        <div class="mini-list">
          <div
            v-for="activity in activities"
            :key="activity.activityId"
            class="row"
          >
            <span
              class="nd"
              :style="{ background: activity.tone }"
            ></span>

            <div class="g1">
              <div class="t">
                {{ activity.title }}
              </div>

              <div class="s">
                {{ activity.meta }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card glass">
        <div class="ch">
          <h3>Upcoming deadlines</h3>
        </div>

        <div class="mini-list">
          <div
            v-for="deadline in deadlines"
            :key="deadline.deadlineId"
            class="row"
          >
            <div
              class="tm mono"
              style="width:78px;color:var(--muted)"
            >
              {{ deadline.day }}
            </div>

            <div class="g1">
              <div class="t">
                {{ deadline.title }}
              </div>

              <div class="s">
                {{ deadline.meta }}
              </div>
            </div>

            <span
              class="badge"
              :class="deadline.badge"
            >
              {{ deadline.badge === 'done' ? 'Ready' : 'Due' }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div
      class="grid g2col reveal"
      style="grid-template-columns:1fr 1fr;margin-top:18px"
    >
      <div class="card glass">
        <div class="ch">
          <h3>AI suggestions</h3>
          <span class="eyebrow">activity insights</span>
        </div>

        <div
          v-for="item in suggestions"
          :key="item.suggestionId"
          class="row"
        >
          <div class="g1">
            <div class="t">
              {{ item.title }}
            </div>

            <div class="s">
              {{ item.action }}
            </div>
          </div>

          <span class="badge live">
            AI
          </span>
        </div>
      </div>

      <div class="card glass">
        <div class="ch">
          <h3>Upcoming meetings</h3>
        </div>

        <div
          v-for="meeting in meetings"
          :key="meeting.meetingId"
          class="row"
        >
          <div
            class="tm mono"
            style="width:82px;color:var(--muted)"
          >
            {{ meeting.day }}
          </div>

          <div class="g1">
            <div class="t">
              {{ meeting.title }}
            </div>

            <div class="s">
              {{ meeting.time }} · {{ meeting.meta }}
            </div>
          </div>

          <span class="badge meeting">
            Meet
          </span>
        </div>
      </div>
    </div>

    <div
      class="grid g2col reveal"
      style="grid-template-columns:1fr 1fr;margin-top:18px"
    >
      <div class="card glass">
        <div class="ch">
          <h3>Top performing students</h3>
        </div>

        <div
          v-for="row in leaderboard"
          :key="row.studentId"
          class="row"
        >
          <span class="badge live">
            #{{ row.rank }}
          </span>

          <div class="g1">
            <div class="t">
              {{ row.name }}
            </div>

            <div class="s">
              Score {{ row.score }} · Trend {{ row.trend }}
            </div>
          </div>
        </div>
      </div>

      <div class="card glass">
        <div class="ch">
          <h3>Student achievements</h3>
        </div>

        <div class="chips">
          <span
            v-for="item in achievements"
            :key="item.achievementId"
            class="badge done"
          >
            {{ item.label }}
          </span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import TutorAreaChart from '../../components/tutor/TutorAreaChart.vue'
import TutorIconSvg from '../../components/tutor/TutorIconSvg.vue'
import TutorStatTile from '../../components/tutor/TutorStatTile.vue'

defineProps({
  stats: {
    type: Array,
    required: true
  },

  sessions: {
    type: Array,
    required: true
  },

  activeKey: {
    type: String,
    required: true
  },

  reduceMotion: {
    type: Boolean,
    required: true
  },

  overview: {
    type: Array,
    required: true
  },

  activities: {
    type: Array,
    required: true
  },

  deadlines: {
    type: Array,
    required: true
  },

  suggestions: {
    type: Array,
    required: true
  },

  meetings: {
    type: Array,
    required: true
  },

  leaderboard: {
    type: Array,
    required: true
  },

  achievements: {
    type: Array,
    required: true
  }
})

defineEmits([
  'navigate',
  'toast'
])

const quickActions = [
  {
    view: 'attendance',
    title: 'Attendance',
    subtitle: 'Mark & send update',
    icon: '<path d="M9 11.5 11 13.5l4-4.5"/><rect x="3.5" y="4" width="17" height="17" rx="2.5"/>'
  },
  {
    view: 'assignments',
    title: 'New quiz',
    subtitle: 'Create or AI-generate',
    icon: '<path d="M8 3h8l3 3v14H5V4Z"/><path d="M9 12h6"/>'
  },
  {
    view: 'materials',
    title: 'Upload',
    subtitle: 'Share study material',
    icon: '<path d="M12 16V4M7 9l5-5 5 5M5 20h14"/>'
  },
  {
    view: 'messages',
    title: 'Reply',
    subtitle: '2 parent queries',
    icon: '<path d="M4 5h16v10H9l-5 4V5Z"/>'
  }
]
</script>