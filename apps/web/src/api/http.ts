import axios from 'axios'
import type { AxiosInstance } from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'
const LOGIN_PATH = '/login'
const SELECTED_TENANT_KEY = 'selected_tenant_id'

const http: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
})

// Attach Bearer token from localStorage on every request
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Redirect to login on 401 (token expired or invalid)
http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem(SELECTED_TENANT_KEY)
      if (window.location.pathname !== LOGIN_PATH) {
        const redirect = `${window.location.pathname}${window.location.search}${window.location.hash}`
        const query = redirect ? `?redirect=${encodeURIComponent(redirect)}` : ''
        window.location.href = `${LOGIN_PATH}${query}`
      }
    }
    return Promise.reject(error)
  },
)

export default http
