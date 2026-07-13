import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/axios'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const role = ref(localStorage.getItem('role') || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)
  const isMerchant = computed(() => role.value === 'merchant')

  function setAuth(t, r) {
    token.value = t
    role.value = r
    localStorage.setItem('token', t)
    localStorage.setItem('role', r)
  }

  function clearAuth() {
    token.value = ''
    role.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('role')
  }

  async function fetchUser() {
    try {
      const res = await api.get('/auth/me')
      user.value = res.data
      return res.data
    } catch (e) {
      clearAuth()
      throw e
    }
  }

  async function login(payload) {
    const res = await api.post('/auth/login', payload)
    setAuth(res.data.access_token, res.data.role)
    await fetchUser()
    return res.data
  }

  async function register(payload) {
    return await api.post('/auth/register', payload)
  }

  function logout() {
    clearAuth()
  }

  return { token, role, user, isLoggedIn, isMerchant, setAuth, clearAuth, fetchUser, login, register, logout }
})
