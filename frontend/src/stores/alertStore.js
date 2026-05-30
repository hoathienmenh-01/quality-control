import { create } from 'zustand'
import { alertsAPI } from '../services/api'

export const useAlertStore = create((set, get) => ({
  alerts: [],
  realtimeAlerts: [],  // Alerts từ WebSocket real-time
  isLoading: false,
  error: null,
  filterSeverity: '',
  wsConnected: false,

  setFilterSeverity: (s) => set({ filterSeverity: s }),
  setWsConnected: (connected) => set({ wsConnected: connected }),

  fetchAlerts: async (params) => {
    set({ isLoading: true, error: null })
    try {
      const response = await alertsAPI.getAll(params)
      set({ alerts: response.data, isLoading: false })
    } catch {
      set({ isLoading: false })
    }
  },

  /**
   * Thêm alert real-time từ WebSocket vào store
   */
  addRealtimeAlert: (wsAlert) => {
    const alert = {
      id: `ws-${Date.now()}`,
      severity: wsAlert.severity,
      title: wsAlert.title,
      message: wsAlert.message,
      station: wsAlert.station_id,
      alert_type: wsAlert.alert_type,
      created_at: wsAlert.created_at || new Date().toISOString(),
      read: false,
      resolved: false,
      isRealtime: true,
    }
    set({ realtimeAlerts: [alert, ...get().realtimeAlerts].slice(0, 100) })
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
    const { alerts, realtimeAlerts, filterSeverity } = get()
    const all = [...realtimeAlerts, ...alerts]
    if (!filterSeverity) return all
    return all.filter((a) => a.severity === filterSeverity)
  },
}))
