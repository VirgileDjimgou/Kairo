import http from './http'

export interface AnnouncementResponse {
  id: string
  tenant_id: string
  title: string
  body: string
  visibility_scope: string
  published_at: string | null
  expires_at: string | null
  created_by: string | null
  created_at: string
  updated_at: string
}

export interface CreateAnnouncementPayload {
  title: string
  body: string
  visibility_scope?: string
  published_at?: string | null
  expires_at?: string | null
}

export interface UpdateAnnouncementPayload {
  title?: string
  body?: string
  visibility_scope?: string
  published_at?: string | null
  expires_at?: string | null
}

export async function listActiveAnnouncements(): Promise<AnnouncementResponse[]> {
  const response = await http.get<AnnouncementResponse[]>('/announcements/active')
  return response.data
}

export async function listAnnouncements(): Promise<AnnouncementResponse[]> {
  const response = await http.get<AnnouncementResponse[]>('/announcements/')
  return response.data
}

export async function getAnnouncement(announcementId: string): Promise<AnnouncementResponse> {
  const response = await http.get<AnnouncementResponse>(`/announcements/${announcementId}`)
  return response.data
}

export async function createAnnouncement(payload: CreateAnnouncementPayload): Promise<AnnouncementResponse> {
  const response = await http.post<AnnouncementResponse>('/announcements/', payload)
  return response.data
}

export async function updateAnnouncement(announcementId: string, payload: UpdateAnnouncementPayload): Promise<AnnouncementResponse> {
  const response = await http.patch<AnnouncementResponse>(`/announcements/${announcementId}`, payload)
  return response.data
}

export async function deleteAnnouncement(announcementId: string): Promise<void> {
  await http.delete(`/announcements/${announcementId}`)
}

export async function exportAnnouncementsCsv(): Promise<Blob> {
  const response = await http.get('/announcements/export', { responseType: 'blob' })
  return response.data
}
