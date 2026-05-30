import { create } from 'zustand'
import { inspectionsAPI } from '../services/api'

// ── Mock data for development ──
const MOCK_INSPECTIONS = Array.from({ length: 50 }, (_, i) => ({
  id: i + 1,
  serial_number: `SN-${String(2024000 + i).padStart(7, '0')}`,
  batch_number: `BATCH-${String(Math.floor(i / 10) + 1).padStart(3, '0')}`,
  station: `Station ${String.fromCharCode(65 + (i % 4))}`,
  result: Math.random() > 0.12 ? 'PASS' : 'FAIL',
  timestamp: new Date(Date.now() - i * 600000).toISOString(),
  inference_time: Math.floor(Math.random() * 200) + 50,
  defects: Math.random() > 0.8 ? ['Thiếu linh kiện', 'Lỗi hàn'] : [],
  checks: {
    component: Math.random() > 0.1 ? 'PASS' : 'FAIL',
    qr: Math.random() > 0.05 ? 'PASS' : 'FAIL',
    sn: Math.random() > 0.08 ? 'PASS' : 'FAIL',
    anten: Math.random() > 0.12 ? 'PASS' : 'FAIL',
  },
}))

export const useInspectionStore = create((set, get) => ({
  inspections: MOCK_INSPECTIONS,
  selectedInspection: null,
  isLoading: false,
  error: null,
  filters: { search: '', result: '', station: '', dateFrom: '', dateTo: '' },
  pagination: { page: 0, pageSize: 10, total: MOCK_INSPECTIONS.length },

  setFilters: (filters) => set({ filters: { ...get().filters, ...filters } }),
  setPagination: (pagination) => set({ pagination: { ...get().pagination, ...pagination } }),

  fetchInspections: async (params) => {
    set({ isLoading: true, error: null })
    try {
      const response = await inspectionsAPI.getAll(params)
      set({ inspections: response.data, isLoading: false })
    } catch {
      // Keep mock data on error
      set({ isLoading: false })
    }
  },

  fetchInspectionById: async (id) => {
    set({ isLoading: true })
    try {
      const response = await inspectionsAPI.getById(id)
      set({ selectedInspection: response.data, isLoading: false })
    } catch {
      const mock = get().inspections.find((i) => i.id === Number(id))
      set({ selectedInspection: mock || null, isLoading: false })
    }
  },

  getFilteredInspections: () => {
    const { inspections, filters } = get()
    return inspections.filter((item) => {
      if (filters.search) {
        const q = filters.search.toLowerCase()
        if (
          !item.serial_number.toLowerCase().includes(q) &&
          !item.batch_number.toLowerCase().includes(q) &&
          !item.station.toLowerCase().includes(q)
        )
          return false
      }
      if (filters.result && item.result !== filters.result) return false
      if (filters.station && item.station !== filters.station) return false
      if (filters.dateFrom) {
        const from = new Date(filters.dateFrom)
        if (new Date(item.timestamp) < from) return false
      }
      if (filters.dateTo) {
        const to = new Date(filters.dateTo)
        to.setDate(to.getDate() + 1)
        if (new Date(item.timestamp) > to) return false
      }
      return true
    })
  },
}))
