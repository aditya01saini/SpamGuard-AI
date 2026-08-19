import axios from 'axios'

// Base URL: defaults to the same-origin '/api' (works in dev via Vite proxy
// and in production when FastAPI serves the built frontend).
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

const api = axios.create({ baseURL, timeout: 90000 })

// Normalize backend error envelopes ({ success, error }) into friendly messages.
api.interceptors.response.use(
  (res) => res,
  (err) => {
    const data = err?.response?.data
    const message = data?.error?.message || data?.detail || err.message
    const error = new Error(message || 'Network error. Please try again.')
    error.status = err?.response?.status
    error.code = data?.error?.code
    throw error
  }
)

export const analyzeEmail = async (payload) => {
  const { data } = await api.post('/analyze', payload)
  return data.data
}

export const analyzeUpload = async (file) => {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/analyze/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data.data
}

export const getHistory = async (params = {}) => {
  const { data } = await api.get('/history', { params })
  return data.data
}

export const getScan = async (id) => {
  const { data } = await api.get(`/history/${id}`)
  return data.data
}

export const deleteScan = async (id) => {
  const { data } = await api.delete(`/history/${id}`)
  return data.data
}

export const getAnalytics = async () => {
  const { data } = await api.get('/analytics')
  return data.data
}

export const getModelInfo = async () => {
  const { data } = await api.get('/model-info')
  return data.data
}

export const getHealth = async () => {
  const { data } = await api.get('/health')
  return data.data
}

export const reportUrl = (id) => `${baseURL}/history/${id}/report`

export default api
