import { computed, type ComputedRef } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import {
  CAP_BACKUP_CREATE,
  CAP_BACKUP_RESTORE_REQUEST,
  CAP_DISCIPLINARY_WRITE,
  CAP_DOCUMENTS_WRITE,
  CAP_EVENTS_SPORTS_WRITE,
  CAP_FINANCE_AUDIT,
  CAP_FINANCE_EXPENSES_WRITE,
  CAP_IDENTITY_ACCESS_RECOVERY,
  CAP_MEMBERSHIP_TENANT_READ,
  CAP_TENANT_ADMINISTRATION,
} from '@/config/capabilities'

export interface DashboardRoleFlags {
  userRoles: ComputedRef<string[]>
  isAdmin: ComputedRef<boolean>
  isPrincipalAdmin: ComputedRef<boolean>
  isTreasurer: ComputedRef<boolean>
  isMemberOnly: ComputedRef<boolean>
  isSecretaryGeneral: ComputedRef<boolean>
  isCensor: ComputedRef<boolean>
  isSportsManager: ComputedRef<boolean>
  isPresidentRole: ComputedRef<boolean>
  isVicePresidentRole: ComputedRef<boolean>
  isAuditor: ComputedRef<boolean>
  isPresident: ComputedRef<boolean>
  canOpenHealthCenter: ComputedRef<boolean>
}

/**
 * Role projections used by the dashboard surfaces.
 *
 * Flags are derived from the authoritative effective capabilities returned by
 * the API; only the principal-admin/admin label distinction still reads the
 * canonical role bundle. Presentation only: backend permissions remain
 * authoritative.
 */
export function useDashboardRoles(): DashboardRoleFlags {
  const authStore = useAuthStore()
  const userRoles = computed(() => authStore.user?.roles ?? [])
  const capabilities = computed(() => authStore.capabilities)
  const can = (capability: string) => capabilities.value.includes(capability)

  const isAdmin = computed(() => userRoles.value.includes('admin'))
  const isPrincipalAdmin = computed(() => userRoles.value.includes('principal_admin'))
  const isTreasurer = computed(() => can(CAP_FINANCE_EXPENSES_WRITE))
  const isMemberOnly = computed(() => !can(CAP_MEMBERSHIP_TENANT_READ))
  const isSecretaryGeneral = computed(() => can(CAP_DOCUMENTS_WRITE))
  const isCensor = computed(() => can(CAP_DISCIPLINARY_WRITE) && !can(CAP_TENANT_ADMINISTRATION))
  const isSportsManager = computed(() => can(CAP_EVENTS_SPORTS_WRITE) && !can(CAP_TENANT_ADMINISTRATION))
  const isPresidentRole = computed(() => can(CAP_BACKUP_RESTORE_REQUEST) && !can(CAP_DOCUMENTS_WRITE))
  const isVicePresidentRole = computed(() => can(CAP_IDENTITY_ACCESS_RECOVERY) && !can(CAP_BACKUP_RESTORE_REQUEST))
  const isAuditor = computed(() => can(CAP_FINANCE_AUDIT) && !can(CAP_BACKUP_CREATE))
  const isPresident = computed(() => isPresidentRole.value)
  const canOpenHealthCenter = computed(() => can(CAP_MEMBERSHIP_TENANT_READ))

  return {
    userRoles,
    isAdmin,
    isPrincipalAdmin,
    isTreasurer,
    isMemberOnly,
    isSecretaryGeneral,
    isCensor,
    isSportsManager,
    isPresidentRole,
    isVicePresidentRole,
    isAuditor,
    isPresident,
    canOpenHealthCenter,
  }
}
