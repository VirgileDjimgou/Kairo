import http from './http'

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

export interface TenantSettingsResponse {
  tenant_id: string
  name: string
  slug: string
  default_language: string
  branding: BrandingConfig
  modules: ModuleToggles
  updated_at: string
}

export interface TenantSettingsUpdate {
  name?: string
  default_language?: string
  branding?: Partial<BrandingConfig>
  modules?: Partial<ModuleToggles>
}

export interface RoleResponse {
  id: string
  tenant_id: string
  code: string
  name: string
  description: string | null
  is_system_role: boolean
}

export async function getTenantSettings(tenantId: string): Promise<TenantSettingsResponse> {
  const { data } = await http.get(`/tenants/${tenantId}/settings`)
  return data
}

export async function updateTenantSettings(
  tenantId: string,
  settings: TenantSettingsUpdate,
): Promise<TenantSettingsResponse> {
  const { data } = await http.put(`/tenants/${tenantId}/settings`, settings)
  return data
}

export async function getTenantRoles(tenantId: string): Promise<RoleResponse[]> {
  const { data } = await http.get(`/tenants/${tenantId}/roles`)
  return data
}

export async function checkModuleHasData(tenantId: string, module: string): Promise<boolean> {
  const { data } = await http.get(`/admin/module-has-data`, { params: { module } })
  return data.has_data
}
