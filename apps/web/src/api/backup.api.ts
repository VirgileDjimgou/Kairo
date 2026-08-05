import http from './http'

export interface BackupRunResponse {
  id: string
  tenant_id: string
  trigger: string
  status: string
  storage_reference: string | null
  archive_sha256: string | null
  manifest_sha256: string | null
  archive_size_bytes: number | null
  components: Record<string, unknown>
  error_code: string | null
  requested_at: string
  started_at: string | null
  completed_at: string | null
  verified_at: string | null
}

export interface BackupOverviewResponse {
  automatic_enabled: boolean
  retention_days: number
  external_storage_configured: boolean
  point_in_time_recovery_enabled: boolean
  last_successful_backup_at: string | null
  last_restore_drill_at: string | null
  runs: BackupRunResponse[]
}

export async function getBackupOverview(): Promise<BackupOverviewResponse> {
  return (await http.get<BackupOverviewResponse>('/recovery/backups')).data
}

export async function requestBackup(reason?: string): Promise<BackupRunResponse> {
  return (await http.post<BackupRunResponse>('/recovery/backups', { reason: reason || null })).data
}

export async function importBackup(archive: File, manifest: File): Promise<BackupRunResponse> {
  const payload = new FormData()
  payload.append('archive', archive)
  payload.append('manifest', manifest)
  return (await http.post<{ run: BackupRunResponse }>('/recovery/backups/import', payload, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })).data.run
}
