<template>

  <div

    class="landing-page relative min-h-screen overflow-x-hidden bg-[#f8fafc] text-slate-900 transition-colors duration-300 dark:bg-[#07111f] dark:text-white"

  >

    <!-- Background -->

    <div class="pointer-events-none fixed inset-0 overflow-hidden">

      <div class="orb orb-one"></div>

      <div class="orb orb-two"></div>

      <div class="orb orb-three"></div>

      <div class="absolute inset-0 bg-grid opacity-[0.35] dark:opacity-[0.12]"></div>

    </div>

    <!-- Navbar -->

    <nav

      :class="[

        'fixed inset-x-0 top-0 z-50 transition-all duration-300',

        navbarShadow

          ? 'border-b border-slate-200/80 bg-white/90 shadow-[0_10px_35px_rgba(15,23,42,0.07)] backdrop-blur-xl dark:border-white/10 dark:bg-[#07111f]/88'

          : 'bg-transparent'

      ]"

    >

      <div class="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-5 sm:px-6 lg:px-8">

        <router-link to="/" class="group flex items-center gap-3">

          <div

            class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-500 via-cyan-500 to-blue-600 text-white shadow-lg shadow-emerald-500/20 transition-transform duration-300 group-hover:scale-105"

          >

            <AcademicCapIcon class="h-6 w-6" />

          </div>

          <div class="leading-tight">

            <div class="text-[17px] font-black tracking-tight text-slate-950 dark:text-white">

              LearnAtHome

            </div>

            <div class="hidden text-[11px] font-medium text-slate-500 sm:block dark:text-slate-400">

              Coaching management, simplified

            </div>

          </div>

        </router-link>

        <div class="hidden items-center gap-7 text-sm font-semibold text-slate-600 lg:flex dark:text-slate-300">

          <a :class="['nav-link', { active: activeSection === 'features' }]" href="#features">Features</a>

          <a :class="['nav-link', { active: activeSection === 'roles' }]" href="#roles">For Everyone</a>

          <a :class="['nav-link', { active: activeSection === 'workflow' }]" href="#workflow">How it Works</a>

          <a :class="['nav-link', { active: activeSection === 'overview' }]" href="#overview">Platform</a>

        </div>

        <div class="flex items-center gap-2 sm:gap-3">

          <button

            type="button"

            @click="toggleDarkMode"

            class="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 bg-white/80 text-slate-700 shadow-sm transition hover:-translate-y-0.5 hover:bg-white dark:border-white/10 dark:bg-white/5 dark:text-slate-200"

            :title="isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'"

          >

            <SunIcon v-if="isDarkMode" class="theme-icon h-5 w-5" />

            <MoonIcon v-else class="theme-icon h-5 w-5" />

          </button>

          <router-link

            to="/login"

            class="hidden rounded-xl px-4 py-2.5 text-sm font-bold text-slate-700 transition hover:bg-slate-100 sm:inline-flex dark:text-slate-200 dark:hover:bg-white/5"

          >

            Log in

          </router-link>

          <router-link

            to="/register"

            class="inline-flex items-center gap-2 rounded-xl bg-slate-950 px-4 py-2.5 text-sm font-bold text-white shadow-lg shadow-slate-900/15 transition hover:-translate-y-0.5 hover:bg-emerald-600 dark:bg-white dark:text-slate-950 dark:hover:bg-emerald-400"

          >

            Get started

            <ArrowRightIcon class="h-4 w-4" />

          </router-link>

        </div>

      </div>

    </nav>

    <!-- Hero -->

    <main class="relative z-10">

      <section class="relative pb-16 pt-32 sm:pt-36 lg:pb-20 lg:pt-40">

        <div class="mx-auto grid max-w-7xl items-center gap-12 px-5 sm:px-6 lg:grid-cols-[1.02fr_.98fr] lg:px-8">

          <div class="max-w-2xl">

            <div class="hero-badge hero-badge-enter">

              <span class="status-dot"></span>

              Built for Students, Tutors, Parents & Admins

            </div>

            <h1

              class="hero-heading mt-6 max-w-3xl text-[44px] font-black leading-[1.02] tracking-[-0.045em] text-slate-950 sm:text-6xl lg:text-[72px] dark:text-white"

            >

              <span class="hero-line"><span>Manage classes.</span></span>
              <span class="hero-line"><span class="gradient-text">Track learning.</span></span>
              <span class="hero-line"><span>Keep everyone <span class="gradient-text">connected.</span></span></span>

            </h1>

            <p class="hero-copy mt-6 max-w-xl text-[17px] leading-7 text-slate-600 sm:text-lg dark:text-slate-300">

              Schedules, attendance, assignments, study resources, academic progress and parent updates — organized in one connected workspace.

            </p>

            <div class="hero-ctas mt-8 flex flex-col gap-3 sm:flex-row">

              <router-link

                to="/register"

                class="group inline-flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-emerald-500 to-cyan-500 px-6 py-3.5 font-extrabold text-white shadow-[0_14px_30px_rgba(16,185,129,.24)] transition hover:-translate-y-1 hover:shadow-[0_18px_35px_rgba(16,185,129,.30)]"

              >

                Create your account

                <ArrowRightIcon class="h-5 w-5 transition group-hover:translate-x-1" />

              </router-link>

              <a

                href="#overview"

                class="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white/80 px-6 py-3.5 font-extrabold text-slate-800 shadow-sm backdrop-blur transition hover:-translate-y-1 hover:border-slate-300 hover:shadow-md dark:border-white/10 dark:bg-white/5 dark:text-white"

              >

                <PlayCircleIcon class="h-5 w-5" />

                Explore platform

              </a>

            </div>

            <div class="hero-proof mt-8 flex flex-wrap gap-x-6 gap-y-3 text-sm font-semibold text-slate-600 dark:text-slate-300">

              <div class="flex items-center gap-2">

                <CheckCircleIcon class="h-5 w-5 text-emerald-500" />

                Role-based dashboards

              </div>

              <div class="flex items-center gap-2">

                <CheckCircleIcon class="h-5 w-5 text-emerald-500" />

                Parent–tutor communication

              </div>

              <div class="flex items-center gap-2">

                <CheckCircleIcon class="h-5 w-5 text-emerald-500" />

                Academic tracking

              </div>

            </div>

          </div>

          <!-- Product Mockup -->

          <div
              id="overview"
              ref="dashboardWrap"
              class="dashboard-enter relative mx-auto w-full max-w-[650px] lg:mx-0"
              @mousemove="handleDashboardParallax"
              @mouseleave="resetDashboardParallax"
            >

            <div class="absolute -inset-8 rounded-[42px] bg-gradient-to-br from-emerald-400/20 via-cyan-400/10 to-blue-500/20 blur-3xl"></div>

            <div ref="dashboardShell" class="dashboard-shell relative overflow-hidden rounded-[28px] border border-white/70 bg-white/90 p-3 shadow-[0_35px_90px_rgba(15,23,42,.18)] backdrop-blur-2xl dark:border-white/10 dark:bg-[#0b1728]/92">

              <div class="flex items-center justify-between border-b border-slate-100 px-3 pb-3 pt-1 dark:border-white/10">

                <div class="flex items-center gap-2">

                  <span class="h-2.5 w-2.5 rounded-full bg-rose-400"></span>

                  <span class="h-2.5 w-2.5 rounded-full bg-amber-400"></span>

                  <span class="h-2.5 w-2.5 rounded-full bg-emerald-400"></span>

                </div>

                <div class="rounded-lg bg-slate-100 px-3 py-1 text-[10px] font-bold text-slate-500 dark:bg-white/5 dark:text-slate-400">

                  Student Dashboard

                </div>

              </div>

              <div class="grid min-h-[420px] grid-cols-[76px_1fr] sm:grid-cols-[110px_1fr]">

                <aside class="border-r border-slate-100 px-2 py-4 dark:border-white/10">

                  <div class="mb-5 flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500 text-white shadow-lg shadow-emerald-500/20 sm:mx-auto">

                    <AcademicCapIcon class="h-5 w-5" />

                  </div>

                  <div class="space-y-2">

                    <div v-for="item in mockNav" :key="item" class="mock-nav-item">

                      <span class="mock-nav-dot"></span>

                      <span class="hidden sm:inline">{{ item }}</span>

                    </div>

                  </div>

                </aside>

                <div class="p-4 sm:p-5">

                  <div class="flex items-start justify-between gap-4">

                    <div>

                      <div class="text-xs font-bold uppercase tracking-[0.16em] text-emerald-600 dark:text-emerald-400">

                        Welcome back

                      </div>

                      <h3 class="mt-1 text-xl font-black text-slate-950 dark:text-white sm:text-2xl">Your learning overview</h3>

                    </div>

                    <div class="grid h-9 w-9 shrink-0 place-items-center rounded-full bg-gradient-to-br from-blue-500 to-violet-500 text-xs font-black text-white">DS</div>

                  </div>

                  <div class="mt-5 grid grid-cols-2 gap-3 lg:grid-cols-4">

                    <div v-for="(stat, statIndex) in mockStats" :key="stat.label" class="mini-stat-card">

                      <component :is="stat.icon" class="h-5 w-5 text-emerald-500" />

                      <div class="mt-3 text-xl font-black text-slate-950 dark:text-white">{{ animatedStats[statIndex] }}</div>

                      <div class="mt-0.5 text-[10px] font-semibold text-slate-500 dark:text-slate-400">{{ stat.label }}</div>

                    </div>

                  </div>

                  <div class="mt-4 grid gap-4 lg:grid-cols-[1.25fr_.75fr]">

                    <div class="rounded-2xl border border-slate-100 bg-slate-50/80 p-4 dark:border-white/10 dark:bg-white/[0.03]">

                      <div class="flex items-center justify-between">

                        <div>

                          <div class="text-sm font-black text-slate-900 dark:text-white">Academic progress</div>

                          <div class="mt-1 text-[11px] text-slate-500">Performance across subjects</div>

                        </div>

                        <ChartBarIcon class="h-5 w-5 text-blue-500" />

                      </div>

                      <div class="mt-5 flex h-28 items-end gap-2">

                        <div v-for="(height, index) in progressBars" :key="index" class="flex flex-1 items-end">

                          <div

                            class="w-full rounded-t-md bg-gradient-to-t from-emerald-500 to-cyan-400 transition-all duration-700"

                            :style="{ height: chartReady ? `${height}%` : `0%`, transitionDelay: `${index * 90}ms` }"

                          ></div>

                        </div>

                      </div>

                      <div class="mt-2 flex justify-between text-[9px] font-semibold text-slate-400">

                        <span>Math</span><span>Science</span><span>English</span><span>SST</span><span>CS</span>

                      </div>

                    </div>

                    <div class="space-y-3">

                      <div class="next-class-card rounded-2xl border border-slate-100 bg-white p-4 dark:border-white/10 dark:bg-white/[0.03]">

                        <div class="flex items-center gap-3">

                          <div class="grid h-10 w-10 place-items-center rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-300">

                            <CalendarDaysIcon class="h-5 w-5" />

                          </div>

                          <div>

                            <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Next class</div>

                            <div class="text-sm font-black text-slate-900 dark:text-white">Mathematics</div>

                            <div class="text-[10px] text-slate-500">04:30 PM · Today</div>

                          </div>

                        </div>

                      </div>

                      <div class="feedback-card rounded-2xl border border-slate-100 bg-white p-4 dark:border-white/10 dark:bg-white/[0.03]">

                        <div class="flex items-center gap-3">

                          <div class="grid h-10 w-10 place-items-center rounded-xl bg-violet-50 text-violet-600 dark:bg-violet-500/10 dark:text-violet-300">

                            <ChatBubbleLeftRightIcon class="h-5 w-5" />

                          </div>

                          <div>

                            <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">New message</div>

                            <div class="text-sm font-black text-slate-900 dark:text-white">Tutor feedback</div>

                            <div class="text-[10px] text-slate-500">Assignment reviewed</div>

                          </div>

                        </div>

                      </div>

                    </div>

                  </div>

                </div>

              </div>

            </div>

            <div class="floating-card floating-card-left">

              <div class="grid h-9 w-9 place-items-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-300">

                <CheckBadgeIcon class="h-5 w-5" />

              </div>

              <div>

                <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Attendance</div>

                <div class="text-sm font-black text-slate-900 dark:text-white">Present today</div>

              </div>

            </div>

            <div class="floating-card floating-card-right">

              <div class="grid h-9 w-9 place-items-center rounded-xl bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-300">

                <DocumentTextIcon class="h-5 w-5" />

              </div>

              <div>

                <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Study material</div>

                <div class="text-sm font-black text-slate-900 dark:text-white">New notes uploaded</div>

              </div>

            </div>

          </div>

        </div>

      </section>

      <!-- Capability Strip -->

      <section class="pb-10">

        <div class="mx-auto max-w-7xl px-5 sm:px-6 lg:px-8">

          <div class="grid overflow-hidden rounded-3xl border border-slate-200 bg-white/75 shadow-sm backdrop-blur md:grid-cols-4 dark:border-white/10 dark:bg-white/[0.035]">

            <div v-for="capability in capabilityStrip" :key="capability.title" class="capability-item">

              <component :is="capability.icon" class="h-5 w-5 text-emerald-500" />

              <div>

                <div class="text-sm font-black text-slate-900 dark:text-white">{{ capability.title }}</div>

                <div class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">{{ capability.desc }}</div>

              </div>

            </div>

          </div>

        </div>

      </section>

      <!-- Features -->

      <section id="features" class="section-space">

        <div class="mx-auto max-w-7xl px-5 sm:px-6 lg:px-8">

          <div class="grid gap-8 lg:grid-cols-[.82fr_1.18fr] lg:items-end">

            <div>

              <span class="section-label">What you can manage</span>

              <h2 class="section-title mt-4">Everything your learning workflow needs.</h2>

            </div>

            <p class="max-w-2xl text-base leading-7 text-slate-600 lg:justify-self-end dark:text-slate-300">

              Manage the daily work behind coaching — from scheduling classes to sharing resources, reviewing progress and keeping parents informed.

            </p>

          </div>

          <div class="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-3">

            <article
              v-for="(feature, index) in features"
              :key="feature.title"
              :class="['feature-card', 'reveal-card', feature.accent]"
              :style="{ '--reveal-delay': `${index * 85}ms` }"
            >
              <span class="feature-glow feature-glow-a"></span>
              <span class="feature-glow feature-glow-b"></span>
              <span class="feature-spark feature-spark-a"></span>
              <span class="feature-spark feature-spark-b"></span>

              <div class="relative z-10">
                <div class="feature-icon">
                  <component :is="feature.icon" class="h-6 w-6 feature-icon-svg" />
                </div>

                <div class="mt-5 text-lg font-black text-slate-950 dark:text-white">{{ feature.title }}</div>

                <p class="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{{ feature.desc }}</p>

                <div class="mt-5 flex flex-wrap gap-2">
                  <span v-for="tag in feature.tags" :key="tag" class="feature-tag">{{ tag }}</span>
                </div>

                <div class="feature-visual mt-5" aria-hidden="true">
                  <span></span><span></span><span></span><span></span>
                </div>
              </div>
            </article>

          </div>

        </div>

      </section>

      <!-- Role tabs/cards -->

      <section id="roles" class="section-space pt-4 reveal-section">

        <div class="mx-auto max-w-7xl px-5 sm:px-6 lg:px-8">

          <div class="role-showcase rounded-[34px] border border-slate-200 bg-slate-950 p-6 shadow-2xl shadow-slate-950/10 sm:p-8 lg:p-10 dark:border-white/10 dark:bg-[#0a1524]">

            <div class="grid gap-8 lg:grid-cols-[.76fr_1.24fr] lg:items-center">

              <div>

                <span class="inline-flex rounded-full bg-white/10 px-3 py-1.5 text-xs font-black uppercase tracking-[0.16em] text-cyan-300">
                  Role-based experience
                </span>

                <h2 class="mt-5 text-3xl font-black tracking-tight text-white sm:text-4xl">
                  One platform. Four focused dashboards.
                </h2>

                <p class="mt-4 max-w-xl text-sm leading-6 text-slate-300">
                  Students, tutors, parents and administrators do not need the same interface. LearnAtHome keeps each workspace focused on the actions that role actually performs.
                </p>

                <div class="role-tabs mt-7 flex flex-wrap gap-2">

                  <button
                    v-for="(role, index) in roles"
                    :key="role.title"
                    type="button"
                    @click="selectRole(index)"
                    :class="[
                      'role-tab rounded-xl px-4 py-2 text-sm font-extrabold transition',
                      activeRole === index
                        ? 'is-active bg-white text-slate-950 shadow-lg'
                        : 'bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white'
                    ]"
                  >
                    {{ role.title }}
                  </button>

                </div>

              </div>

              <div class="role-panel-wrap rounded-[26px] border border-white/10 bg-white/[0.055] p-5 sm:p-6">
                <Transition name="role-swap" mode="out-in">
                  <div :key="activeRole" class="role-panel">

                    <div class="flex items-center gap-4">

                      <div :class="['grid h-12 w-12 place-items-center rounded-2xl bg-gradient-to-br text-white shadow-lg', activeRoleData.color]">
                        <component :is="activeRoleData.icon" class="h-6 w-6" />
                      </div>

                      <div>
                        <div class="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">{{ activeRoleData.title }} dashboard</div>
                        <div class="mt-1 text-xl font-black text-white">{{ activeRoleData.heading }}</div>
                      </div>

                    </div>

                    <div class="mt-6 grid gap-3 sm:grid-cols-2">

                      <div
                        v-for="item in activeRoleData.points"
                        :key="item"
                        class="flex gap-3 rounded-2xl border border-white/10 bg-black/10 p-4"
                      >
                        <CheckCircleIcon class="mt-0.5 h-5 w-5 shrink-0 text-emerald-400" />
                        <span class="text-sm font-semibold leading-6 text-slate-200">{{ item }}</span>
                      </div>

                    </div>

                  </div>
                </Transition>
              </div>

            </div>

          </div>

        </div>

      </section>

      <!-- Workflow -->

      <section id="workflow" class="section-space">

        <div class="mx-auto max-w-7xl px-5 sm:px-6 lg:px-8">

          <div class="mx-auto max-w-3xl text-center">

            <span class="section-label">Simple workflow</span>

            <h2 class="section-title mt-4">How learning moves through LearnAtHome</h2>

            <p class="mt-4 text-base leading-7 text-slate-600 dark:text-slate-300">

              Plan the session, give students what they need, track their progress and keep parents informed — without switching between disconnected tools.

            </p>

          </div>

          <div ref="workflowSection" class="workflow-grid relative mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-4">

            <div class="workflow-line absolute left-[12%] right-[12%] top-8 hidden h-px lg:block"></div>

            <div v-for="(step, index) in workflow" :key="step.title" class="workflow-card reveal-workflow" :style="{ '--step-delay': `${index * 140}ms` }">

              <div class="relative z-10 flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-950 text-white shadow-lg dark:bg-white dark:text-slate-950">

                <component :is="step.icon" class="h-6 w-6" />

              </div>

              <div class="mt-5 text-[11px] font-black uppercase tracking-[0.18em] text-emerald-600 dark:text-emerald-400">Step {{ index + 1 }}</div>

              <div class="mt-1 text-lg font-black text-slate-950 dark:text-white">{{ step.title }}</div>

              <p class="mt-2 text-sm leading-6 text-slate-600 dark:text-slate-300">{{ step.desc }}</p>

            </div>

          </div>

        </div>

      </section>

      <!-- Outcome section -->

      <section class="section-space pt-4">

        <div class="mx-auto max-w-7xl px-5 sm:px-6 lg:px-8">

          <div class="grid overflow-hidden rounded-[34px] border border-slate-200 bg-white shadow-xl shadow-slate-900/5 lg:grid-cols-2 dark:border-white/10 dark:bg-white/[0.035]">

            <div class="p-7 sm:p-9 lg:p-11">

              <span class="section-label">Built for daily use</span>

              <h2 class="mt-4 text-3xl font-black tracking-tight text-slate-950 sm:text-4xl dark:text-white">

                Less chasing. More visibility.

              </h2>

              <p class="mt-4 max-w-xl text-sm leading-7 text-slate-600 dark:text-slate-300">

                Schedules, attendance, assignments, learning resources and tutor updates stay attached to the same student journey — so everyone sees the information they need without repeated follow-ups.

              </p>

              <div class="mt-7 space-y-4">

                <div v-for="benefit in benefits" :key="benefit.title" class="flex gap-4">

                  <div class="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-300">

                    <component :is="benefit.icon" class="h-5 w-5" />

                  </div>

                  <div>

                    <div class="text-sm font-black text-slate-950 dark:text-white">{{ benefit.title }}</div>

                    <div class="mt-1 text-sm leading-6 text-slate-500 dark:text-slate-400">{{ benefit.desc }}</div>

                  </div>

                </div>

              </div>

            </div>

            <div class="relative min-h-[390px] overflow-hidden bg-gradient-to-br from-emerald-500 via-cyan-500 to-blue-600 p-7 sm:p-9 lg:p-11">

              <div class="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-white/20 blur-3xl"></div>

              <div class="absolute -bottom-20 -left-16 h-64 w-64 rounded-full bg-blue-900/25 blur-3xl"></div>

              <div ref="parentSummary" class="parent-summary relative mx-auto max-w-md rounded-[26px] border border-white/20 bg-white/12 p-5 shadow-2xl backdrop-blur-xl">

                <div class="flex items-center justify-between text-white">

                  <div>

                    <div class="text-xs font-bold uppercase tracking-[0.15em] text-white/70">Parent view</div>

                    <div class="mt-1 text-xl font-black">Weekly learning summary</div>

                  </div>

                  <UserGroupIcon class="h-7 w-7" />

                </div>

                <div class="mt-5 grid grid-cols-2 gap-3">

                  <div class="rounded-2xl bg-white p-4 text-slate-950">

                    <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">Attendance</div>

                    <div class="mt-2 text-2xl font-black">{{ parentAttendance }}%</div>

                    <div class="mt-1 text-xs font-semibold text-emerald-600">Good consistency</div>

                  </div>

                  <div class="rounded-2xl bg-white p-4 text-slate-950">

                    <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">Assignments</div>

                    <div class="mt-2 text-2xl font-black">{{ parentAssignments }}/10</div>

                    <div class="pending-label mt-1 text-xs font-semibold text-blue-600">2 pending</div>

                  </div>

                </div>

                <div class="mt-3 rounded-2xl bg-white p-4">

                  <div class="flex items-center justify-between">

                    <div>

                      <div class="text-[10px] font-black uppercase tracking-wider text-slate-400">Tutor update</div>

                      <div class="mt-1 text-sm font-black text-slate-900">Improving steadily in Mathematics</div>

                    </div>

                    <ChatBubbleLeftRightIcon class="h-5 w-5 text-violet-500" />

                  </div>

                  <div class="mt-4 h-2 overflow-hidden rounded-full bg-slate-100">

                    <div class="parent-progress h-full rounded-full bg-gradient-to-r from-violet-500 to-blue-500" :style="{ width: parentSummaryReady ? `78%` : `0%` }"></div>

                  </div>

                </div>

              </div>

            </div>

          </div>

        </div>

      </section>

      <!-- CTA -->

      <section class="pb-20 pt-10 sm:pb-24">

        <div class="mx-auto max-w-7xl px-5 sm:px-6 lg:px-8">

          <div class="relative overflow-hidden rounded-[34px] bg-slate-950 px-6 py-12 text-center shadow-2xl sm:px-10 lg:py-16 dark:border dark:border-white/10">

            <div class="absolute left-1/2 top-0 h-52 w-[70%] -translate-x-1/2 rounded-full bg-emerald-500/20 blur-[90px]"></div>

            <div class="relative">

              <span class="inline-flex rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-black uppercase tracking-[0.16em] text-emerald-300">Start organized</span>

              <h2 class="mx-auto mt-5 max-w-3xl text-3xl font-black tracking-tight text-white sm:text-5xl">

                Your classes, students and progress. Finally connected.

              </h2>

              <p class="mx-auto mt-4 max-w-2xl text-sm leading-7 text-slate-300 sm:text-base">

                Create your LearnAtHome account and open the dashboard built for your role — Student, Tutor, Parent or Admin.

              </p>

              <div class="mt-8 flex flex-col justify-center gap-3 sm:flex-row">

                <router-link

                  to="/register"

                  class="inline-flex items-center justify-center gap-2 rounded-2xl bg-white px-6 py-3.5 font-extrabold text-slate-950 transition hover:-translate-y-1 hover:bg-emerald-300"

                >

                  Create your account

                  <ArrowRightIcon class="h-5 w-5" />

                </router-link>

                <router-link

                  to="/login"

                  class="inline-flex items-center justify-center rounded-2xl border border-white/15 bg-white/5 px-6 py-3.5 font-extrabold text-white transition hover:-translate-y-1 hover:bg-white/10"

                >

                  Log in

                </router-link>

              </div>

            </div>

          </div>

        </div>

      </section>

    </main>

    <!-- Footer -->

    <footer class="relative z-10 border-t border-slate-200 bg-white/70 py-8 backdrop-blur dark:border-white/10 dark:bg-[#07111f]/80">

      <div class="mx-auto flex max-w-7xl flex-col gap-5 px-5 sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8">

        <div>

          <div class="flex items-center gap-2 text-base font-black text-slate-950 dark:text-white">

            <AcademicCapIcon class="h-5 w-5 text-emerald-500" />

            LearnAtHome

          </div>

          <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">

            Coaching management for students, tutors, parents and administrators.

          </p>

        </div>

        <div class="flex flex-wrap gap-x-5 gap-y-2 text-xs font-bold text-slate-500 dark:text-slate-400">

          <a href="#features" class="footer-link">Features</a>

          <a href="#roles" class="footer-link">Roles</a>

          <a href="#workflow" class="footer-link">Workflow</a>

          <router-link to="/login" class="footer-link">Login</router-link>

          <router-link to="/register" class="footer-link">Register</router-link>

        </div>

      </div>

    </footer>

  </div>

