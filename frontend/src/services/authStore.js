import { create } from 'zustand'
import { authAPI } from './api'

export const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const response = await authAPI.login({ email, password })
      const { access_token } = response.data
      localStorage.setItem('token', access_token)
      set({ token: access_token, isAuthenticated: true, isLoading: false })
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.detail || 'Đăng nhập thất bại'
      set({ error: message, isLoading: false })
      return { success: false, error: message }
    }
  },

  logout: () => {
    localStorage.removeItem('token')
    set({ user: null, token: null, isAuthenticated: false })
  },

  fetchUser: async () => {
    try {
      const response = await authAPI.me()
      set({ user: response.data })
    } catch {
      set({ user: null, isAuthenticated: false })
    }
  },
}))
