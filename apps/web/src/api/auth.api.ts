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

export interface ActiveSessionResponse {
  id: string
  current: boolean
  current_tenant_id: string
  created_at: string
  last_seen_at: string
  created_ip: string | null
  last_seen_ip: string | null
  created_user_agent: string | null
  last_seen_user_agent: string | null
}

export interface SessionActionResponse {
  message: string
  revoked_session_count: number
}

export interface SecurityEventResponse {
  id: string
  action: string
  actor_user_id: string | null
  entity_type: string
  entity_id: string | null
  details: Record<string, unknown>
  created_at: string
}

export interface ManagedTenantUserResponse {
  user_id: string
  email: string
  display_name: string
  profile_type: string
  membership_status: string
  user_status: string
  roles: string[]
  last_login_at: string | null
  active_session_count: number
  last_security_event_action: string | null
  last_security_event_at: string | null
}

export interface ManagedTenantUserActionResponse {
  message: string
  membership_status: string
  revoked_session_count: number
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
  delivery_status: string
  delivery_message: string | null
  delivery_simulation_only: boolean
  invite_token: string | null
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

export interface MfaStatusResponse {
  enabled: boolean
  enrolled: boolean
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

export async function listActiveSessions(): Promise<ActiveSessionResponse[]> {
  const response = await http.get<ActiveSessionResponse[]>('/auth/sessions')
  return response.data
}

export async function revokeOtherSessions(): Promise<SessionActionResponse> {
  const response = await http.post<SessionActionResponse>('/auth/sessions/revoke-others')
  return response.data
}

export async function revokeAllSessions(): Promise<SessionActionResponse> {
  const response = await http.post<SessionActionResponse>('/auth/sessions/revoke-all')
  return response.data
}

export async function revokeSession(sessionId: string): Promise<SessionActionResponse> {
  const response = await http.delete<SessionActionResponse>(`/auth/sessions/${sessionId}`)
  return response.data
}

export async function listSecurityEvents(): Promise<SecurityEventResponse[]> {
  const response = await http.get<SecurityEventResponse[]>('/auth/security-events')
  return response.data
}

export async function listManagedUsers(tenantId: string): Promise<ManagedTenantUserResponse[]> {
  const response = await http.get<ManagedTenantUserResponse[]>(`/auth/admin/managed-users/${tenantId}`)
  return response.data
}

export async function suspendManagedUser(userId: string): Promise<ManagedTenantUserActionResponse> {
  const response = await http.post<ManagedTenantUserActionResponse>(`/auth/admin/managed-users/${userId}/suspend`)
  return response.data
}

export async function reactivateManagedUser(userId: string): Promise<ManagedTenantUserActionResponse> {
  const response = await http.post<ManagedTenantUserActionResponse>(`/auth/admin/managed-users/${userId}/reactivate`)
  return response.data
}

export async function revokeManagedUserSessions(userId: string): Promise<ManagedTenantUserActionResponse> {
  const response = await http.post<ManagedTenantUserActionResponse>(`/auth/admin/managed-users/${userId}/revoke-sessions`)
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

export async function getMfaStatus(): Promise<MfaStatusResponse> {
  const response = await http.get<MfaStatusResponse>('/auth/mfa/status')
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