</template>

<script setup>

import { computed, onMounted, onUnmounted, ref } from 'vue'

import {

  AcademicCapIcon,

  ArrowRightIcon,

  BookOpenIcon,

  CalendarDaysIcon,

  ChartBarIcon,

  ChatBubbleLeftRightIcon,

  CheckBadgeIcon,

  CheckCircleIcon,

  ClipboardDocumentCheckIcon,

  ClipboardDocumentListIcon,

  DocumentTextIcon,

  FolderOpenIcon,

  MoonIcon,

  PlayCircleIcon,

  PresentationChartLineIcon,

  ShieldCheckIcon,

  SunIcon,

  UserGroupIcon,

  UsersIcon

} from '@heroicons/vue/24/outline'

const isDarkMode = ref(false)

const navbarShadow = ref(false)
const activeSection = ref('overview')

const activeRole = ref(0)

const dashboardWrap = ref(null)
const dashboardShell = ref(null)
const workflowSection = ref(null)
const parentSummary = ref(null)

const animatedStats = ref(['0%', '00', '00', '00'])
const chartReady = ref(false)
const parentAttendance = ref(0)
const parentAssignments = ref(0)
const parentSummaryReady = ref(false)

let revealObserver
let workflowObserver
let parentObserver
let rafId = 0

