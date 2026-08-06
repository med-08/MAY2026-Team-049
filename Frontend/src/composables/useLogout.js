import { useRouter } from 'vue-router'
import { authApi } from '../services/authApi'

export function useLogout() {
  const router = useRouter()

  async function logout(redirectTo = '/login') {
    try {
      await authApi.logout()
    } catch (err) {
      console.error('Logout failed:', err)
    } finally {
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      localStorage.removeItem('user_id')
      localStorage.removeItem('username')
      localStorage.removeItem('parent_id')
      localStorage.removeItem('student_id')
      localStorage.removeItem('tutor_id')

      router.push(redirectTo)
    }
  }

  return { logout }
}