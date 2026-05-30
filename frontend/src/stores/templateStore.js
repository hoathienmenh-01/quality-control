import { create } from 'zustand'
import { templatesAPI } from '../services/api'

const MOCK_TEMPLATES = [
  {
    id: 1,
    name: 'Template A - Board PCB',
    product_type: 'PCB Board',
    description: 'Template kiểm tra board PCB với 4 linh kiện chính',
    created_at: '2024-01-15T08:00:00Z',
    updated_at: '2024-03-20T10:30:00Z',
    checks: ['component', 'qr', 'sn', 'anten'],
    active: true,
  },
  {
    id: 2,
    name: 'Template B - Module WiFi',
    product_type: 'WiFi Module',
    description: 'Template kiểm tra module WiFi với anten đặc biệt',
    created_at: '2024-02-01T09:00:00Z',
    updated_at: '2024-03-18T14:00:00Z',
    checks: ['component', 'qr', 'anten'],
    active: true,
  },
  {
    id: 3,
    name: 'Template C - Sensor Hub',
    product_type: 'Sensor',
    description: 'Template kiểm tra cảm biến đa năng',
    created_at: '2024-02-20T10:00:00Z',
    updated_at: '2024-03-15T16:00:00Z',
    checks: ['component', 'sn'],
    active: false,
  },
]

export const useTemplateStore = create((set, get) => ({
  templates: MOCK_TEMPLATES,
  isLoading: false,
  error: null,
  searchQuery: '',

  setSearchQuery: (q) => set({ searchQuery: q }),

  fetchTemplates: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await templatesAPI.getAll()
      set({ templates: response.data, isLoading: false })
    } catch {
      set({ isLoading: false })
    }
  },

  createTemplate: async (data) => {
    try {
      const response = await templatesAPI.create(data)
      set({ templates: [...get().templates, response.data] })
      return { success: true }
    } catch {
      const newTemplate = { ...data, id: Date.now(), created_at: new Date().toISOString(), updated_at: new Date().toISOString() }
      set({ templates: [...get().templates, newTemplate] })
      return { success: true }
    }
  },

  updateTemplate: async (id, data) => {
    try {
      const response = await templatesAPI.update(id, data)
      set({ templates: get().templates.map((t) => (t.id === id ? response.data : t)) })
      return { success: true }
    } catch {
      set({
        templates: get().templates.map((t) =>
          t.id === id ? { ...t, ...data, updated_at: new Date().toISOString() } : t
        ),
      })
      return { success: true }
    }
  },

  deleteTemplate: async (id) => {
    try {
      await templatesAPI.delete(id)
      set({ templates: get().templates.filter((t) => t.id !== id) })
      return { success: true }
    } catch {
      set({ templates: get().templates.filter((t) => t.id !== id) })
      return { success: true }
    }
  },

  getFilteredTemplates: () => {
    const { templates, searchQuery } = get()
    if (!searchQuery) return templates
    const q = searchQuery.toLowerCase()
    return templates.filter(
      (t) =>
        t.name.toLowerCase().includes(q) ||
        t.product_type.toLowerCase().includes(q) ||
        t.description?.toLowerCase().includes(q)
    )
  },
}))
