import { create } from 'zustand'
import { dashboardAPI } from '../services/api'

export const useDashboardStore = create((set) => ({
  stats: {
    total_inspected: 1250,
    total_passed: 1180,
    total_failed: 70,
    pass_rate: 94.4,
  },
  isLoading: false,
  error: null,

  fetchStats: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await dashboardAPI.stats()
      set({ stats: response.data, isLoading: false })
    } catch {
      set({ isLoading: false })
    }
  },
}))
