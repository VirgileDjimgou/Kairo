import http from './http'

export interface PolicyRecordResponse {
  id: string
  tenant_id: string
  title: string
  category: string
  description: string | null
  document_id: string | null
  document_title: string | null
  status: string
  created_by: string | null
  created_at: string
  updated_at: string
}

export interface PolicyCategoryResponse {
  categories: string[]
}

export interface CreatePolicyPayload {
  title: string
  category: string
  description?: string | null
  document_id?: string | null
  status?: string
}

export interface UpdatePolicyPayload {
  title?: string
  category?: string
  description?: string | null
  document_id?: string | null
  status?: string
}

export async function listPublicPolicies(): Promise<PolicyRecordResponse[]> {
  const response = await http.get<PolicyRecordResponse[]>('/policies/public')
  return response.data
}

export async function listPolicies(): Promise<PolicyRecordResponse[]> {
  const response = await http.get<PolicyRecordResponse[]>('/policies/')
  return response.data
}

export async function listPolicyCategories(): Promise<PolicyCategoryResponse> {
  const response = await http.get<PolicyCategoryResponse>('/policies/categories')
  return response.data
}

export async function getPolicy(policyId: string): Promise<PolicyRecordResponse> {
  const response = await http.get<PolicyRecordResponse>(`/policies/${policyId}`)
  return response.data
}

export async function createPolicy(payload: CreatePolicyPayload): Promise<PolicyRecordResponse> {
  const response = await http.post<PolicyRecordResponse>('/policies/', payload)
  return response.data
}

export async function updatePolicy(policyId: string, payload: UpdatePolicyPayload): Promise<PolicyRecordResponse> {
  const response = await http.patch<PolicyRecordResponse>(`/policies/${policyId}`, payload)
  return response.data
}

export async function deletePolicy(policyId: string): Promise<void> {
  await http.delete(`/policies/${policyId}`)
}
