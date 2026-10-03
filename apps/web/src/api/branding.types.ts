/**
 * Canonical tenant branding contract (mirrors the FastAPI `TenantBranding`).
 * Platform identity and tenant identity are separate; these values are
 * presentation only and never influence authorization or business logic.
 */
export interface TenantBranding {
  display_name: string
  short_name: string
  legal_name: string
  logo_url: string
  logo_dark_url: string
  favicon_url: string
  icon_192_url: string
  icon_512_url: string
  maskable_icon_url: string
  primary_color: string
  secondary_color: string
  background_color: string
  theme_color: string
  notification_name: string
  support_name: string
  support_email: string
  custom_domain: string
}

/** Safe Kairo defaults, identical to the backend defaults. */
export const KAIRO_BRANDING_DEFAULTS: TenantBranding = {
  display_name: 'Kairo',
  short_name: 'Kairo',
  legal_name: '',
  logo_url: '',
  logo_dark_url: '',
  favicon_url: '',
  icon_192_url: '',
  icon_512_url: '',
  maskable_icon_url: '',
  primary_color: '#1f4f8f',
  secondary_color: '#2f6f55',
  background_color: '#f8f9fb',
  theme_color: '#1a3f6b',
  notification_name: 'Kairo',
  support_name: 'Kairo Support',
  support_email: '',
  custom_domain: '',
}
