import http from './http'

export interface DisciplinaryRecordResponse {
  id: string
  tenant_id: string
  membership_profile_id: string
  membership_display_name: string | null
  policy_record_id: string | null
  policy_title: string | null
  title: string
  description: string | null
  amount: string
  currency: string
  status: string
  recorded_by: string | null
  recorded_at: string
  created_at: string
  updated_at: string
}

export interface CreateDisciplinaryPayload {
  membership_profile_id: string
  policy_record_id?: string | null
  title: string
  description?: string | null
  amount?: string
  currency?: string
  status?: string
}

export interface UpdateDisciplinaryPayload {
  policy_record_id?: string | null
  title?: string
  description?: string | null
  amount?: string
  currency?: string
  status?: string
}

export async function listMyDisciplinaryRecords(): Promise<DisciplinaryRecordResponse[]> {
  const response = await http.get<DisciplinaryRecordResponse[]>('/disciplinary/me')
  return response.data
}

export async function listDisciplinaryRecords(): Promise<DisciplinaryRecordResponse[]> {
  const response = await http.get<DisciplinaryRecordResponse[]>('/disciplinary/')
  return response.data
}

export async function getDisciplinaryRecord(recordId: string): Promise<DisciplinaryRecordResponse> {
  const response = await http.get<DisciplinaryRecordResponse>(`/disciplinary/${recordId}`)
  return response.data
}

export async function createDisciplinaryRecord(payload: CreateDisciplinaryPayload): Promise<DisciplinaryRecordResponse> {
  const response = await http.post<DisciplinaryRecordResponse>('/disciplinary/', payload)
  return response.data
}

export async function updateDisciplinaryRecord(recordId: string, payload: UpdateDisciplinaryPayload): Promise<DisciplinaryRecordResponse> {
  const response = await http.patch<DisciplinaryRecordResponse>(`/disciplinary/${recordId}`, payload)
  return response.data
}

export async function deleteDisciplinaryRecord(recordId: string): Promise<void> {
  await http.delete(`/disciplinary/${recordId}`)
}
