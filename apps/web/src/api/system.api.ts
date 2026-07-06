export interface SystemHealthCheck {
  status: 'ok' | 'degraded' | 'unavailable' | 'error'
  latency_ms: number
}

export interface SystemHealthResponse {
  status: 'ok' | 'degraded' | 'unavailable'
  version: string
  env: string
  checks: Record<string, SystemHealthCheck>
  modules: string[]
}

const SYSTEM_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1').replace(
  /\/api\/v1\/?$/,
  '',
)

export async function getSystemHealth(): Promise<SystemHealthResponse> {
  const response = await fetch(`${SYSTEM_BASE_URL}/health`, {
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to load system health (${response.status})`)
  }

  return response.json() as Promise<SystemHealthResponse>
}
