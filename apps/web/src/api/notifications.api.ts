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
  retry_supported: boolean
  retry_eligible: boolean
  retry_source_provider_reference?: string | null
  stale_pending: boolean
  stale_minutes?: number | null
  created_at: string
}

export interface NotificationHistorySummary {
  total: number
  pending: number
  delivered: number
  failed: number
  simulated: number
  stale_pending: number
}

export interface NotificationHistoryResponse {
  items: NotificationHistoryEntry[]
  summary: NotificationHistorySummary
}

export interface InboxNotification {
  id: string
  event_type: string
  category: string
  priority: string
  target_path: string
  metadata: Record<string, unknown>
  read_at: string | null
  created_at: string
}

export interface NotificationInboxResponse {
  items: InboxNotification[]
  unread_count: number
}

export interface PushConfiguration {
  enabled: boolean
  public_key?: string | null
  reason?: string | null
}

export interface NotificationPreferences {
  push_enabled: boolean
  finance_enabled: boolean
  discipline_enabled: boolean
  announcements_enabled: boolean
  events_enabled: boolean
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

export interface RetryNotificationPayload {
  channel: string
  provider_reference: string
}

export interface NotificationRetryResponse {
  source_provider_reference: string
  dispatch: NotificationDispatchResponse
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

export async function listNotificationHistory(params?: {
  status?: 'all' | 'pending' | 'delivered' | 'failed' | 'simulated'
  stale_only?: boolean
  limit?: number
}): Promise<NotificationHistoryResponse> {
  const response = await http.get<NotificationHistoryResponse>('/notifications/history', { params })
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

export async function retryNotificationDispatch(
  payload: RetryNotificationPayload,
): Promise<NotificationRetryResponse> {
  const response = await http.post<NotificationRetryResponse>('/notifications/retry', payload)
  return response.data
}

export async function getNotificationInbox(): Promise<NotificationInboxResponse> {
  const response = await http.get<NotificationInboxResponse>('/notifications/inbox')
  return response.data
}

export async function markNotificationRead(id: string): Promise<void> {
  await http.post(`/notifications/inbox/${id}/read`)
}

export async function markAllNotificationsRead(): Promise<void> {
  await http.post('/notifications/inbox/read-all')
}

export async function getPushConfiguration(): Promise<PushConfiguration> {
  const response = await http.get<PushConfiguration>('/notifications/push/configuration')
  return response.data
}

export async function getNotificationPreferences(): Promise<NotificationPreferences> {
  const response = await http.get<NotificationPreferences>('/notifications/preferences')
  return response.data
}

export async function updateNotificationPreferences(payload: NotificationPreferences): Promise<NotificationPreferences> {
  const response = await http.put<NotificationPreferences>('/notifications/preferences', payload)
  return response.data
}

export async function registerNotificationDevice(payload: { installation_id: string; platform?: string }): Promise<void> {
  await http.post('/notifications/devices', payload)
}

export async function savePushSubscription(payload: { installation_id: string; platform?: string; endpoint: string; p256dh: string; auth: string }): Promise<void> {
  await http.post('/notifications/push-subscriptions', payload)
}
