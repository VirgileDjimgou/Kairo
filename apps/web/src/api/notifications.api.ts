import http from './http'

export interface NotificationChannelResponse {
  channel: string
  display_name: string
  description: string
  configured: boolean
  simulation_only: boolean
  target_hint: string
}

export interface NotificationDispatchResponse {
  channel: string
  status: string
  message: string
  delivered: boolean
  simulation_only: boolean
}

export interface NotificationTestResponse {
  results: NotificationDispatchResponse[]
}

export interface SendNotificationTestPayload {
  channels: string[]
  recipient: string
  subject?: string | null
  body: string
}

export async function listNotificationChannels(): Promise<NotificationChannelResponse[]> {
  const response = await http.get<NotificationChannelResponse[]>('/notifications/channels')
  return response.data
}

export async function sendNotificationTest(
  payload: SendNotificationTestPayload,
): Promise<NotificationTestResponse> {
  const response = await http.post<NotificationTestResponse>('/notifications/test', payload)
  return response.data
}
