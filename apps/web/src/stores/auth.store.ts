import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { login as apiLogin, getMe } from '@/api/auth.api'
import type {
  MfaRequiredResponse,
  MfaCompleteLoginRequest,
  MfaLoginResponse,
  UserWithMembershipsResponse,
} from '@/api/auth.api'
import { useTenantStore } from '@/stores/tenant.store'
import { completeMfaLogin as apiCompleteMfaLogin } from '@/api/auth.api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<UserWithMembershipsResponse | null>(null)
  const mfaToken = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)
  const needsMfa = computed(() => !!mfaToken.value)
  const hasRole = (role: string) => computed(() => user.value?.roles?.includes(role) ?? false)
  const hasAnyRole = (roles: string[]) =>
    computed(() => roles.some((role) => user.value?.roles?.includes(role) ?? false))

  async function login(email: string, password: string, tenantSlug?: string): Promise<boolean | string> {
    const data = await apiLogin({ email, password, tenant_slug: tenantSlug })

    if ('mfa_required' in data && data.mfa_required) {
      mfaToken.value = data.mfa_token
      return 'mfa_required'
    }

    const tokenData = data as import('@/api/auth.api').TokenResponse
    token.value = tokenData.access_token
    localStorage.setItem('access_token', tokenData.access_token)
    mfaToken.value = null
    await fetchMe()
    return true
  }

  async function completeMfa(code: string): Promise<boolean> {
    if (!mfaToken.value) return false
    const data = await apiCompleteMfaLogin({ mfa_token: mfaToken.value, code })
    token.value = data.access_token
    localStorage.setItem('access_token', data.access_token)
    mfaToken.value = null
    await fetchMe()
    return true
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      const profile = await getMe()
      user.value = profile
      const tenantStore = useTenantStore()
      tenantStore.setMemberships(profile.memberships, profile.tenant_id)
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    mfaToken.value = null
    localStorage.removeItem('access_token')
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
    isAuthenticated,
    needsMfa,
    hasRole,
    hasAnyRole,
    login,
    completeMfa,
    logout,
    fetchMe,
    restoreSession,
  }
})
