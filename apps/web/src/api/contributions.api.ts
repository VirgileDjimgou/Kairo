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

export async function getContributionSummary(year?: number): Promise<ContributionSummary> {
  const params = year ? { year } : {}
  const response = await http.get<ContributionSummary>('/contributions/summary', { params })
  return response.data
}
