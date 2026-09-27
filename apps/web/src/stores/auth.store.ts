import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { login as apiLogin, getMe, updateLanguagePreference as apiUpdateLanguagePreference } from '@/api/auth.api'
import type {
  UserWithMembershipsResponse,
} from '@/api/auth.api'
import { useTenantStore } from '@/stores/tenant.store'
import { completeMfaLogin as apiCompleteMfaLogin } from '@/api/auth.api'
import { useLocaleStore } from '@/stores/locale.store'
import type { SupportedLocale } from '@/i18n/messages'
import { DEMO_TENANT_SLUG } from '@/config/demoAccounts'
import { ROLE_CAPABILITY_BUNDLES } from '@/config/capabilityBundles'
import { revokeCurrentDevice } from '@/services/web-push'

const DEMO_SESSION_KEY = 'kairo_demo_session'

function deriveCapabilitiesFromRoles(roles: string[]): string[] {
  const merged = new Set<string>()
  for (const role of roles) {
    for (const capability of ROLE_CAPABILITY_BUNDLES[role] ?? []) {
      merged.add(capability)
    }
  }
  return [...merged]
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<UserWithMembershipsResponse | null>(null)
  const mfaToken = ref<string | null>(null)
  const isDemoSession = ref<boolean>(localStorage.getItem(DEMO_SESSION_KEY) === '1')

  const isAuthenticated = computed(() => !!token.value)
  const needsMfa = computed(() => !!mfaToken.value)
  const hasRole = (role: string) => computed(() => user.value?.roles?.includes(role) ?? false)
  const hasAnyRole = (roles: string[]) =>
    computed(() => roles.some((role) => user.value?.roles?.includes(role) ?? false))

  const capabilities = computed<string[]>(() => {
    const tenantStore = useTenantStore()
    const tenantCapabilities = tenantStore.currentTenant?.capabilities
    if (tenantCapabilities && tenantCapabilities.length > 0) return tenantCapabilities
    const userCapabilities = user.value?.capabilities
    if (userCapabilities && userCapabilities.length > 0) return userCapabilities
    return deriveCapabilitiesFromRoles(user.value?.roles ?? [])
  })
  const hasCapability = (capability: string) =>
    computed(() => capabilities.value.includes(capability))

  async function login(email: string, password: string, tenantSlug?: string): Promise<boolean | string> {
    const localeStore = useLocaleStore()
    const selectedLocale = localeStore.currentLocale
    const data = await apiLogin({
      email,
      password,
      ...(tenantSlug ? { tenant_slug: tenantSlug } : {}),
    })

    if ('mfa_required' in data && data.mfa_required) {
      mfaToken.value = data.mfa_token
      return 'mfa_required'
    }

    const tokenData = data as import('@/api/auth.api').TokenResponse
    token.value = tokenData.access_token
    localStorage.setItem('access_token', tokenData.access_token)
    mfaToken.value = null
    await fetchMe(selectedLocale)
    return true
  }

  async function completeMfa(code: string): Promise<boolean> {
    if (!mfaToken.value) return false
    const localeStore = useLocaleStore()
    const selectedLocale = localeStore.currentLocale
    const data = await apiCompleteMfaLogin({ mfa_token: mfaToken.value, code })
    token.value = data.access_token
    localStorage.setItem('access_token', data.access_token)
    mfaToken.value = null
    await fetchMe(selectedLocale)
    return true
  }

  /**
   * Starts a portfolio demo session for the given account. Demo sessions are
   * only ever created from the public `/demo` page and are flagged in storage
   * so the shell can display the demo banner.
   */
  async function loginAsDemo(email: string, password: string): Promise<boolean> {
    const result = await login(email, password, DEMO_TENANT_SLUG)
    if (result !== true) {
      return false
    }
    isDemoSession.value = true
    localStorage.setItem(DEMO_SESSION_KEY, '1')
    return true
  }

  async function fetchMe(preferredLocaleOverride?: SupportedLocale) {
    if (!token.value) return
    try {
      const profile = await getMe()
      user.value = profile
      const tenantStore = useTenantStore()
      tenantStore.setMemberships(profile.memberships, profile.tenant_id)
      const localeStore = useLocaleStore()
      const resolvedLocale = localeStore.resolvePreferredLocale({
        preferredLanguage: preferredLocaleOverride ?? profile.preferred_language,
        tenantDefaultLanguage: tenantStore.currentTenant?.default_language ?? null,
      })
      localeStore.applyLocale(resolvedLocale)
      if (preferredLocaleOverride || !profile.preferred_language || profile.preferred_language !== resolvedLocale) {
        try {
          const preference = await apiUpdateLanguagePreference({ preferred_language: resolvedLocale })
          if (user.value) {
            user.value.preferred_language = preference.preferred_language
          }
        } catch {
          if (user.value) {
            user.value.preferred_language = resolvedLocale
          }
        }
      }
    } catch {
      logout()
    }
  }

  async function updatePreferredLanguage(locale: SupportedLocale) {
    const localeStore = useLocaleStore()
    await localeStore.setLocale(locale, true)
    if (user.value) {
      user.value.preferred_language = locale
    }
  }

  function logout() {
    if (token.value) {
      // The installation identity survives; only this profile's push binding is
      // revoked so a signed-out browser stops receiving authenticated hints.
      void revokeCurrentDevice().catch(() => undefined)
    }
    token.value = null
    user.value = null
    mfaToken.value = null
    isDemoSession.value = false
    localStorage.removeItem('access_token')
    localStorage.removeItem(DEMO_SESSION_KEY)
    const tenantStore = useTenantStore()
    tenantStore.reset()
  }

  async function restoreSession() {
    if (!token.value) {
      const storedToken = localStorage.getItem('access_token')
      if (storedToken) {
        token.value = storedToken
      }
    }

    if (token.value && !user.value) {
      await fetchMe()
    }
  }

  return {
    token,
    user,
    mfaToken,
    isDemoSession,
    isAuthenticated,
    needsMfa,
    hasRole,
    hasAnyRole,
    capabilities,
    hasCapability,
    login,
    loginAsDemo,
    completeMfa,
    logout,
    fetchMe,
    restoreSession,
    updatePreferredLanguage,
  }
})
