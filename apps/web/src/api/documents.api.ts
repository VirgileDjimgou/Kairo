import http from './http'

export interface DocumentVersionResponse {
  id: string
  file_name: string
  mime_type: string
  file_size_bytes: number
  storage_bucket: string
  storage_key: string
  checksum: string
  created_at: string
}

export interface DocumentListItemResponse {
  id: string
  title: string
  description: string | null
  source_type: string
  language: string
  access_scope: string
  allowed_role_ids: string[] | null
  status: string
  owner_user_id: string | null
  created_at: string
  current_version: DocumentVersionResponse | null
}

export interface UploadDocumentResponse extends DocumentListItemResponse {
  ingestion_job_id: string
  duplicate_of_document_id: string | null
}

export interface UploadDocumentPayload {
  file: File
  title: string
  description?: string
  access_scope?: string
}

export interface UpdateDocumentAccessPayload {
  access_scope: string
  allowed_role_ids?: string[] | null
}

export async function listDocuments(): Promise<DocumentListItemResponse[]> {
  const response = await http.get<DocumentListItemResponse[]>('/documents')
  return response.data
}

export interface IngestionJobResponse {
  id: string
  document_id: string
  document_version_id: string
  status: string
  error_message: string | null
  chunk_count: number
  indexed_chunk_count: number
  started_at: string | null
  finished_at: string | null
  created_at: string
}

export async function getIngestionJob(jobId: string): Promise<IngestionJobResponse> {
  const response = await http.get<IngestionJobResponse>(`/documents/ingestion-jobs/${jobId}`)
  return response.data
}

export async function uploadDocument(payload: UploadDocumentPayload): Promise<UploadDocumentResponse> {
  const formData = new FormData()
  formData.append('file', payload.file)
  formData.append('title', payload.title)
  formData.append('access_scope', payload.access_scope ?? 'tenant_public')

  if (payload.description) {
    formData.append('description', payload.description)
  }

  const response = await http.post<UploadDocumentResponse>('/documents/upload', formData)
  return response.data
}

export async function updateDocumentAccess(
  documentId: string,
  payload: UpdateDocumentAccessPayload,
): Promise<DocumentListItemResponse> {
  const response = await http.patch<DocumentListItemResponse>(`/documents/${documentId}/access`, payload)
  return response.data
}

export async function reindexDocument(documentId: string): Promise<IngestionJobResponse> {
  const response = await http.post<IngestionJobResponse>(`/documents/${documentId}/reindex`)
  return response.data
}

export interface BulkUploadItemResponse {
  index: number
  file_name: string
  status: string
  document: UploadDocumentResponse | null
  error: string | null
}

export interface BulkUploadResponse {
  items: BulkUploadItemResponse[]
  success_count: number
  failure_count: number
}

export async function bulkUploadDocuments(payload: {
  files: File[]
  title_prefix?: string
  description?: string
  access_scope?: string
  allowed_role_ids?: string[] | null
}): Promise<BulkUploadResponse> {
  const formData = new FormData()
  for (const file of payload.files) {
    formData.append('files', file)
  }
  formData.append('title_prefix', payload.title_prefix ?? '')
  formData.append('access_scope', payload.access_scope ?? 'tenant_public')
  if (payload.description) {
    formData.append('description', payload.description)
  }
  if (payload.allowed_role_ids && payload.allowed_role_ids.length > 0) {
    for (const role of payload.allowed_role_ids) {
      formData.append('allowed_role_ids', role)
    }
  }
  const response = await http.post<BulkUploadResponse>('/documents/bulk-upload', formData)
  return response.data
}

export async function archiveDocument(documentId: string): Promise<DocumentListItemResponse> {
  const response = await http.patch<DocumentListItemResponse>(`/documents/${documentId}/archive`)
  return response.data
}

export async function unarchiveDocument(documentId: string): Promise<DocumentListItemResponse> {
  const response = await http.patch<DocumentListItemResponse>(`/documents/${documentId}/unarchive`)
  return response.data
}

export async function retryIngestionJob(jobId: string): Promise<{ job: IngestionJobResponse; retried: boolean }> {
  const response = await http.post<{ job: IngestionJobResponse; retried: boolean }>(
    `/documents/ingestion-jobs/${jobId}/retry`,
  )
  return response.data
}

export interface ChatQueryLogResponse {
  id: string
  tenant_id: string
  user_id: string
  question: string
  answer: string
  refused: boolean
  refusal_reason: string | null
  confidence: number
  citations_json: string
  source_types_json: string
  created_at: string
}

export async function listChatQueries(limit = 20): Promise<ChatQueryLogResponse[]> {
  const response = await http.get<ChatQueryLogResponse[]>('/admin/chat-queries', {
    params: { limit },
  })
  return response.data
}
