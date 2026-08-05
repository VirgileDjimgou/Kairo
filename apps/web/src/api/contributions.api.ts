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

export type TreasuryExpenseCategory = 'sport_equipment' | 'fuel_transport' | 'tournament' | 'cultural_event' | 'administration' | 'other'

export interface ExpenseRecordResponse {
  id: string
  tenant_id: string
  category: TreasuryExpenseCategory
  amount: string
  currency: string
  spent_at: string
  description: string
  payee: string | null
  payment_method: string
  reference: string | null
  created_by: string | null
  created_at: string
}

export interface CreateExpensePayload {
  category: TreasuryExpenseCategory
  amount: string
  currency?: string
  spent_at?: string | null
  description: string
  payee?: string | null
  payment_method?: string
  reference?: string | null
}

export interface BudgetCategoryTotal {
  category: string
  amount: string
}

export interface AnnualBudgetResponse {
  year: number
  currency: string
  income_total: string
  expense_total: string
  available_balance: string
  income_by_category: BudgetCategoryTotal[]
  expenses_by_category: BudgetCategoryTotal[]
  recent_expenses: ExpenseRecordResponse[]
}

export type ContributionReceiptStatus = 'draft' | 'submitted' | 'clarification_requested' | 'validated' | 'partially_validated' | 'rejected' | 'cancelled'
export type FinancialIncomeType = 'membership_contribution' | 'donation' | 'sponsorship' | 'tournament_proceeds' | 'other_income' | 'disciplinary_payment'
export type CashHandoverStatus = 'pending_handover' | 'handover_reported' | 'received_in_treasury'

export interface ContributionReceiptDeclarationResponse {
  id: string
  tenant_id: string
  membership_profile_id: string | null
  income_type: FinancialIncomeType
  source_name: string | null
  disciplinary_record_id: string | null
  declarant_user_id: string
  declarant_role_code: string
  amount: string
  currency: string
  received_at: string
  payment_method: string
  note: string | null
  reference: string | null
  evidence_json: string
  status: ContributionReceiptStatus
  submitted_at: string | null
  processed_at: string | null
  processed_by_user_id: string | null
  processed_amount: string | null
  processing_note: string | null
  contribution_record_id: string | null
  payment_record_id: string | null
  cash_handover_status: CashHandoverStatus | null
  handover_reminder_days: number | null
  handover_due_at: string | null
  handover_reminder_updated_at: string | null
  handover_reminder_sent_at: string | null
  handover_reported_at: string | null
  handover_reported_by_user_id: string | null
  handover_method: string | null
  treasury_received_at: string | null
  treasury_received_by_user_id: string | null
  treasury_receipt_note: string | null
  created_at: string
  updated_at: string
}

export interface CreateContributionReceiptDeclarationPayload {
  membership_profile_id?: string | null
  income_type?: FinancialIncomeType
  source_name?: string | null
  disciplinary_record_id?: string | null
  amount: string
  currency?: string
  received_at?: string | null
  payment_method?: string
  note?: string | null
  reference?: string | null
  evidence_json?: string
}

export interface ContributionReceiptMemberOption {
  id: string
  display_name: string
  member_code: string
  first_name: string
  last_name: string
  email: string | null
  phone: string | null
  membership_type: string
  status: string
  joined_at: string
}

export interface ProcessContributionReceiptDeclarationPayload {
  action: 'validated' | 'partially_validated' | 'rejected' | 'clarification_requested' | 'cancelled'
  contribution_record_id?: string
  processed_amount?: string
  note?: string
  handover_reminder_days?: number
}

export interface ReportContributionReceiptHandoverPayload { method: 'cash' | 'bank_transfer'; note?: string | null }
export interface UpdateContributionReceiptHandoverReminderPayload { reminder_days: number }
export interface ConfirmContributionReceiptInTreasuryPayload { method?: 'cash' | 'bank_transfer'; note?: string | null }

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

export async function getAnnualBudget(year: number): Promise<AnnualBudgetResponse> {
  const response = await http.get<AnnualBudgetResponse>('/contributions/annual-budget', { params: { year } })
  return response.data
}

export async function createExpense(payload: CreateExpensePayload): Promise<ExpenseRecordResponse> {
  const response = await http.post<ExpenseRecordResponse>('/contributions/expenses', payload)
  return response.data
}

export async function createContributionReceiptDeclaration(payload: CreateContributionReceiptDeclarationPayload): Promise<ContributionReceiptDeclarationResponse> {
  const response = await http.post<ContributionReceiptDeclarationResponse>('/contributions/receipt-declarations', payload)
  return response.data
}

export async function listMyContributionReceiptDeclarations(): Promise<ContributionReceiptDeclarationResponse[]> {
  const response = await http.get<ContributionReceiptDeclarationResponse[]>('/contributions/receipt-declarations/mine')
  return response.data
}

export async function listMemberContributionReceiptDeclarations(): Promise<ContributionReceiptDeclarationResponse[]> {
  const response = await http.get<ContributionReceiptDeclarationResponse[]>('/contributions/receipt-declarations/me')
  return response.data
}

export async function listContributionReceiptDeclarations(): Promise<ContributionReceiptDeclarationResponse[]> {
  const response = await http.get<ContributionReceiptDeclarationResponse[]>('/contributions/receipt-declarations')
  return response.data
}

export async function listContributionReceiptDeclarationMemberOptions(): Promise<ContributionReceiptMemberOption[]> {
  const response = await http.get<ContributionReceiptMemberOption[]>('/contributions/receipt-declarations/member-options')
  return response.data
}

export async function submitContributionReceiptDeclaration(id: string): Promise<ContributionReceiptDeclarationResponse> {
  const response = await http.post<ContributionReceiptDeclarationResponse>(`/contributions/receipt-declarations/${id}/submit`)
  return response.data
}

export async function processContributionReceiptDeclaration(id: string, payload: ProcessContributionReceiptDeclarationPayload): Promise<ContributionReceiptDeclarationResponse> {
  const response = await http.post<ContributionReceiptDeclarationResponse>(`/contributions/receipt-declarations/${id}/process`, payload)
  return response.data
}

export async function reportContributionReceiptHandover(id: string, payload: ReportContributionReceiptHandoverPayload): Promise<ContributionReceiptDeclarationResponse> {
  const response = await http.post<ContributionReceiptDeclarationResponse>(`/contributions/receipt-declarations/${id}/handover`, payload)
  return response.data
}

export async function updateContributionReceiptHandoverReminder(id: string, payload: UpdateContributionReceiptHandoverReminderPayload): Promise<ContributionReceiptDeclarationResponse> {
  const response = await http.post<ContributionReceiptDeclarationResponse>(`/contributions/receipt-declarations/${id}/handover-reminder`, payload)
  return response.data
}

export async function confirmContributionReceiptInTreasury(id: string, payload: ConfirmContributionReceiptInTreasuryPayload = {}): Promise<ContributionReceiptDeclarationResponse> {
  const response = await http.post<ContributionReceiptDeclarationResponse>(`/contributions/receipt-declarations/${id}/confirm-treasury-receipt`, payload)
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

export type MemberFinanceExportFormat = 'xlsx' | 'pdf' | 'whatsapp'

export async function exportMemberFinanceReport(
  format: MemberFinanceExportFormat,
  year: number,
): Promise<Blob> {
  const response = await http.get(`/contributions/report/export/${format}`, {
    params: { year },
    responseType: 'blob',
  })
  return response.data
}
