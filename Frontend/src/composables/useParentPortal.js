import { ref, computed } from 'vue'
import { parentApi } from '../services/parentApi'

function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem('user') || 'null')
  } catch {
    return null
  }
}

export function useParentPortal() {
  const user = ref(getStoredUser())

  const parentId = computed(() => {
    return user.value?.parent_id || Number(localStorage.getItem('parent_id')) || user.value?.user_id || null
  })

  const loading = ref(false)
  const error = ref('')

  const parent = ref(null)
  const children = ref([])
  const overview = ref(null)
  const meetings = ref([])
  const parentNotifications = ref([])

  const progressByChild = ref({})
  const curriculumByChild = ref({})

  async function loadProfile() {
    if (!parentId.value) return
    loading.value = true
    error.value = ''
    try {
      const res = await parentApi.getProfile(parentId.value)
      parent.value = res.data
      children.value = res.data?.linked_children || []
      return res.data
    } catch (err) {
      error.value = err.message || 'Failed to load profile'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadOverview() {
    if (!parentId.value) return
    loading.value = true
    error.value = ''
    try {
      const res = await parentApi.getOverview(parentId.value)
      overview.value = res.data
      if (!children.value.length) {
        children.value = res.data?.children || []
      }
      return res.data
    } catch (err) {
      error.value = err.message || 'Failed to load overview'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadMeetings() {
    if (!parentId.value) return
    loading.value = true
    error.value = ''
    try {
      const res = await parentApi.getMeetings(parentId.value)
      meetings.value = res.data || []
      return meetings.value
    } catch (err) {
      error.value = err.message || 'Failed to load meetings'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadChildProgress(studentId) {
    if (!parentId.value || !studentId) return
    loading.value = true
    error.value = ''
    try {
      const res = await parentApi.getChildProgress(parentId.value, studentId)
      progressByChild.value = {
        ...progressByChild.value,
        [studentId]: res.data
      }
      return res.data
    } catch (err) {
      error.value = err.message || 'Failed to load child progress'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadCurriculum(studentId) {
    if (!studentId) return
    loading.value = true
    error.value = ''
    try {
      const res = await parentApi.getChildCurriculum(studentId)
      curriculumByChild.value = {
        ...curriculumByChild.value,
        [studentId]: res.data
      }
      return res.data
    } catch (err) {
      error.value = err.message || 'Failed to load curriculum'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateProfile(payload) {
    if (!parentId.value) return
    loading.value = true
    error.value = ''
    try {
      const res = await parentApi.updateProfile(parentId.value, payload)
      parent.value = {
        ...(parent.value || {}),
        ...(res.data || {})
      }
      return res.data
    } catch (err) {
      error.value = err.message || 'Failed to update profile'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function submitMeetingRequest(payload) {
    if (!parentId.value) throw new Error('Parent not logged in')
    loading.value = true
    error.value = ''
    try {
      const [preferred_date, preferred_time] = (payload.preferredDate || '').split('T')
      const body = {
        parent_id: parentId.value,
        tutor_id: payload.tutor_id,
        student_id: payload.student_id,
        preferred_date,
        preferred_time,
        preferred_end_time: (payload.preferredEndTime || '').split('T')[1] || payload.preferredEndTime || '',
        notes: payload.reason || '',
        include_student: payload.includeStudent !== false
      }
      const res = await parentApi.requestMeeting(body)
      await loadMeetings()
      return res.data
    } catch (err) {
      error.value = err.message || 'Failed to submit meeting request'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function loadNotifications() {
    if (!parentId.value) return []
    try {
      const res = await parentApi.getNotifications(parentId.value)
      parentNotifications.value = res.data || []
      return parentNotifications.value
    } catch (err) {
      return parentNotifications.value
    }
  }

  const unreadNotificationCount = computed(() =>
    parentNotifications.value.filter((n) => !n.is_read).length
  )

  async function markNotificationRead(id) {
    await parentApi.markNotificationRead(id)
    const item = parentNotifications.value.find((n) => n.id === id || n.notification_id === id)
    if (item) item.is_read = true
  }

  async function markAllNotificationsRead() {
    const unread = parentNotifications.value.filter((n) => !n.is_read)
    for (const n of unread) {
      try { await markNotificationRead(n.id ?? n.notification_id) } catch {}
    }
  }

  async function generateWeeklyReport(studentId) {
    if (!studentId) throw new Error('No child selected')
    
    // Check if progress data exists; load it if not available
    let progressData = progressByChild.value[studentId]
    if (!progressData) {
      progressData = await loadChildProgress(studentId)
    }

    const studentName = progressData?.student_name || 'Student'
    const attendance = progressData?.attendance_rate || '100%'
    const quizzes = progressData?.recent_quiz_scores || []
    
    let quizSummary = 'No quizzes taken this week.'
    if (quizzes.length > 0) {
      const latestQuiz = quizzes[0]
      quizSummary = `Scored ${latestQuiz.score} in ${latestQuiz.subject} (${latestQuiz.topic || 'Quiz'}).`
    }

    const remarks = progressData?.tutor_remarks?.[0]?.remark || 'Demonstrating consistent effort across all subjects.'

    return `Weekly Executive AI Summary for ${studentName}:
• Attendance Record: Maintained an active attendance rate of ${attendance}.
• Academic Assessment: ${quizSummary}
• Tutor Focus Note: ${remarks}
• Recommended Next Step: Continue regular homework practice and review word problems for upcoming quizzes.`
  }

  const latestSummary = computed(() => overview.value?.latest_summary || null)

  return {
    user,
    parentId,
    loading,
    error,
    parent,
    children,
    overview,
    latestSummary,
    meetings,
    parentNotifications,
    unreadNotificationCount,
    loadNotifications,
    markNotificationRead,
    markAllNotificationsRead,
    progressByChild,
    curriculumByChild,
    loadProfile,
    loadOverview,
    loadMeetings,
    loadChildProgress,
    loadCurriculum,
    updateProfile,
    submitMeetingRequest,
    generateWeeklyReport
  }
}