const selectRole = (index) => {
  if (index === activeRole.value) return
  activeRole.value = index
}

const animateNumber = (from, to, duration, update) => {
  const start = performance.now()
  const tick = (now) => {
    const progress = Math.min((now - start) / duration, 1)
    const eased = 1 - Math.pow(1 - progress, 3)
    update(Math.round(from + (to - from) * eased))
    if (progress < 1) requestAnimationFrame(tick)
  }
  requestAnimationFrame(tick)
}

const startDashboardAnimation = () => {
  animateNumber(0, 92, 900, value => { animatedStats.value[0] = `${value}%` })
  animateNumber(0, 8, 720, value => { animatedStats.value[1] = String(value).padStart(2, '0') })
  animateNumber(0, 24, 820, value => { animatedStats.value[2] = String(value).padStart(2, '0') })
  animateNumber(0, 5, 680, value => { animatedStats.value[3] = String(value).padStart(2, '0') })
  setTimeout(() => { chartReady.value = true }, 380)
}

const startParentSummaryAnimation = () => {
  if (parentSummaryReady.value) return
  parentSummaryReady.value = true
  animateNumber(0, 92, 850, value => { parentAttendance.value = value })
  setTimeout(() => {
    animateNumber(0, 8, 620, value => { parentAssignments.value = value })
  }, 180)
}

