import http from './http'

// ── Existing types ────────────────────────────────────────────────────────────

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

export interface MfaRequiredResponse {
  mfa_required: true
  mfa_token: string
  expires_in: number
}

export interface BrandingConfig {
  primary_color: string
  logo_url: string
}

export interface ModuleToggles {
  membership: boolean
  contributions: boolean
  policies: boolean
  disciplinary: boolean
  events: boolean
  announcements: boolean
  chat: boolean
  notifications: boolean
}

export interface TenantMembershipResponse {
  tenant_id: string
  slug: string
  name: string
  roles: string[]
  branding: BrandingConfig
  modules: ModuleToggles
  profile_type: string
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

export interface UserWithMembershipsResponse extends UserResponse {
  memberships: TenantMembershipResponse[]
}

export interface SwitchTenantRequest {
  tenant_id: string
}

export interface SwitchTenantResponse {
  access_token: string
  token_type: string
  expires_in: number
  tenant_id: string
  user_id: string
  memberships: TenantMembershipResponse[]
}

// ── Invitation types ──────────────────────────────────────────────────────────

export interface InviteRequest {
  email: string
  role_code: string
  tenant_id: string
}

export interface InviteResponse {
  invitation_id: string
  email: string
  role_code: string
  status: string
  expires_at: string
  invite_token: string
}

export interface AcceptInviteRequest {
  token: string
  display_name: string
  password: string
}

export interface AcceptInviteResponse {
  access_token: string
  token_type: string
  expires_in: number
  tenant_id: string
  user_id: string
}

export interface InvitationStatusResponse {
  id: string
  email: string
  role_code: string
  status: string
  expires_at: string
  created_at: string
}

// ── Password Reset types ──────────────────────────────────────────────────────

export interface ForgotPasswordRequest {
  email: string
}

export interface ForgotPasswordResponse {
  message: string
  reset_token: string | null
}

export interface ResetPasswordRequest {
  token: string
  new_password: string
}

// ── MFA types ─────────────────────────────────────────────────────────────────

export interface MfaEnrollResponse {
  secret: string
  uri: string
  qr_code_url: string
}

export interface MfaVerifyRequest {
  code: string
}

export interface MfaCompleteLoginRequest {
  mfa_token: string
  code: string
}

export interface MfaLoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  tenant_id: string
  user_id: string
}

// ── Refresh types ─────────────────────────────────────────────────────────────

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface RefreshTokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

// ── API functions ─────────────────────────────────────────────────────────────

export async function login(payload: LoginRequest): Promise<TokenResponse | MfaRequiredResponse> {
  const response = await http.post<TokenResponse | MfaRequiredResponse>('/auth/login', payload)
  return response.data
}

export async function getMe(): Promise<UserWithMembershipsResponse> {
  const response = await http.get<UserWithMembershipsResponse>('/auth/me')
  return response.data
}

export async function switchTenant(payload: SwitchTenantRequest): Promise<SwitchTenantResponse> {
  const response = await http.post<SwitchTenantResponse>('/auth/switch-tenant', payload)
  return response.data
}

export async function inviteUser(payload: InviteRequest): Promise<InviteResponse> {
  const response = await http.post<InviteResponse>('/auth/invite', payload)
  return response.data
}

export async function acceptInvite(payload: AcceptInviteRequest): Promise<AcceptInviteResponse> {
  const response = await http.post<AcceptInviteResponse>('/auth/accept-invite', payload)
  return response.data
}

export async function listInvitations(tenantId: string): Promise<InvitationStatusResponse[]> {
  const response = await http.get<InvitationStatusResponse[]>(`/auth/invitations/${tenantId}`)
  return response.data
}

export async function cancelInvitation(invitationId: string): Promise<void> {
  await http.delete(`/auth/invitations/${invitationId}`)
}

export async function forgotPassword(payload: ForgotPasswordRequest): Promise<ForgotPasswordResponse> {
  const response = await http.post<ForgotPasswordResponse>('/auth/forgot-password', payload)
  return response.data
}

export async function resetPassword(payload: ResetPasswordRequest): Promise<void> {
  await http.post('/auth/reset-password', payload)
}

export async function enrollMfa(): Promise<MfaEnrollResponse> {
  const response = await http.post<MfaEnrollResponse>('/auth/mfa/enroll')
  return response.data
}

export async function verifyMfa(payload: MfaVerifyRequest): Promise<void> {
  await http.post('/auth/mfa/verify', payload)
}

export async function disableMfa(): Promise<void> {
  await http.delete('/auth/mfa')
}

export async function completeMfaLogin(payload: MfaCompleteLoginRequest): Promise<MfaLoginResponse> {
  const response = await http.post<MfaLoginResponse>('/auth/mfa/complete', payload)
  return response.data
}

export async function refreshToken(payload: RefreshTokenRequest): Promise<RefreshTokenResponse> {
  const response = await http.post<RefreshTokenResponse>('/auth/refresh', payload)
  return response.data
}
