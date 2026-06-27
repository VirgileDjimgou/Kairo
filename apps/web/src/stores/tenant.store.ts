import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export interface TenantOption {
  id: string
  slug: string
  name: string
}

const defaultTenants: TenantOption[] = [
  { id: 'demo', slug: 'demo', name: 'Demo Organization' },
  { id: 'community', slug: 'community', name: 'Community Collective' },
]

export const useTenantStore = defineStore('tenant', () => {
  const tenants = ref<TenantOption[]>(defaultTenants)
  const selectedTenantId = ref<string>(defaultTenants[0]?.id ?? '')

  const currentTenant = computed(
    () => tenants.value.find((tenant) => tenant.id === selectedTenantId.value) ?? tenants.value[0],
  )

  const currentTenantName = computed(() => currentTenant.value?.name ?? 'Organization')

  function selectTenant(tenantId: string) {
    selectedTenantId.value = tenantId
  }

  return { tenants, selectedTenantId, currentTenant, currentTenantName, selectTenant }
})