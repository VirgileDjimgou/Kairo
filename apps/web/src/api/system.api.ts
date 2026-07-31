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

export async function getSystemHealth(): Promise<SystemHealthResponse> {
  const response = await fetch(`${getApiOrigin()}/health`, {
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to load system health (${response.status})`)
  }

  return response.json() as Promise<SystemHealthResponse>
}
import { getApiOrigin } from './http'
