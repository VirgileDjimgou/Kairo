import http from './http'
import type { ContributionRecordResponse } from './contributions.api'

export interface MembershipProfileResponse {
  id: string
  tenant_id: string
  user_id: string | null
  member_code: string
  first_name: string
  last_name: string
  display_name: string
  email: string | null
  phone: string | null
  status: string
  joined_at: string
  created_at: string
  updated_at: string
}

export interface MemberBalanceResponse {
  profile: MembershipProfileResponse
  total_expected: string
  total_paid: string
  total_balance: string
  contribution_count: number
}

export interface MemberStatementResponse {
  profile: MembershipProfileResponse
  summary: MemberBalanceResponse
  contributions: ContributionRecordResponse[]
}

export interface CreateMemberPayload {
  member_code: string
  first_name: string
  last_name: string
  display_name: string
  email?: string
  phone?: string
  status?: string
}

export interface UpdateMemberPayload {
  member_code?: string
  first_name?: string
  last_name?: string
  display_name?: string
  email?: string
  phone?: string
  status?: string
}

export async function getMyProfile(): Promise<MembershipProfileResponse> {
  const response = await http.get<MembershipProfileResponse>('/memberships/me')
  return response.data
}

export async function getMyBalance(): Promise<MemberBalanceResponse> {
  const response = await http.get<MemberBalanceResponse>('/memberships/me/balance')
  return response.data
}

export async function getMyContributions(): Promise<ContributionRecordResponse[]> {
  const response = await http.get<ContributionRecordResponse[]>('/memberships/me/contributions')
  return response.data
}

export async function getMyStatement(): Promise<MemberStatementResponse> {
  const response = await http.get<MemberStatementResponse>('/memberships/me/statement')
  return response.data
}

export async function downloadMyStatementPdf(): Promise<Blob> {
  const response = await http.get('/memberships/me/statement.pdf', { responseType: 'blob' })
  return response.data
}

export async function listMembers(): Promise<MembershipProfileResponse[]> {
  const response = await http.get<MembershipProfileResponse[]>('/memberships/')
  return response.data
}

export async function getMember(profileId: string): Promise<MembershipProfileResponse> {
  const response = await http.get<MembershipProfileResponse>(`/memberships/${profileId}`)
  return response.data
}

export async function getMemberBalance(profileId: string): Promise<MemberBalanceResponse> {
  const response = await http.get<MemberBalanceResponse>(`/memberships/${profileId}/balance`)
  return response.data
}

export async function createMember(payload: CreateMemberPayload): Promise<MembershipProfileResponse> {
  const response = await http.post<MembershipProfileResponse>('/memberships/', payload)
  return response.data
}

export async function updateMember(profileId: string, payload: UpdateMemberPayload): Promise<MembershipProfileResponse> {
  const response = await http.patch<MembershipProfileResponse>(`/memberships/${profileId}`, payload)
  return response.data
}

export async function deleteMember(profileId: string): Promise<void> {
  await http.delete(`/memberships/${profileId}`)
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

export async function importMembersCsv(file: File, dryRun = false): Promise<ImportResult> {
  const formData = new FormData()
  formData.append('file', file)
  const params = dryRun ? { dry_run: 'true' } : {}
  const response = await http.post<ImportResult>('/memberships/import', formData, { params })
  return response.data
}

export async function exportMembersCsv(): Promise<Blob> {
  const response = await http.get('/memberships/export', { responseType: 'blob' })
  return response.data
}
