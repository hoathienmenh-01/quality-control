import { create } from 'zustand'
import { alertsAPI } from '../services/api'

const MOCK_ALERTS = [
  {
    id: 1,
    severity: 'critical',
    message: 'Station B: Tỷ lệ lỗi vượt ngưỡng 15%',
    station: 'Station B',
    created_at: new Date(Date.now() - 300000).toISOString(),
    read: false,
    resolved: false,
  },
  {
    id: 2,
    severity: 'warning',
    message: 'Camera mất kết nối tạm thời',
    station: 'Station A',
    created_at: new Date(Date.now() - 1800000).toISOString(),
    read: false,
    resolved: false,
  },
  {
    id: 3,
    severity: 'info',
    message: 'Batch #1234 hoàn thành kiểm tra',
    station: 'Station C',
    created_at: new Date(Date.now() - 3600000).toISOString(),
    read: true,
    resolved: true,
  },
  {
    id: 4,
    severity: 'warning',
    message: 'QR reader chậm bất thường tại Station D',
    station: 'Station D',
    created_at: new Date(Date.now() - 7200000).toISOString(),
    read: true,
    resolved: false,
  },
  {
    id: 5,
    severity: 'info',
    message: 'Hệ thống backup hoàn tất',
    station: null,
    created_at: new Date(Date.now() - 14400000).toISOString(),
    read: true,
    resolved: true,
  },
]

export const useAlertStore = create((set, get) => ({
  alerts: MOCK_ALERTS,
  isLoading: false,
  error: null,
  filterSeverity: '',

  setFilterSeverity: (s) => set({ filterSeverity: s }),

  fetchAlerts: async (params) => {
    set({ isLoading: true, error: null })
    try {
      const response = await alertsAPI.getAll(params)
      set({ alerts: response.data, isLoading: false })
    } catch {
      set({ isLoading: false })
    }
  },

  markRead: async (id) => {
    try {
      await alertsAPI.markRead(id)
    } catch {}
    set({ alerts: get().alerts.map((a) => (a.id === id ? { ...a, read: true } : a)) })
  },

  resolve: async (id) => {
    try {
      await alertsAPI.resolve(id)
    } catch {}
    set({ alerts: get().alerts.map((a) => (a.id === id ? { ...a, resolved: true } : a)) })
  },

  getFilteredAlerts: () => {
    const { alerts, filterSeverity } = get()
    if (!filterSeverity) return alerts
    return alerts.filter((a) => a.severity === filterSeverity)
  },
}))
