import http from './http'

export interface NotificationChannelResponse {
  channel: string
  display_name: string
  description: string
  configured: boolean
  simulation_only: boolean
  target_hint: string
  polling_supported: boolean
}

export interface NotificationDispatchResponse {
  channel: string
  status: string
  message: string
  delivered: boolean
  simulation_only: boolean
  delivery_stage: string
  reconciliation_status: string
  reconciliation_supported: boolean
  provider_reference?: string | null
  polling_supported: boolean
}

export interface NotificationHistoryEntry {
  id: string
  action: string
  channel: string
  recipient: string
  status: string
  message: string
  delivered: boolean
  simulation_only: boolean
  delivery_stage: string
  reconciliation_status: string
  reconciliation_supported: boolean
  provider_reference?: string | null
  polling_supported: boolean
  created_at: string
}

export interface PollNotificationReconciliationPayload {
  channel: string
  provider_reference: string
}

export interface NotificationReconciliationPollResponse {
  channel: string
  provider_reference: string
  delivery_stage: string
  reconciliation_status: string
  updated: boolean
  provider_message: string
  external_status?: string | null
}

export interface SendNotificationDispatchPayload {
  channel: string
  recipient: string
  subject?: string | null
  body: string
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

export async function sendNotificationDispatch(
  payload: SendNotificationDispatchPayload,
): Promise<NotificationDispatchResponse> {
  const response = await http.post<NotificationDispatchResponse>('/notifications/dispatch', payload)
  return response.data
}

export async function listNotificationHistory(): Promise<NotificationHistoryEntry[]> {
  const response = await http.get<NotificationHistoryEntry[]>('/notifications/history')
  return response.data
}

export async function pollNotificationReconciliation(
  payload: PollNotificationReconciliationPayload,
): Promise<NotificationReconciliationPollResponse> {
  const response = await http.post<NotificationReconciliationPollResponse>(
    '/notifications/reconciliation/poll',
    payload,
  )
  return response.data
}
