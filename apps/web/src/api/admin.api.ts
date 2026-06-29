import http from './http'

export interface IngestionJobHealthItemResponse {
  job_id: string
  document_id: string
  document_version_id: string
  status: string
  error_message: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string
}

export interface IngestionJobHealthResponse {
  queued_count: number
  processing_count: number
  failed_count: number
  completed_count: number
  retried_count: number
  recent_failures: IngestionJobHealthItemResponse[]
}

export async function getIngestionJobsHealth(): Promise<IngestionJobHealthResponse> {
  const response = await http.get<IngestionJobHealthResponse>('/admin/ingestion-jobs/health')
  return response.data
}
