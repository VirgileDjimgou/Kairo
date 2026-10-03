import { ref } from 'vue'
import http from '@/api/http'
import type { TenantBranding } from '@/api/branding.types'

export interface HostTenantResolution {
  tenant_id: string
  slug: string
  name: string
  default_language: string
  branding: Partial<TenantBranding>
  manifest_url: string
}

/**
 * Tenant resolved from the request host by the backend (exact custom domain or
 * direct platform subdomain). The client never supplies a tenant override; an
 * unmapped host resolves to `null` and the platform defaults apply.
 */
export const hostTenant = ref<HostTenantResolution | null>(null)

export async function resolveHostTenant(): Promise<HostTenantResolution | null> {
  try {
    // A 404 means "no tenant mapped to this host" and is a normal outcome:
    // suppress operation failure notifications for this background probe.
    const { data } = await http.get<HostTenantResolution>('/tenants/public/resolve', {
      headers: { 'X-Kairo-Operation-Failure-Log': '1' },
    })
    hostTenant.value = data
    return data
  } catch {
    hostTenant.value = null
    return null
  }
}