const handleDashboardParallax = (event) => {
  if (!dashboardShell.value || window.matchMedia('(pointer: coarse)').matches || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
  cancelAnimationFrame(rafId)
  rafId = requestAnimationFrame(() => {
    const rect = dashboardWrap.value.getBoundingClientRect()
    const x = (event.clientX - rect.left) / rect.width - 0.5
    const y = (event.clientY - rect.top) / rect.height - 0.5
    dashboardShell.value.style.transform = `perspective(1200px) rotateX(${-y * 1.2}deg) rotateY(${x * 1.2}deg) translate3d(${x * 4}px, ${y * 4}px, 0)`
  })
}

const resetDashboardParallax = () => {
  if (!dashboardShell.value) return
  dashboardShell.value.style.transform = ''
}


const mockNav = ['Overview', 'Classes', 'Tasks', 'Progress']

const progressBars = [72, 88, 64, 79, 91]

const mockStats = [

  { label: 'Attendance', value: '92%', icon: CheckBadgeIcon },

  { label: 'Assignments', value: '08', icon: ClipboardDocumentCheckIcon },

  { label: 'Materials', value: '24', icon: FolderOpenIcon },

  { label: 'Subjects', value: '05', icon: BookOpenIcon }

]

const capabilityStrip = [

  { title: 'Scheduling', desc: 'Classes & weekly timetable', icon: CalendarDaysIcon },

  { title: 'Attendance', desc: 'Track class participation', icon: CheckBadgeIcon },

  { title: 'Assignments', desc: 'Share, submit & review', icon: ClipboardDocumentCheckIcon },

  { title: 'Progress', desc: 'Academic performance view', icon: ChartBarIcon }

]

const features = [
  {
    title: 'Student Management',
    icon: AcademicCapIcon,
    desc: 'Profiles, attendance, academic activity and student progress stay connected in one record.',
    tags: ['Profiles', 'Attendance', 'Progress'],
    accent: 'feature-cyan'
  },
  {
    title: 'Tutor Workspace',
    icon: PresentationChartLineIcon,
    desc: "Plan sessions, upload resources, review assignments and monitor each student's learning progress.",
    tags: ['Classes', 'Resources', 'Performance'],
    accent: 'feature-violet'
  },
  {
    title: 'Parent Visibility',
    icon: UserGroupIcon,
    desc: 'Parents can check attendance, marks, upcoming classes, tutor feedback and learning updates without chasing messages.',
    tags: ['Attendance', 'Marks', 'Messages'],
    accent: 'feature-rose'
  },
  {
    title: 'Smart Class Scheduling',
    icon: CalendarDaysIcon,
    desc: 'Create sessions and weekly timetables so tutors and students always know what is coming next.',
    tags: ['Timetable', 'Sessions', 'Planning'],
    accent: 'feature-emerald'
  },
  {
    title: 'Study Materials & Tasks',
    icon: DocumentTextIcon,
    desc: 'Share notes, resources, quizzes and assignments directly with the students who need them.',
    tags: ['Notes', 'Assignments', 'Quizzes'],
    accent: 'feature-amber'
  },
  {
    title: 'Academic Analytics',
    icon: ChartBarIcon,
    desc: 'Turn attendance and performance data into clear progress views for tutors, students and parents.',
    tags: ['Insights', 'Trends', 'Tracking'],
    accent: 'feature-blue'
  },
  {
    title: 'Connected Communication',
    icon: ChatBubbleLeftRightIcon,
    desc: 'Keep tutor feedback, parent conversations and student learning updates connected to the same workspace.',
    tags: ['Messages', 'Feedback', 'Updates'],
    accent: 'feature-purple'
  },
  {
    title: 'Admin Control',
    icon: ShieldCheckIcon,
    desc: 'Manage users, roles and platform activity from one dedicated administration dashboard.',
    tags: ['Users', 'Control', 'Oversight'],
    accent: 'feature-teal'
  },
  {
    title: 'Role-Based Experience',
    icon: UsersIcon,
    desc: 'Students, tutors, parents and admins each see the tools and information relevant to their role.',
    tags: ['Student', 'Tutor', 'Parent', 'Admin'],
    accent: 'feature-indigo'
  }
]

const roles = [

  {

    title: 'Student',

    icon: AcademicCapIcon,

    color: 'from-cyan-500 to-blue-600',

    heading: 'Everything needed to stay on track.',

    points: [

      'Access study material and learning resources',

      'View classes and weekly schedules',

      'Submit assignments and track academic progress',

      'See attendance and tutor updates'

    ]

  },

  {

    title: 'Tutor',

    icon: PresentationChartLineIcon,

    color: 'from-violet-500 to-indigo-600',

    heading: 'Teach, organize and follow progress.',

    points: [

      'Manage students and class schedules',

      'Upload notes, assignments and learning resources',

      'Review academic performance and attendance',

      'Communicate with students and parents'

    ]

  },

  {

    title: 'Parent',

    icon: UserGroupIcon,

    color: 'from-pink-500 to-violet-600',

    heading: 'Stay informed without chasing updates.',

    points: [

      'Monitor attendance and academic results',

      'Check upcoming classes and schedules',

      'Review learning progress in one place',

      'Communicate directly with tutors'

    ]

  },

  {

    title: 'Admin',

    icon: ShieldCheckIcon,

    color: 'from-emerald-500 to-teal-600',

    heading: 'Keep the whole platform organized.',

    points: [

      'Manage students, tutors and parent accounts',

      'Oversee platform activity and records',

      'Maintain structured access across user roles',

      'View operational and academic information centrally'

    ]

  }

]

const activeRoleData = computed(() => roles[activeRole.value])

const workflow = [

  {

    title: 'Plan the class',

    icon: CalendarDaysIcon,

    desc: 'Tutors organize sessions and schedules so students know what is coming next.'

  },

  {

    title: 'Learn & submit',

    icon: ClipboardDocumentListIcon,

    desc: 'Students access resources, attend classes and complete assigned work.'

  },

  {

    title: 'Track progress',

    icon: ChartBarIcon,

    desc: 'Attendance and academic performance stay connected to the student profile.'

  },

  {

    title: 'Keep parents updated',

    icon: ChatBubbleLeftRightIcon,

    desc: 'Parents can review progress and communicate with tutors from the same platform.'

  }

]

const benefits = [

  {

    title: 'Clearer daily operations',

    desc: 'Schedules, student work, attendance and materials stay connected instead of scattered.',

    icon: ClipboardDocumentCheckIcon

  },

  {

    title: 'Better communication',

    desc: 'Important learning updates remain visible to the people who need them.',

    icon: ChatBubbleLeftRightIcon

  },

  {

    title: 'More useful progress tracking',

    desc: 'Students and parents can see academic activity through a structured dashboard.',

    icon: ChartBarIcon

  }

]

const toggleDarkMode = () => {

  isDarkMode.value = !isDarkMode.value

  document.documentElement.classList.toggle('dark', isDarkMode.value)

  localStorage.setItem('darkMode', String(isDarkMode.value))

}

const onScroll = () => {
  navbarShadow.value = window.scrollY > 16

  const sections = ['overview', 'features', 'roles', 'workflow']
  let current = 'overview'
  for (const id of sections) {
    const el = document.getElementById(id)
    if (el && el.getBoundingClientRect().top <= 180) current = id
  }
  activeSection.value = current
}

onMounted(() => {
  const stored = localStorage.getItem('darkMode')
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches
  const shouldUseDark = stored === null ? prefersDark : stored === 'true'

  isDarkMode.value = shouldUseDark
  document.documentElement.classList.toggle('dark', shouldUseDark)
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

  if (reduceMotion) {
    document.querySelectorAll('.reveal-card, .reveal-workflow').forEach(el => el.classList.add('is-visible'))
    chartReady.value = true
    animatedStats.value = ['92%', '08', '24', '05']
    parentAttendance.value = 92
    parentAssignments.value = 8
    parentSummaryReady.value = true
    return
  }

  setTimeout(startDashboardAnimation, 650)

  revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return
      entry.target.classList.add('is-visible')
      revealObserver.unobserve(entry.target)
    })
  }, { threshold: 0.18 })

  document.querySelectorAll('.reveal-card').forEach(el => revealObserver.observe(el))

  workflowObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return
      entry.target.classList.add('workflow-active')
      entry.target.querySelectorAll('.reveal-workflow').forEach(el => el.classList.add('is-visible'))
      workflowObserver.unobserve(entry.target)
    })
  }, { threshold: 0.2 })

  if (workflowSection.value) workflowObserver.observe(workflowSection.value)

  parentObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return
      startParentSummaryAnimation()
      entry.target.classList.add('summary-active')
      parentObserver.unobserve(entry.target)
    })
  }, { threshold: 0.28 })

  if (parentSummary.value) parentObserver.observe(parentSummary.value)
})

onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  revealObserver?.disconnect()
  workflowObserver?.disconnect()
  parentObserver?.disconnect()
  cancelAnimationFrame(rafId)
})

</script>

<style scoped>

.landing-page {

  isolation: isolate;

}

.section-space {

  padding-top: 72px;

  padding-bottom: 72px;

}

.section-label {

  display: inline-flex;

  align-items: center;

  border-radius: 999px;

  border: 1px solid rgba(16, 185, 129, 0.16);

  background: rgba(16, 185, 129, 0.08);

  padding: 7px 12px;

  font-size: 11px;

  font-weight: 900;

  letter-spacing: 0.14em;

  text-transform: uppercase;

  color: rgb(5 150 105);

}

.dark .section-label {

  border-color: rgba(52, 211, 153, 0.15);

  background: rgba(16, 185, 129, 0.1);

  color: rgb(110 231 183);

}

.section-title {

  max-width: 720px;

  font-size: clamp(2rem, 4vw, 3.5rem);

  line-height: 1.06;

  letter-spacing: -0.04em;

  font-weight: 900;

  color: rgb(15 23 42);

}

.dark .section-title {

  color: white;

}

.nav-link {

  position: relative;

  transition: color 0.2s ease;

}

.nav-link::after {

  content: '';

  position: absolute;

  left: 50%;

  bottom: -8px;

  width: 0;

  height: 2px;

  border-radius: 999px;

  background: rgb(16 185 129);

  transform: translateX(-50%);

  transition: width 0.25s ease;

}

.nav-link:hover {

  color: rgb(5 150 105);

}

.nav-link:hover::after,
.nav-link.active::after {

  width: 75%;

}
.nav-link.active { color: rgb(5 150 105); }
.theme-icon { animation: themeIconIn .35s cubic-bezier(.22,1,.36,1); }
@keyframes themeIconIn { from { opacity:0; transform:rotate(-35deg) scale(.75) } to { opacity:1; transform:none } }

.hero-badge {

  display: inline-flex;

  align-items: center;

  gap: 9px;

  border: 1px solid rgb(226 232 240);

  border-radius: 999px;

  background: rgba(255,255,255,.75);

  padding: 8px 13px;

  font-size: 12px;

  font-weight: 800;

  color: rgb(71 85 105);

  box-shadow: 0 8px 22px rgba(15,23,42,.04);

  backdrop-filter: blur(14px);

}

.dark .hero-badge {

  border-color: rgba(255,255,255,.09);

  background: rgba(255,255,255,.045);

  color: rgb(203 213 225);

}

.status-dot {

  width: 8px;

  height: 8px;

  border-radius: 999px;

  background: rgb(16 185 129);

  box-shadow: 0 0 0 5px rgba(16,185,129,.12);

  animation: softPulse 2.4s ease-in-out infinite;

}

