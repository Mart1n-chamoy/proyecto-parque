import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para agregar token si existe
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

// Clientes
export const clientsAPI = {
  getAll: (params) => api.get('/clients/', { params }),
  get: (id) => api.get(`/clients/${id}/`),
  create: (data) => api.post('/clients/', data),
  update: (id, data) => api.put(`/clients/${id}/`, data),
  delete: (id) => api.delete(`/clients/${id}/`),
  getActive: () => api.get('/clients/active/'),
  getInactive: () => api.get('/clients/inactive/'),
  activate: (id) => api.post(`/clients/${id}/activate/`),
  deactivate: (id) => api.post(`/clients/${id}/deactivate/`),
}

// Llamadas
export const callsAPI = {
  getAll: (params) => api.get('/calls/', { params }),
  get: (id) => api.get(`/calls/${id}/`),
  create: (data) => api.post('/calls/', data),
  update: (id, data) => api.put(`/calls/${id}/`, data),
  delete: (id) => api.delete(`/calls/${id}/`),
  getPending: () => api.get('/calls/pending/'),
  getCompleted: () => api.get('/calls/completed/'),
  getFailed: () => api.get('/calls/failed/'),
  retry: (id) => api.post(`/calls/${id}/retry/`),
}

// Lotes de Llamadas
export const batchesAPI = {
  getAll: (params) => api.get('/calls/batches/', { params }),
  get: (id) => api.get(`/calls/batches/${id}/`),
  create: (data) => api.post('/calls/batches/', data),
  update: (id, data) => api.put(`/calls/batches/${id}/`, data),
  delete: (id) => api.delete(`/calls/batches/${id}/`),
  getPending: () => api.get('/calls/batches/pending/'),
  getProcessing: () => api.get('/calls/batches/processing/'),
  start: (id) => api.post(`/calls/batches/${id}/start/`),
  complete: (id) => api.post(`/calls/batches/${id}/complete/`),
}

export default api
