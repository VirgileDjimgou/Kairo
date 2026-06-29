import http from './http'

export interface EventResponse {
  id: string
  tenant_id: string
  title: string
  description: string | null
  start_at: string
  end_at: string | null
  location: string | null
  visibility_scope: string
  status: string
  created_by: string | null
  created_at: string
  updated_at: string
}

export interface CreateEventPayload {
  title: string
  description?: string | null
  start_at: string
  end_at?: string | null
  location?: string | null
  visibility_scope?: string
  status?: string
}

export interface UpdateEventPayload {
  title?: string
  description?: string | null
  start_at?: string
  end_at?: string | null
  location?: string | null
  visibility_scope?: string
  status?: string
}

export async function listPublicEvents(): Promise<EventResponse[]> {
  const response = await http.get<EventResponse[]>('/events/public')
  return response.data
}

export async function listAllEvents(upcoming = false): Promise<EventResponse[]> {
  const params = upcoming ? { upcoming: 'true' } : {}
  const response = await http.get<EventResponse[]>('/events/', { params })
  return response.data
}

export async function getEvent(eventId: string): Promise<EventResponse> {
  const response = await http.get<EventResponse>(`/events/${eventId}`)
  return response.data
}

export async function createEvent(payload: CreateEventPayload): Promise<EventResponse> {
  const response = await http.post<EventResponse>('/events/', payload)
  return response.data
}

export async function updateEvent(eventId: string, payload: UpdateEventPayload): Promise<EventResponse> {
  const response = await http.patch<EventResponse>(`/events/${eventId}`, payload)
  return response.data
}

export async function deleteEvent(eventId: string): Promise<void> {
  await http.delete(`/events/${eventId}`)
}

export async function exportEventsCsv(): Promise<Blob> {
  const response = await http.get('/events/export', { responseType: 'blob' })
  return response.data
}