.gradient-text {

  display: inline-block;

  background: linear-gradient(110deg, #10b981, #06b6d4, #3b82f6);

  background-size: 180% 180%;

  -webkit-background-clip: text;

  background-clip: text;

  color: transparent;

  animation: gradientShift 7s ease infinite;

}

.orb {

  position: absolute;

  border-radius: 999px;

  filter: blur(90px);

  opacity: 0.22;

  will-change: transform;

}

.orb-one {

  width: 380px;

  height: 380px;

  top: -120px;

  left: -90px;

  background: #34d399;

  animation: orbFloatOne 18s ease-in-out infinite;

}

.orb-two {

  width: 440px;

  height: 440px;

  top: 20%;

  right: -160px;

  background: #60a5fa;

  animation: orbFloatTwo 22s ease-in-out infinite;

}

.orb-three {

  width: 340px;

  height: 340px;

  bottom: 5%;

  left: 30%;

  background: #a78bfa;

  opacity: 0.11;

  animation: orbFloatThree 20s ease-in-out infinite;

}

.bg-grid {

  background-image:

    linear-gradient(rgba(15, 23, 42, 0.035) 1px, transparent 1px),

    linear-gradient(90deg, rgba(15, 23, 42, 0.035) 1px, transparent 1px);

  background-size: 34px 34px;

  mask-image: linear-gradient(to bottom, black 0%, transparent 72%);

}

.dark .bg-grid {

  background-image:

    linear-gradient(rgba(255,255,255,.07) 1px, transparent 1px),

    linear-gradient(90deg, rgba(255,255,255,.07) 1px, transparent 1px);

}

.dashboard-shell {

  animation: dashboardFloat 6s ease-in-out infinite;

}

.mock-nav-item {

  display: flex;

  min-height: 34px;

  align-items: center;

  gap: 8px;

  border-radius: 10px;

  padding: 0 8px;

  font-size: 9px;

  font-weight: 800;

  color: rgb(100 116 139);

}

.mock-nav-item:first-child {

  background: rgba(16,185,129,.08);

  color: rgb(5 150 105);

}

.dark .mock-nav-item {

  color: rgb(148 163 184);

}

.dark .mock-nav-item:first-child {

  background: rgba(16,185,129,.10);

  color: rgb(110 231 183);

}

.mock-nav-dot {

  width: 7px;

  height: 7px;

  border-radius: 999px;

  background: currentColor;

  opacity: .65;

}

.mini-stat-card {

  border: 1px solid rgb(241 245 249);

  border-radius: 15px;

  background: white;

  padding: 12px;

  box-shadow: 0 6px 18px rgba(15,23,42,.035);

}

.dark .mini-stat-card {

  border-color: rgba(255,255,255,.08);

  background: rgba(255,255,255,.035);

}

.floating-card {

  position: absolute;

  z-index: 20;

  display: flex;

  align-items: center;

  gap: 10px;

  border: 1px solid rgba(255,255,255,.8);

  border-radius: 16px;

  background: rgba(255,255,255,.90);

  padding: 10px 12px;

  box-shadow: 0 18px 40px rgba(15,23,42,.12);

  backdrop-filter: blur(16px);

}

.dark .floating-card {

  border-color: rgba(255,255,255,.1);

  background: rgba(11,23,40,.92);

}

.floating-card-left {

  left: -22px;

  bottom: 58px;

  animation: cardFloatOne 5s ease-in-out infinite;

}

.floating-card-right {

  right: -24px;

  top: 84px;

  animation: cardFloatTwo 5.8s ease-in-out infinite;

}

.capability-item {

  display: flex;

  align-items: center;

  gap: 12px;

  padding: 17px 18px;

  border-bottom: 1px solid rgb(226 232 240);

}

.dark .capability-item {

  border-color: rgba(255,255,255,.08);

}

.feature-card {

  position: relative;

  overflow: hidden;

  border: 1px solid rgb(226 232 240);

  border-radius: 22px;

  background: rgba(255,255,255,.80);

  padding: 22px;

  box-shadow: 0 8px 28px rgba(15,23,42,.035);

  backdrop-filter: blur(12px);

  transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;

}

.feature-card::before {

  content: '';

  position: absolute;

  inset: 0;

  background: radial-gradient(circle at top right, rgba(16,185,129,.10), transparent 34%);

  opacity: 0;

  transition: opacity .3s ease;

}

.feature-card:hover {

  transform: translateY(-6px);

  border-color: rgba(16,185,129,.25);

  box-shadow: 0 18px 42px rgba(15,23,42,.08);

}

.feature-card:hover::before {

  opacity: 1;

}

.dark .feature-card {

  border-color: rgba(255,255,255,.08);

  background: rgba(255,255,255,.035);

}

.feature-icon {

  position: relative;

  z-index: 1;

  display: grid;

  width: 46px;

  height: 46px;

  place-items: center;

  border-radius: 14px;

  background: rgba(16,185,129,.09);

  color: rgb(5 150 105);

  transition: transform .3s ease, *background* .3s ease;

}

.feature-card:hover .feature-icon {

  transform: rotate(-4deg) scale(1.06);

  background: rgb(16 185 129);

  color: white;

}

.dark .feature-icon {

  background: rgba(52,211,153,.10);

  color: rgb(110 231 183);

}

.feature-tag {

  border: 1px solid rgb(226 232 240);

  border-radius: 999px;

  background: rgb(248 250 252);

  padding: 5px 8px;

  font-size: 10px;

  font-weight: 800;

  color: rgb(100 116 139);

}

.dark .feature-tag {

  border-color: rgba(255,255,255,.07);

  background: rgba(255,255,255,.04);

  color: rgb(148 163 184);

}

.workflow-card {

  position: relative;

  border: 1px solid rgb(226 232 240);

  border-radius: 22px;

  background: rgba(255,255,255,.75);

  padding: 20px;

  box-shadow: 0 8px 24px rgba(15,23,42,.035);

  backdrop-filter: blur(12px);

}

.dark .workflow-card {

  border-color: rgba(255,255,255,.08);

  background: rgba(255,255,255,.03);

}

.footer-link {

  transition: color .2s ease;

}

.footer-link:hover {

  color: rgb(5 150 105);

}

.reveal-up {

  opacity: 0;

  transform: translateY(16px);

  animation: revealUp .7s cubic-bezier(.2,.7,.2,1) forwards;

}

.delay-1 { animation-delay: .08s; }

.delay-2 { animation-delay: .16s; }

.delay-3 { animation-delay: .24s; }

.delay-4 { animation-delay: .32s; }

@keyframes revealUp {

  to { opacity: 1; transform: translateY(0); }

}

@keyframes gradientShift {

  0%,100% { background-position: 0% 50%; }

  50% { background-position: 100% 50%; }

}

@keyframes softPulse {

  0%,100% { box-shadow: 0 0 0 5px rgba(16,185,129,.10); }

  50% { box-shadow: 0 0 0 8px rgba(16,185,129,.04); }

}

@keyframes dashboardFloat {

  0%,100% { transform: translateY(0); }

  50% { transform: translateY(-7px); }

}

@keyframes cardFloatOne {

  0%,100% { transform: translateY(0) rotate(-1deg); }

  50% { transform: translateY(-9px) rotate(1deg); }

}

@keyframes cardFloatTwo {

  0%,100% { transform: translateY(0) rotate(1deg); }

  50% { transform: translateY(9px) rotate(-1deg); }

}

@keyframes orbFloatOne {

  0%,100% { transform: translate3d(0,0,0) scale(1); }

  50% { transform: translate3d(55px,45px,0) scale(1.08); }

}

@keyframes orbFloatTwo {

  0%,100% { transform: translate3d(0,0,0) scale(1); }

  50% { transform: translate3d(-45px,35px,0) scale(.94); }

}

@keyframes orbFloatThree {

  0%,100% { transform: translate3d(0,0,0) scale(1); }

  50% { transform: translate3d(35px,-45px,0) scale(1.05); }

}

@media (min-width: 768px) {

  .capability-item {

    border-bottom: 0;

    border-right: 1px solid rgb(226 232 240);

  }

  .capability-item:last-child {

    border-right: 0;

  }

  .dark .capability-item {

    border-color: rgba(255,255,255,.08);

  }

}

@media (max-width: 1024px) {

  .floating-card-left {

    left: 10px;

  }

  .floating-card-right {

    right: 10px;

  }

}

@media (max-width: 640px) {

  .section-space {

    padding-top: 56px;

    padding-bottom: 56px;

  }

  .floating-card {

    display: none;

  }

  .dashboard-shell {

    animation: none;

  }

}

@media (prefers-reduced-motion: reduce) {

  *,

  *::before,

  *::after {

    scroll-behavior: auto !important;

    animation-duration: .01ms !important;

    animation-iteration-count: 1 !important;

    transition-duration: .01ms !important;

  }

}


/* =========================================================
   Premium LearnAtHome motion + gradient layer
   ========================================================= */

html { scroll-behavior: smooth; }

nav {
  animation: navEnter .72s cubic-bezier(.22,1,.36,1) both;
}

.hero-badge-enter {
  opacity: 0;
  transform: translateY(12px);
  animation: heroFade .65s .08s cubic-bezier(.22,1,.36,1) forwards;
}

.hero-heading .hero-line {
  display: block;
  overflow: hidden;
  padding-bottom: .04em;
}
.hero-heading .hero-line > span {
  display: block;
  opacity: 0;
  transform: translateY(105%);
  animation: heroLineReveal .8s cubic-bezier(.22,1,.36,1) forwards;
}
.hero-heading .hero-line:nth-child(1) > span { animation-delay: .16s; }
.hero-heading .hero-line:nth-child(2) > span { animation-delay: .26s; }
.hero-heading .hero-line:nth-child(3) > span { animation-delay: .36s; }

.hero-copy,
.hero-ctas,
.hero-proof {
  opacity: 0;
  transform: translateY(18px);
  animation: heroFade .72s cubic-bezier(.22,1,.36,1) forwards;
}
.hero-copy { animation-delay: .48s; }
.hero-ctas { animation-delay: .60s; }
.hero-proof { animation-delay: .70s; }

.dashboard-enter {
  opacity: 0;
  transform: translateX(40px) scale(.96);
  animation: dashboardEnter .86s .30s cubic-bezier(.22,1,.36,1) forwards;
}
.dashboard-shell {
  transform-style: preserve-3d;
  transition: transform .28s cubic-bezier(.22,1,.36,1), box-shadow .35s ease;
  animation: none !important;
}
.dashboard-enter:hover .dashboard-shell {
  box-shadow: 0 42px 105px rgba(15,23,42,.22);
}

.mini-stat-card {
  background:
    linear-gradient(145deg, rgba(255,255,255,.95), rgba(248,250,252,.76)) padding-box,
    linear-gradient(135deg, rgba(6,182,212,.22), rgba(99,102,241,.12), rgba(236,72,153,.12)) border-box;
  border: 1px solid transparent;
  transition: transform .28s cubic-bezier(.22,1,.36,1), box-shadow .28s ease;
}
.mini-stat-card:nth-child(1) { box-shadow: 0 10px 26px rgba(16,185,129,.08); }
.mini-stat-card:nth-child(2) { box-shadow: 0 10px 26px rgba(59,130,246,.08); }
.mini-stat-card:nth-child(3) { box-shadow: 0 10px 26px rgba(139,92,246,.08); }
.mini-stat-card:nth-child(4) { box-shadow: 0 10px 26px rgba(245,158,11,.08); }
.dark .mini-stat-card {
  background:
    linear-gradient(145deg, rgba(15,23,42,.88), rgba(10,20,35,.72)) padding-box,
    linear-gradient(135deg, rgba(34,211,238,.23), rgba(139,92,246,.20), rgba(16,185,129,.14)) border-box;
}
.next-class-card { animation: microSlideLeft .72s .9s cubic-bezier(.22,1,.36,1) both; }
.feedback-card { animation: microSlideRight .72s 1.02s cubic-bezier(.22,1,.36,1) both; }

.floating-card-left { animation: microFloatA 5.4s ease-in-out infinite !important; }
.floating-card-right { animation: microFloatB 6.1s ease-in-out infinite !important; }

/* Feature section */
.feature-card {
  --c1: 6,182,212;
  --c2: 59,130,246;
  --c3: 99,102,241;
  min-height: 286px;
  background:
    linear-gradient(150deg, rgba(var(--c1),.16), rgba(255,255,255,.88) 42%, rgba(var(--c2),.12)),
    rgba(255,255,255,.78);
  border: 1px solid rgba(var(--c1),.22);
  box-shadow:
    0 16px 40px rgba(15,23,42,.06),
    inset 0 1px 0 rgba(255,255,255,.75);
  backdrop-filter: blur(18px);
  transform: translateY(28px);
  opacity: 0;
  transition:
    transform .55s cubic-bezier(.22,1,.36,1),
    opacity .55s cubic-bezier(.22,1,.36,1),
    box-shadow .34s ease,
    border-color .34s ease;
  transition-delay: var(--reveal-delay);
}
.feature-card.is-visible {
  transform: translateY(0);
  opacity: 1;
}
.feature-card:hover {
  transform: translateY(-7px) scale(1.01);
  border-color: rgba(var(--c1),.48);
  box-shadow:
    0 26px 60px rgba(var(--c2),.16),
    0 10px 25px rgba(15,23,42,.08),
    inset 0 1px 0 rgba(255,255,255,.9);
}
.dark .feature-card {
  background:
    radial-gradient(circle at 90% 0%, rgba(var(--c2),.22), transparent 36%),
    linear-gradient(145deg, rgba(var(--c1),.13), rgba(8,18,32,.94) 48%, rgba(var(--c3),.13)),
    rgba(7,17,31,.88);
  border-color: rgba(var(--c1),.22);
  box-shadow: 0 22px 60px rgba(0,0,0,.24), inset 0 1px 0 rgba(255,255,255,.05);
}
.dark .feature-card:hover {
  border-color: rgba(var(--c1),.55);
  box-shadow: 0 28px 70px rgba(var(--c2),.18), 0 12px 30px rgba(0,0,0,.26);
}

.feature-cyan { --c1: 6,182,212; --c2: 59,130,246; --c3: 14,165,233; }
.feature-violet { --c1: 139,92,246; --c2: 79,70,229; --c3: 99,102,241; }
.feature-rose { --c1: 244,63,94; --c2: 168,85,247; --c3: 236,72,153; }
.feature-emerald { --c1: 16,185,129; --c2: 6,182,212; --c3: 20,184,166; }
.feature-amber { --c1: 245,158,11; --c2: 249,115,22; --c3: 251,191,36; }
.feature-blue { --c1: 59,130,246; --c2: 139,92,246; --c3: 99,102,241; }
.feature-purple { --c1: 34,211,238; --c2: 168,85,247; --c3: 236,72,153; }
.feature-teal { --c1: 16,185,129; --c2: 59,130,246; --c3: 20,184,166; }
.feature-indigo { --c1: 99,102,241; --c2: 168,85,247; --c3: 236,72,153; }

.feature-icon {
  background: linear-gradient(135deg, rgba(var(--c1),.96), rgba(var(--c2),.94));
  color: white;
  box-shadow: 0 12px 26px rgba(var(--c1),.24);
}
.feature-card:hover .feature-icon {
  transform: translateY(-2px) rotate(-3deg) scale(1.07);
  box-shadow: 0 16px 36px rgba(var(--c1),.35);
}
.feature-card:nth-child(4) .feature-icon-svg { animation: calendarFlip .44s var(--reveal-delay) cubic-bezier(.22,1,.36,1) both; }
.feature-card:nth-child(6) .feature-icon-svg { transform-origin: bottom; animation: barsGrow .46s var(--reveal-delay) cubic-bezier(.22,1,.36,1) both; }
.feature-card:nth-child(7) .feature-icon-svg { animation: chatReveal .44s var(--reveal-delay) cubic-bezier(.22,1,.36,1) both; }
.feature-card:nth-child(3) .feature-icon-svg { animation: avatarPop .42s var(--reveal-delay) cubic-bezier(.22,1,.36,1) both; }
.feature-card:nth-child(1) .feature-icon-svg { animation: capTilt .42s var(--reveal-delay) cubic-bezier(.22,1,.36,1) both; }

.feature-glow {
  position: absolute;
  border-radius: 999px;
  filter: blur(34px);
  pointer-events: none;
  opacity: .42;
}
.feature-glow-a {
  width: 150px; height: 150px;
  top: -60px; right: -35px;
  background: rgba(var(--c1),.34);
}
.feature-glow-b {
  width: 120px; height: 120px;
  bottom: -50px; left: -35px;
  background: rgba(var(--c2),.24);
}
.feature-spark {
  position: absolute;
  width: 7px; height: 7px;
  border-radius: 999px;
  background: rgba(var(--c1),.72);
  box-shadow: 0 0 16px rgba(var(--c1),.68);
  animation: sparkFloat 4.8s ease-in-out infinite;
}
.feature-spark-a { top: 22px; right: 28px; }
.feature-spark-b { bottom: 56px; right: 48px; animation-delay: -2.1s; transform: scale(.7); }

.feature-tag {
  background: rgba(255,255,255,.56);
  border-color: rgba(var(--c1),.18);
  color: rgb(71 85 105);
  backdrop-filter: blur(12px);
}
.dark .feature-tag {
  background: rgba(255,255,255,.055);
  border-color: rgba(var(--c1),.18);
  color: rgb(203 213 225);
}

.feature-visual {
  display: flex;
  align-items: end;
  gap: 6px;
  height: 24px;
  opacity: .8;
}
.feature-visual span {
  flex: 1;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(var(--c1),.9), rgba(var(--c2),.78));
  transform-origin: left center;
  animation: visualPulse 5.5s ease-in-out infinite;
}
.feature-visual span:nth-child(1){height:6px; animation-delay:-1.2s}
.feature-visual span:nth-child(2){height:10px; animation-delay:-2.5s}
.feature-visual span:nth-child(3){height:7px; animation-delay:-3.6s}
.feature-visual span:nth-child(4){height:13px; animation-delay:-.4s}

