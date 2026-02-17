import { ref, computed } from 'vue'
import { request } from '../api'

const TOKEN_KEY = 'smart_procurement_token'
const USER_KEY = 'smart_procurement_user'

// 全局状态
const token = ref(localStorage.getItem(TOKEN_KEY) || '')
const user = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))

export function useAuth() {
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const userRole = computed(() => user.value?.role || '')
  const isAdmin = computed(() => userRole.value === 'admin')
  const isProcessor = computed(() => userRole.value === 'processor')
  const isHandler = computed(() => userRole.value === 'handler')

  const login = async (username, password) => {
    try {
      const res = await request.post('/auth/login', { username, password })
      if (res.success) {
        token.value = res.data.access_token
        user.value = res.data.user
        localStorage.setItem(TOKEN_KEY, res.data.access_token)
        localStorage.setItem(USER_KEY, JSON.stringify(res.data.user))
        return { success: true }
      }
      return { success: false, error: res.error }
    } catch (e) {
      return { success: false, error: e.message || '登录失败' }
    }
  }

  const register = async (username, email, password, role) => {
    try {
      const res = await request.post('/auth/register', { username, email, password, role })
      return { success: res.success, error: res.error }
    } catch (e) {
      return { success: false, error: e.message || '注册失败' }
    }
  }

  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  const fetchCurrentUser = async () => {
    if (!token.value) return null
    try {
      const res = await request.get('/auth/me')
      if (res.success) {
        user.value = res.data
        localStorage.setItem(USER_KEY, JSON.stringify(res.data))
        return res.data
      }
    } catch (e) {
      logout()
    }
    return null
  }

  return {
    token,
    user,
    isLoggedIn,
    userRole,
    isAdmin,
    isProcessor,
    isHandler,
    login,
    register,
    logout,
    fetchCurrentUser
  }
}
