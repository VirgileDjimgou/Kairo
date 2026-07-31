import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { notifyOperation } from '@/services/operation-notifications'

export const API_BASE_URL = resolveApiBaseUrl(import.meta.env.VITE_API_BASE_URL)
const LOGIN_PATH = '/login'
const SELECTED_TENANT_KEY = 'selected_tenant_id'

function resolveApiBaseUrl(configuredBaseUrl?: string): string {
  if (!configuredBaseUrl) {
    return import.meta.env.DEV ? 'http://localhost:8000/api/v1' : '/api/v1'
  }

  if (window.location.protocol !== 'https:' || !configuredBaseUrl.startsWith('http://')) {
    return configuredBaseUrl
  }

  try {
    const configuredUrl = new URL(configuredBaseUrl)
    if (configuredUrl.host === window.location.host) {
      return `${window.location.origin}${configuredUrl.pathname}${configuredUrl.search}`
    }
  } catch {
    // Keep an invalid development configuration unchanged so Axios reports it clearly.
  }

  return configuredBaseUrl
}

const http: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30_000,
})

/**
 * Returns the origin that hosts the API. Public HTTPS clients always retain
 * their HTTPS origin, even when an obsolete deployment configuration contains
 * an insecure same-host API URL.
 */
export function getApiOrigin(): string {
  if (API_BASE_URL.startsWith('/')) {
    return window.location.origin
  }

  try {
    return new URL(API_BASE_URL).origin
  } catch {
    return window.location.origin
  }
}

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
  (response) => {
    const method = response.config.method?.toLowerCase()
    const isMutation = method === 'post' || method === 'put' || method === 'patch' || method === 'delete'
    const isFailureLog = response.config.headers?.['X-Kairo-Operation-Failure-Log'] === '1'
    if (isMutation && !isFailureLog) {
      notifyOperation({ level: 'success', messageKey: 'toast.operationSucceeded' })
    }
    return response
  },
  (error) => {
    const status = error.response?.status
    const detail = typeof error.response?.data?.detail === 'string'
      ? error.response.data.detail
      : undefined
    const isFailureLog = error.config?.headers?.['X-Kairo-Operation-Failure-Log'] === '1'
    if (!isFailureLog) {
      notifyOperation({
        level: status === 422 ? 'warning' : 'error',
        messageKey: status === 422 ? 'toast.validationFailed' : 'toast.operationFailed',
        detail,
      })
      reportOperationFailure(error)
    }
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

function reportOperationFailure(error: unknown): void {
  const request = (error as { config?: { method?: string; url?: string; headers?: Record<string, string> }; response?: { status?: number } }).config
  const response = (error as { response?: { status?: number } }).response
  if (!localStorage.getItem('access_token') || !request?.url || request.url.includes('/operation-journal/failures')) return
  void http.post('/admin/audit/operation-journal/failures', {
    method: request.method?.toUpperCase() ?? 'UNKNOWN',
    path: request.url.split('?')[0],
    status_code: response?.status ?? null,
  }, { headers: { 'X-Kairo-Operation-Failure-Log': '1' } }).catch(() => undefined)
}

export default http