/* Roles */
.role-panel-wrap {
  position: relative;
  overflow: hidden;
  background:
    radial-gradient(circle at 100% 0%, rgba(34,211,238,.12), transparent 34%),
    rgba(255,255,255,.055);
}
.role-panel { will-change: transform, opacity; }
.role-swap-enter-active,
.role-swap-leave-active {
  transition: opacity .28s ease, transform .28s cubic-bezier(.22,1,.36,1);
}
.role-swap-enter-from { opacity: 0; transform: translateY(8px); }
.role-swap-leave-to { opacity: 0; transform: translateY(-8px); }

/* Workflow */
.workflow-line {
  background: linear-gradient(90deg, transparent, #22d3ee 18%, #8b5cf6 50%, #10b981 82%, transparent);
  transform: scaleX(0);
  transform-origin: left center;
  opacity: .78;
}
.workflow-active .workflow-line {
  animation: workflowDraw 1.15s cubic-bezier(.22,1,.36,1) forwards;
}
.reveal-workflow {
  opacity: 0;
  transform: translateY(20px);
}
.reveal-workflow.is-visible {
  animation: workflowCardIn .55s var(--step-delay) cubic-bezier(.22,1,.36,1) forwards;
}
.workflow-card {
  transition: transform .3s cubic-bezier(.22,1,.36,1), box-shadow .3s ease, border-color .3s ease;
}
.workflow-card:hover {
  transform: translateY(-5px);
  border-color: rgba(34,211,238,.24);
  box-shadow: 0 18px 42px rgba(15,23,42,.08);
}
.workflow-active .workflow-card > div:first-child {
  animation: stepGlow .65s calc(var(--step-delay) + .28s) ease both;
}

/* Parent summary */
.parent-progress { transition: width 1s .25s cubic-bezier(.22,1,.36,1); }
.pending-label { opacity: 0; transform: translateY(4px); }
.summary-active .pending-label { animation: heroFade .4s .75s ease forwards; }
.parent-summary > div:last-child { opacity: .5; transform: translateY(8px); transition: .55s .85s cubic-bezier(.22,1,.36,1); }
.summary-active > div:last-child { opacity: 1; transform: translateY(0); }

/* CTA depth */
section:nth-last-of-type(1) > div > div {
  isolation: isolate;
}
section:nth-last-of-type(1) > div > div::before {
  content: '';
  position: absolute;
  inset: -40%;
  z-index: -1;
  background: conic-gradient(from 180deg, rgba(34,211,238,.18), rgba(16,185,129,.20), rgba(59,130,246,.18), rgba(139,92,246,.15), rgba(34,211,238,.18));
  filter: blur(55px);
  animation: ctaGlow 14s linear infinite;
}

/* subtle page depth */
.landing-page::before {
  content:'';
  position: fixed;
  inset: 0;
  pointer-events:none;
  z-index:-1;
  background:
    radial-gradient(circle at 14% 24%, rgba(16,185,129,.08), transparent 28%),
    radial-gradient(circle at 86% 42%, rgba(59,130,246,.08), transparent 30%),
    radial-gradient(circle at 50% 78%, rgba(168,85,247,.06), transparent 28%);
}

@keyframes navEnter { from {opacity:0; transform:translateY(-12px)} to {opacity:1; transform:none} }
@keyframes heroLineReveal { to {opacity:1; transform:translateY(0)} }
@keyframes heroFade { to {opacity:1; transform:translateY(0)} }
@keyframes dashboardEnter { to {opacity:1; transform:translateX(0) scale(1)} }
@keyframes microSlideLeft { from{opacity:0;transform:translateX(-12px)} to{opacity:1;transform:none} }
@keyframes microSlideRight { from{opacity:0;transform:translateX(14px)} to{opacity:1;transform:none} }
@keyframes microFloatA { 0%,100%{transform:translateY(0) rotate(-.4deg)} 50%{transform:translateY(-5px) rotate(.3deg)} }
@keyframes microFloatB { 0%,100%{transform:translateY(0) rotate(.4deg)} 50%{transform:translateY(5px) rotate(-.25deg)} }
@keyframes sparkFloat { 0%,100%{transform:translateY(0);opacity:.45} 50%{transform:translateY(-7px);opacity:1} }
@keyframes visualPulse { 0%,100%{transform:scaleX(.62);opacity:.55} 50%{transform:scaleX(1);opacity:1} }
@keyframes calendarFlip { from{opacity:0;transform:rotateX(60deg) scale(.9)} to{opacity:1;transform:none} }
@keyframes barsGrow { from{opacity:.2;transform:scaleY(.2)} to{opacity:1;transform:scaleY(1)} }
@keyframes chatReveal { from{opacity:0;transform:scale(.72) translateY(4px)} to{opacity:1;transform:none} }
@keyframes avatarPop { from{opacity:0;transform:scale(.65)} to{opacity:1;transform:scale(1)} }
@keyframes capTilt { from{opacity:0;transform:rotate(-12deg) scale(.85)} to{opacity:1;transform:none} }
@keyframes workflowDraw { to{transform:scaleX(1)} }
@keyframes workflowCardIn { to{opacity:1;transform:translateY(0)} }
@keyframes stepGlow {
  0%{box-shadow:0 0 0 rgba(34,211,238,0)}
  45%{box-shadow:0 0 0 7px rgba(34,211,238,.13),0 0 30px rgba(34,211,238,.28)}
  100%{box-shadow:0 10px 24px rgba(15,23,42,.12)}
}
@keyframes ctaGlow { to { transform: rotate(360deg); } }

@media (min-width: 1024px) {
  .section-space { padding-top: 104px; padding-bottom: 104px; }
}

@media (max-width: 1023px) and (min-width: 641px) {
  .section-space { padding-top: 82px; padding-bottom: 82px; }
}

@media (max-width: 640px) {
  .feature-card { min-height: auto; }
  .feature-spark { display:none; }
}

@media (prefers-reduced-motion: reduce) {
  .hero-badge-enter,
  .hero-heading .hero-line > span,
  .hero-copy,
  .hero-ctas,
  .hero-proof,
  .dashboard-enter,
  .next-class-card,
  .feedback-card {
    opacity: 1 !important;
    transform: none !important;
    animation: none !important;
  }
  .feature-card,
  .reveal-workflow {
    opacity: 1 !important;
    transform: none !important;
  }
  .feature-spark,
  .feature-visual span,
  .floating-card-left,
  .floating-card-right,
  section:nth-last-of-type(1) > div > div::before {
    animation: none !important;
  }
}

</style>