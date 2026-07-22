import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import type { TenantMembershipResponse } from '@/api/auth.api'
import { switchTenant as apiSwitchTenant } from '@/api/auth.api'

const SELECTED_TENANT_KEY = 'selected_tenant_id'

export const useTenantStore = defineStore('tenant', () => {
  const memberships = ref<TenantMembershipResponse[]>([])
  const selectedTenantId = ref<string>(localStorage.getItem(SELECTED_TENANT_KEY) ?? '')

  const currentTenant = computed<TenantMembershipResponse | null>(() => {
    return memberships.value.find((m) => m.tenant_id === selectedTenantId.value) ?? null
  })

  const currentTenantName = computed(() => currentTenant.value?.name ?? 'Organization')
  const hasMultipleTenants = computed(() => memberships.value.length > 1)

  const enabledModules = computed(() => currentTenant.value?.modules ?? null)

  function setMemberships(list: TenantMembershipResponse[], autoSelectTenantId?: string) {
    memberships.value = list
    if (autoSelectTenantId && list.some((m) => m.tenant_id === autoSelectTenantId)) {
      selectedTenantId.value = autoSelectTenantId
      localStorage.setItem(SELECTED_TENANT_KEY, autoSelectTenantId)
    } else if (selectedTenantId.value && list.some((m) => m.tenant_id === selectedTenantId.value)) {
      // persisted selection is still valid
    } else if (list.length > 0) {
      const firstMembership = list.at(0)
      if (firstMembership) {
        selectedTenantId.value = firstMembership.tenant_id
        localStorage.setItem(SELECTED_TENANT_KEY, firstMembership.tenant_id)
      }
    } else {
      selectedTenantId.value = ''
      localStorage.removeItem(SELECTED_TENANT_KEY)
    }
  }

  async function selectTenant(tenantId: string): Promise<boolean> {
    const target = memberships.value.find((m) => m.tenant_id === tenantId)
    if (!target) return false

    try {
      const result = await apiSwitchTenant({ tenant_id: tenantId })
      // Store the new token
      localStorage.setItem('access_token', result.access_token)
      selectedTenantId.value = tenantId
      localStorage.setItem(SELECTED_TENANT_KEY, tenantId)
      setMemberships(result.memberships, tenantId)
      return true
    } catch {
      return false
    }
  }

  function reset() {
    memberships.value = []
    selectedTenantId.value = ''
    localStorage.removeItem(SELECTED_TENANT_KEY)
  }

  function isModuleEnabled(moduleName: string): boolean {
    const mods = enabledModules.value
    if (!mods) return true
    const key = moduleName as keyof typeof mods
    return mods[key] ?? true
  }

  return {
    memberships,
    selectedTenantId,
    currentTenant,
    currentTenantName,
    hasMultipleTenants,
    enabledModules,
    setMemberships,
    selectTenant,
    reset,
    isModuleEnabled,
  }
})
