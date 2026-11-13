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
  account_id: string | null
  receipt_number: string | null
  reversed_at: string | null
  reversed_by: string | null
  reversal_reason: string | null
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
  category: string
  amount: string
  currency: string
  spent_at: string
  description: string
  payee: string | null
  payment_method: string
  reference: string | null
  account_id: string | null
  reversed_at: string | null
  reversed_by: string | null
  reversal_reason: string | null
  status: 'recorded' | 'approved' | 'rejected'
  approved_at: string | null
  approved_by: string | null
  approval_note: string | null
  attachment_file_name: string | null
  attachment_content_type: string | null
  attachment_size_bytes: number | null
  attachment_uploaded_at: string | null
  created_by: string | null
  created_at: string
}

export interface CreateExpensePayload {
  category: string
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
  planned_amount: string
  variance: string
}

export interface AnnualBudgetResponse {
  year: number
  currency: string
  income_total: string
  expense_total: string
  available_balance: string
  planned_income_total: string
  planned_expense_total: string
  income_variance: string
  expense_variance: string
  income_by_category: BudgetCategoryTotal[]
  expenses_by_category: BudgetCategoryTotal[]
  recent_expenses: ExpenseRecordResponse[]
}

export interface ExpenseCategoryResponse {
  id: string
  code: string
  name: string
  is_default: boolean
  is_active: boolean
}

export interface FinanceAccountResponse {
  id: string
  name: string
  kind: 'cash' | 'bank' | 'other'
  is_default: boolean
}

export interface TreasuryPositionAccount {
  account_id: string | null
  name: string
  kind: string
  opening_balance: string
  inflow: string
  outflow: string
  pending_custody: string
  closing_balance: string
}

export interface TreasuryPositionResponse {
  year: number
  currency: string
  accounts: TreasuryPositionAccount[]
  total_opening: string
  total_inflow: string
  total_outflow: string
  total_pending_custody: string
  total_closing: string
}

export interface BudgetPlanLine {
  direction: 'income' | 'expense'
  category: string
  planned_amount: string
}

export interface BudgetPlanResponse {
  year: number
  currency: string
  lines: BudgetPlanLine[]
  planned_income_total: string
  planned_expense_total: string
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

export async function listExpenseCategories(): Promise<ExpenseCategoryResponse[]> {
  const response = await http.get<ExpenseCategoryResponse[]>('/contributions/expense-categories')
  return response.data
}

export async function createExpenseCategory(name: string): Promise<ExpenseCategoryResponse> {
  const response = await http.post<ExpenseCategoryResponse>('/contributions/expense-categories', { name })
  return response.data
}

export async function listFinanceAccounts(): Promise<FinanceAccountResponse[]> {
  const response = await http.get<FinanceAccountResponse[]>('/contributions/accounts')
  return response.data
}

export async function getTreasuryPosition(year: number): Promise<TreasuryPositionResponse> {
  const response = await http.get<TreasuryPositionResponse>('/contributions/treasury-position', {
    params: { year },
  })
  return response.data
}

export async function setOpeningBalance(
  accountId: string,
  year: number,
  amount: string,
): Promise<TreasuryPositionResponse> {
  const response = await http.put<TreasuryPositionResponse>(
    `/contributions/accounts/${accountId}/opening-balance/${year}`,
    { amount },
  )
  return response.data
}

export async function getBudgetPlan(year: number): Promise<BudgetPlanResponse> {
  const response = await http.get<BudgetPlanResponse>('/contributions/budget-plan', {
    params: { year },
  })
  return response.data
}

export async function setBudgetPlan(
  year: number,
  lines: BudgetPlanLine[],
): Promise<BudgetPlanResponse> {
  const response = await http.put<BudgetPlanResponse>(`/contributions/budget-plan/${year}`, {
    lines,
  })
  return response.data
}

export async function downloadPaymentReceipt(paymentId: string): Promise<Blob> {
  const response = await http.get(`/contributions/payments/${paymentId}/receipt.pdf`, {
    responseType: 'blob',
  })
  return response.data
}

export async function exportFinanceJournal(year: number): Promise<Blob> {
  const response = await http.get('/contributions/journal/export', {
    params: { year },
    responseType: 'blob',
  })
  return response.data
}

export async function createExpense(payload: CreateExpensePayload): Promise<ExpenseRecordResponse> {
  const response = await http.post<ExpenseRecordResponse>('/contributions/expenses', payload)
  return response.data
}

export interface ExpenseListParams {
  year?: number
  category?: TreasuryExpenseCategory
  limit?: number
  offset?: number
}

export async function listExpenses(params: ExpenseListParams = {}): Promise<ExpenseRecordResponse[]> {
  const response = await http.get<ExpenseRecordResponse[]>('/contributions/expenses', { params })
  return response.data
}

export async function getExpense(expenseId: string): Promise<ExpenseRecordResponse> {
  const response = await http.get<ExpenseRecordResponse>(`/contributions/expenses/${expenseId}`)
  return response.data
}

export async function reverseExpense(expenseId: string, reason: string): Promise<ExpenseRecordResponse> {
  const response = await http.post<ExpenseRecordResponse>(`/contributions/expenses/${expenseId}/reverse`, { reason })
  return response.data
}

export async function approveExpense(expenseId: string): Promise<ExpenseRecordResponse> {
  const response = await http.post<ExpenseRecordResponse>(`/contributions/expenses/${expenseId}/approve`)
  return response.data
}

export async function rejectExpense(expenseId: string, note: string): Promise<ExpenseRecordResponse> {
  const response = await http.post<ExpenseRecordResponse>(`/contributions/expenses/${expenseId}/reject`, { note })
  return response.data
}

export async function exportExpenses(year: number, format: 'csv' | 'xlsx' = 'csv'): Promise<Blob> {
  const response = await http.get('/contributions/expenses/export', {
    params: { year, export_format: format },
    responseType: 'blob',
  })
  return response.data
}

export async function uploadExpenseAttachment(expenseId: string, file: File): Promise<ExpenseRecordResponse> {
  const formData = new FormData()
  formData.append('file', file)
  const response = await http.post<ExpenseRecordResponse>(
    `/contributions/expenses/${expenseId}/attachment`,
    formData,
  )
  return response.data
}

export async function downloadExpenseAttachment(expenseId: string): Promise<Blob> {
  const response = await http.get(`/contributions/expenses/${expenseId}/attachment`, {
    responseType: 'blob',
  })
  return response.data
}

export interface FinancePeriodResponse {
  year: number
  status: 'open' | 'closed'
  closed_at: string | null
  closed_by: string | null
  reopened_at: string | null
  reopen_reason: string | null
}

export async function getFinancePeriod(year: number): Promise<FinancePeriodResponse> {
  const response = await http.get<FinancePeriodResponse>(`/contributions/periods/${year}`)
  return response.data
}

export async function closeFinancePeriod(year: number): Promise<FinancePeriodResponse> {
  const response = await http.post<FinancePeriodResponse>(`/contributions/periods/${year}/close`)
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
  row_number: number
  message: string
  column?: string | null
  value?: string | null
}

export interface ImportResult {
  total_rows: number
  success_count: number
  error_count: number
  skipped_count: number
  errors: ImportRowError[]
  dry_run: boolean
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
