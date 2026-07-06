import http from './http'

export interface ContributionRecordResponse {
  id: string
  tenant_id: string
  membership_profile_id: string
  year: number
  expected_amount: string
  paid_amount: string
  balance: string
  currency: string
  status: string
  due_date: string | null
  created_at: string
  updated_at: string
}

export interface PaymentRecordResponse {
  id: string
  tenant_id: string
  contribution_record_id: string
  amount: string
  currency: string
  paid_at: string
  payment_method: string
  reference: string | null
  recorded_by: string | null
  created_at: string
}

export interface ContributionReminderResponse {
  id: string
  tenant_id: string
  contribution_record_id: string
  membership_profile_id: string
  member_display_name: string
  member_code: string
  balance_snapshot: string
  due_date_snapshot: string | null
  channel: 'email'
  delivery_status: 'sent' | 'simulated' | 'failed' | 'skipped'
  recipient: string
  subject: string
  body: string
  provider_message: string | null
  reminded_by: string | null
  sent_at: string
  created_at: string
}

export interface CreateContributionPayload {
  membership_profile_id: string
  year: number
  expected_amount: string
  paid_amount: string
  currency?: string
  status?: string
  due_date?: string | null
}

export interface UpdateContributionPayload {
  expected_amount?: string
  paid_amount?: string
  currency?: string
  status?: string
  due_date?: string | null
}

export interface RecordPaymentPayload {
  contribution_record_id: string
  amount: string
  currency?: string
  paid_at?: string | null
  payment_method?: string
  reference?: string | null
}

export interface ContributionSummary {
  total_count: number
  total_expected: string
  total_paid: string
  total_balance: string
}

export interface SendContributionReminderPayload {
  channel?: 'email'
}

export interface SendContributionReminderBatchPayload {
  channel?: 'email'
  year?: number
  status?: string
  due_scope?: 'all_outstanding' | 'overdue' | 'due_soon'
  limit?: number
}

export interface ContributionReminderBatchResponse {
  attempted_count: number
  reminder_count: number
  reminders: ContributionReminderResponse[]
}

export async function listContributions(year?: number): Promise<ContributionRecordResponse[]> {
  const params = year ? { year } : {}
  const response = await http.get<ContributionRecordResponse[]>('/contributions/', { params })
  return response.data
}

export async function getContribution(contributionId: string): Promise<ContributionRecordResponse> {
  const response = await http.get<ContributionRecordResponse>(`/contributions/${contributionId}`)
  return response.data
}

export async function createContribution(payload: CreateContributionPayload): Promise<ContributionRecordResponse> {
  const response = await http.post<ContributionRecordResponse>('/contributions/', payload)
  return response.data
}

export async function updateContribution(contributionId: string, payload: UpdateContributionPayload): Promise<ContributionRecordResponse> {
  const response = await http.patch<ContributionRecordResponse>(`/contributions/${contributionId}`, payload)
  return response.data
}

export async function deleteContribution(contributionId: string): Promise<void> {
  await http.delete(`/contributions/${contributionId}`)
}

export async function listMemberContributions(profileId: string): Promise<ContributionRecordResponse[]> {
  const response = await http.get<ContributionRecordResponse[]>(`/contributions/by-member/${profileId}`)
  return response.data
}

export async function recordPayment(payload: RecordPaymentPayload): Promise<PaymentRecordResponse> {
  const response = await http.post<PaymentRecordResponse>('/contributions/payments', payload)
  return response.data
}

export async function listPayments(contributionId: string): Promise<PaymentRecordResponse[]> {
  const response = await http.get<PaymentRecordResponse[]>(`/contributions/${contributionId}/payments`)
  return response.data
}

export async function listTenantPayments(): Promise<PaymentRecordResponse[]> {
  const response = await http.get<PaymentRecordResponse[]>('/contributions/payments')
  return response.data
}

export async function listContributionReminders(year?: number): Promise<ContributionReminderResponse[]> {
  const params = year ? { year } : {}
  const response = await http.get<ContributionReminderResponse[]>('/contributions/reminders', { params })
  return response.data
}

export async function sendContributionReminder(
  contributionId: string,
  payload: SendContributionReminderPayload = {},
): Promise<ContributionReminderResponse> {
  const response = await http.post<ContributionReminderResponse>(
    `/contributions/${contributionId}/reminders/send`,
    { channel: payload.channel || 'email' },
  )
  return response.data
}

export async function sendContributionReminderBatch(
  payload: SendContributionReminderBatchPayload,
): Promise<ContributionReminderBatchResponse> {
  const response = await http.post<ContributionReminderBatchResponse>(
    '/contributions/reminders/send',
    {
      channel: payload.channel || 'email',
      year: payload.year,
      status: payload.status,
      due_scope: payload.due_scope || 'overdue',
      limit: payload.limit || 25,
    },
  )
  return response.data
}

export async function getContributionSummary(year?: number): Promise<ContributionSummary> {
  const params = year ? { year } : {}
  const response = await http.get<ContributionSummary>('/contributions/summary', { params })
  return response.data
}

export interface ImportRowError {
  row: number
  message: string
}

export interface ImportResult {
  total: number
  success_count: number
  error_count: number
  errors: ImportRowError[]
}

export async function importContributionsCsv(file: File, dryRun = false): Promise<ImportResult> {
  const formData = new FormData()
  formData.append('file', file)
  const params = dryRun ? { dry_run: 'true' } : {}
  const response = await http.post<ImportResult>('/contributions/import', formData, { params })
  return response.data
}

export async function exportContributionsCsv(year?: number): Promise<Blob> {
  const params = year ? { year } : {}
  const response = await http.get('/contributions/export', { params, responseType: 'blob' })
  return response.data
}

export async function exportFinanceReportCsv(): Promise<Blob> {
  const response = await http.get('/contributions/report/export', { responseType: 'blob' })
  return response.data
}
