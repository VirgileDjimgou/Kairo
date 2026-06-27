import http from './http'

export interface LoginRequest {
  email: string
  password: string
  tenant_slug?: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
  tenant_id: string
  user_id: string
}

export interface UserResponse {
  id: string
  email: string
  display_name: string
  status: string
  tenant_id: string
  roles: string[]
  last_login_at: string | null
}

export async function login(payload: LoginRequest): Promise<TokenResponse> {
  const response = await http.post<TokenResponse>('/auth/login', payload)
  return response.data
}

export async function getMe(): Promise<UserResponse> {
  const response = await http.get<UserResponse>('/auth/me')
  return response.data
}
