import http from './http'

export interface AuditEventResponse {
  id: string
  tenant_id: string
  actor_user_id: string | null
  module_key: string | null
  action: string
  entity_type: string
  entity_id: string | null
  details: Record<string, unknown>
  created_at: string
}

export interface AuditEventFilters {
  limit?: number
  offset?: number
  actor_user_id?: string
  action?: string
  entity_type?: string
  entity_id?: string
  module_key?: string
  search?: string
  created_from?: string
  created_to?: string
}

export async function listAuditEvents(filters: AuditEventFilters = {}): Promise<AuditEventResponse[]> {
  const response = await http.get<AuditEventResponse[]>('/admin/audit/events', { params: filters })
  return response.data
}

export async function exportAuditEventsCsv(filters: AuditEventFilters = {}): Promise<Blob> {
  const response = await http.get('/admin/audit/events/export', {
    params: { ...filters, format: 'csv' },
    responseType: 'blob',
  })
  return response.data
}
