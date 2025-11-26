import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<any>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const role = ref<string | null>(localStorage.getItem('role'))

  const isAuthenticated = computed(() => !!token.value)
  const isAdmin = computed(() => role.value === 'admin')

  const login = async (username: string, password: string, isAdmin: boolean = false) => {
    try {
      const endpoint = isAdmin ? '/admin/login' : '/user/login'
      const response = await api.post(endpoint, { username, password })
      
      token.value = response.data.token || response.data.access_token
      role.value = isAdmin ? 'admin' : 'user'
      user.value = response.data.user || response.data
      
      localStorage.setItem('token', token.value)
      localStorage.setItem('role', role.value)
      
      if (response.data.user) {
        localStorage.setItem('user', JSON.stringify(response.data.user))
      }
      
      return { success: true }
    } catch (error: any) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Login failed' 
      }
    }
  }

  const register = async (userData: any) => {
    try {
      const response = await api.post('/user/register', userData)
      return { success: true, data: response.data }
    } catch (error: any) {
      return { 
        success: false, 
        message: error.response?.data?.message || 'Registration failed' 
      }
    }
  }

  const logout = () => {
    token.value = null
    role.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('role')
    localStorage.removeItem('user')
  }

  const loadUser = () => {
    const storedUser = localStorage.getItem('user')
    if (storedUser) {
      user.value = JSON.parse(storedUser)
    }
  }

  return {
    user,
    token,
    role,
    isAuthenticated,
    isAdmin,
    login,
    register,
    logout,
    loadUser
  }
})

