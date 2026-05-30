import { create } from 'zustand'
import { dashboardAPI } from '../services/api'

export const useDashboardStore = create((set) => ({
  stats: null,  // null = chưa load, khác mock data
  isLoading: false,
  error: null,
  isMock: false,  // true nếu đang dùng dữ liệu mẫu

  fetchStats: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await dashboardAPI.stats()
      set({ stats: response.data, isLoading: false, isMock: false })
    } catch (err) {
      set({ 
        isLoading: false, 
        error: err.message || 'Không thể tải dữ liệu',
        isMock: true,  // Đánh dấu đang dùng mock
        stats: {
          total_inspected: 0,
          total_passed: 0,
          total_failed: 0,
          pass_rate: 0,
        },
      })
    }
  },
}))
