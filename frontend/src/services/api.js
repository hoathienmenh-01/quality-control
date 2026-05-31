import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// Request interceptor — attach token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor — handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

// ── Auth ──
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
}

// ── Inspections ──
export const inspectionsAPI = {
  getAll: (params) => api.get('/inspections', { params }),
  getById: (id) => api.get(`/inspections/${id}`),
  create: (data) => api.post('/inspections', data),
  getStats: () => api.get('/inspections/stats'),
}

// ── Templates ──
export const templatesAPI = {
  getAll: () => api.get('/templates'),
  create: (data) => api.post('/templates', data),
  update: (id, data) => api.put(`/templates/${id}`, data),
  delete: (id) => api.delete(`/templates/${id}`),
}

// ── Export ──
export const exportAPI = {
  excel: (params) => api.get('/export/excel', { params, responseType: 'blob' }),
  csv: (params) => api.get('/export/csv', { params, responseType: 'blob' }),
  sql: (params) => api.get('/export/sql', { params, responseType: 'blob' }),
}

// ── Defects ──
export const defectsAPI = {
  summary: (params) => api.get('/defects/summary', { params }),
  trend: (params) => api.get('/defects/trend', { params }),
  top: (params) => api.get('/defects/top', { params }),
}

// ── Alerts ──
export const alertsAPI = {
  getAll: (params) => api.get('/alerts', { params }),
  markRead: (id) => api.put(`/alerts/${id}/read`),
  resolve: (id) => api.put(`/alerts/${id}/resolve`),
}

// ── Dashboard ──
export const dashboardAPI = {
  stats: () => api.get('/dashboard/stats'),
  realtime: () => api.get('/dashboard/realtime'),
}

// ── Camera ──
export const cameraAPI = {
  capture: () => api.post('/camera/capture'),
  status: () => api.get('/camera/status'),
  connect: (data) => api.post('/camera/connect', data),
}

export default api
