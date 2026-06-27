import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { login as apiLogin, getMe } from '@/api/auth.api'
import type { UserResponse } from '@/api/auth.api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const user = ref<UserResponse | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(email: string, password: string, tenantSlug?: string) {
    const data = await apiLogin({ email, password, tenant_slug: tenantSlug })
    token.value = data.access_token
    localStorage.setItem('access_token', data.access_token)
    await fetchMe()
  }

  async function fetchMe() {
    if (!token.value) return
    try {
      user.value = await getMe()
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('access_token')
  }

  // Restore session on app load
  async function restoreSession() {
    if (token.value && !user.value) {
      await fetchMe()
    }
  }

  return { token, user, isAuthenticated, login, logout, fetchMe, restoreSession }
})
