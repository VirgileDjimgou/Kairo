<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-xl-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2" data-testid="tenant-ops-label">
          Multi-tenant operations
        </div>
        <h1 class="h4 fw-bold mb-1" data-testid="tenant-ops-title">Command center</h1>
        <p class="text-muted mb-0">
          Inspect the organizations available to the current account, switch tenants explicitly, and review the current tenant posture without crossing isolation boundaries.
        </p>
      </div>
      <div class="d-flex flex-wrap align-items-start gap-2">
        <RouterLink to="/admin" class="btn btn-outline-secondary">
          <i class="bi bi-arrow-left me-1"></i>Back to overview
        </RouterLink>
        <RouterLink to="/admin/settings" class="btn btn-outline-secondary">
          <i class="bi bi-gear me-1"></i>Tenant settings
        </RouterLink>
        <button class="btn om-primary-btn" type="button" @click="refreshTenantContext" :disabled="loading || isRecovering">
          {{ loading ? copy.refreshing : copy.refreshContext }}
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-warning border-0 shadow-sm mb-4" role="alert">
      <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
        <div>
          <div class="fw-semibold">
            <i class="bi bi-exclamation-triangle me-2"></i>{{ copy.workspaceErrorTitle }}
          </div>
          <p class="small mb-0 mt-2">{{ error }}</p>
          <p class="mb-0 small text-muted mt-1">{{ localeStore.t('common.recoveryHint') }}</p>
        </div>
        <button class="btn btn-outline-secondary btn-sm align-self-start" type="button" @click="retryRefreshTenantContext" :disabled="isRecovering">
          <span v-if="isRecovering" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
          {{ isRecovering ? localeStore.t('common.loading') : localeStore.t('common.retry') }}
        </button>
      </div>
    </div>

    <div v-if="actionError" class="alert alert-danger border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ actionError }}
    </div>

    <div v-if="successMessage" class="alert alert-success border-0 shadow-sm mb-4" data-testid="tenant-ops-success">
      <i class="bi bi-check-circle me-2"></i>{{ successMessage }}
    </div>

    <div class="row g-4 mb-4">
      <div class="col-md-6 col-xl-3" v-for="card in summaryCards" :key="card.id">
        <div class="summary-card h-100">
          <div class="small text-muted mb-2">{{ card.label }}</div>
          <div class="summary-value">{{ card.value }}</div>
          <div class="small text-muted mt-2">{{ card.hint }}</div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-xl-7">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">Tenant inventory</div>
                <h2 class="h6 fw-bold mb-1">Available memberships</h2>
                <p class="text-muted small mb-0">
                  Every tenant entry comes from the backend membership list. Switching remains explicit and keeps the active tenant visible.
                </p>
              </div>
              <span class="badge bg-light text-dark border align-self-start">
                {{ memberships.length }} tenant(s)
              </span>
            </div>

            <div class="vstack gap-3">
              <article
                v-for="membership in memberships"
                :key="membership.tenant_id"
                class="tenant-card"
                :class="{ 'tenant-card-current': membership.tenant_id === currentTenantId }"
                :data-testid="`tenant-card-${membership.slug}`"
              >
                <div class="d-flex flex-column flex-lg-row justify-content-between gap-3">
                  <div class="d-flex align-items-start gap-3">
                    <div
                      class="tenant-brand"
                      :style="{ backgroundColor: membership.branding.primary_color || '#1f4f8f' }"
                      aria-hidden="true"
                    ></div>
                    <div>
                      <div class="d-flex flex-wrap align-items-center gap-2 mb-2">
                        <h3 class="h6 fw-bold mb-0">{{ membership.name }}</h3>
                        <span v-if="membership.tenant_id === currentTenantId" class="badge bg-success-subtle text-success">
                          Current tenant
                        </span>
                        <span v-else class="badge bg-light text-dark border">Available tenant</span>
                      </div>
                      <div class="small text-muted mb-2">
                        {{ membership.slug }} · profile {{ membership.profile_type }} · {{ membership.roles.join(', ') || 'No roles' }}
                      </div>
                      <div class="d-flex flex-wrap gap-2">
                        <span
                          v-for="role in membership.roles"
                          :key="`${membership.tenant_id}-${role}`"
                          class="badge bg-light text-dark border"
                        >
                          {{ role }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div class="text-lg-end">
                    <div class="small text-muted mb-1">Modules enabled</div>
                    <div class="fw-bold">{{ enabledModuleCount(membership) }} / {{ moduleTotal }}</div>
                    <div class="small text-muted mt-2">
                      {{ membershipHint(membership) }}
                    </div>
                  </div>
                </div>

                <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mt-3">
                  <div class="small text-muted">
                    Tenant context is isolated. Switching keeps the authorization boundary intact and refreshes the signed access token.
                  </div>
                  <button
                    class="btn btn-sm"
                    :class="membership.tenant_id === currentTenantId ? 'btn-outline-secondary' : 'btn-primary'"
                    type="button"
                    :disabled="switchingTenantId === membership.tenant_id || membership.tenant_id === currentTenantId"
                    @click="switchTenant(membership)"
                  >
                    <span
                      v-if="switchingTenantId === membership.tenant_id"
                      class="spinner-border spinner-border-sm me-1"
                      role="status"
                      aria-hidden="true"
                    ></span>
                    {{
                      membership.tenant_id === currentTenantId
                        ? 'Already active'
                        : `Switch to ${membership.slug}`
                    }}
                  </button>
                </div>
              </article>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">Safe preparation notes</div>
            <h2 class="h6 fw-bold mb-3">Multi-tenant demo helper</h2>
            <p class="text-muted small mb-3">
              Use the repo helper when you want a second isolated tenant for demos or screenshots. The command center stays safe because it only reflects memberships the backend already returned to the current user.
            </p>
            <pre class="demo-code mb-0">./seed/seed-multi-tenant.sh
.\seed\seed-multi-tenant.ps1</pre>
          </div>
        </div>
      </div>

      <div class="col-xl-5">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">Current tenant context</div>
            <h2 class="h6 fw-bold mb-3">Active organization</h2>

            <div v-if="currentMembership" class="vstack gap-3 small">
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">Name</span>
                <span class="fw-semibold text-end">{{ currentMembership.name }}</span>
              </div>
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">Slug</span>
                <span class="fw-semibold text-end">{{ currentMembership.slug }}</span>
              </div>
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">Roles</span>
                <span class="fw-semibold text-end">{{ currentMembership.roles.join(', ') || 'No roles' }}</span>
              </div>
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">Profile type</span>
                <span class="fw-semibold text-end text-capitalize">{{ currentMembership.profile_type }}</span>
              </div>
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">Current tenant selected</span>
                <span class="badge bg-success-subtle text-success align-self-start">Yes</span>
              </div>
            </div>

            <div v-else class="alert alert-warning mb-0">
              No active tenant is selected. Restore the session or choose a tenant from the login flow.
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">Recovery posture</div>
            <h2 class="h6 fw-bold mb-3">Current tenant evidence</h2>

            <div v-if="settings" class="vstack gap-2 small">
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">Backup evidence</span>
                <span class="fw-semibold text-end text-capitalize">{{ settings.operations.last_backup_status }}</span>
              </div>
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">Restore drill</span>
                <span class="fw-semibold text-end text-capitalize">{{ settings.operations.last_restore_drill_status }}</span>
              </div>
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">Alert posture</span>
                <span class="fw-semibold text-end text-capitalize">{{ settings.operations.alert_posture }}</span>
              </div>
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">Overall status</span>
                <span class="badge text-capitalize" :class="recoveryBadgeClass(settings.operations.overall_status)">
                  {{ settings.operations.overall_status }}
                </span>
              </div>
              <div class="small text-muted pt-1">
                {{ settings.operations.status_message }}
              </div>
            </div>

            <div v-else class="text-muted small">
              Recovery evidence is loaded from the current tenant settings.
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">Operator actions</div>
            <h2 class="h6 fw-bold mb-3">Fast paths</h2>
            <div class="vstack gap-2">
              <RouterLink to="/admin/settings" class="quick-action">
                <div class="fw-semibold">Review tenant settings</div>
                <div class="small text-muted">Inspect branding, modules, and recovery evidence.</div>
              </RouterLink>
              <RouterLink to="/admin/access" class="quick-action">
                <div class="fw-semibold">Manage access</div>
                <div class="small text-muted">Invite teammates or review lifecycle controls.</div>
              </RouterLink>
              <RouterLink to="/admin/audit" class="quick-action">
                <div class="fw-semibold">Open audit trail</div>
                <div class="small text-muted">Review sensitive tenant actions in one place.</div>
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useRecoveryState } from '@/composables/useRecoveryState'
import { getTenantSettings, type TenantSettingsResponse } from '@/api/settings.api'
import { useAuthStore } from '@/stores/auth.store'
import { useLocaleStore } from '@/stores/locale.store'
import { useTenantStore } from '@/stores/tenant.store'
import type { TenantMembershipResponse } from '@/api/auth.api'

const auth = useAuthStore()
const localeStore = useLocaleStore()
const tenantStore = useTenantStore()
const { loading, error, isRecovering, run, retry } = useRecoveryState()
const successMessage = ref('')
const switchingTenantId = ref('')
const settings = ref<TenantSettingsResponse | null>(null)
const actionError = ref('')

const memberships = computed(() => tenantStore.memberships)
const currentTenantId = computed(() => tenantStore.currentTenant?.tenant_id ?? '')
const currentMembership = computed(
  () => memberships.value.find((item) => item.tenant_id === currentTenantId.value) ?? null,
)
const moduleTotal = computed(() =>
  currentMembership.value ? Object.keys(currentMembership.value.modules).length : 0,
)
const copy = computed(() => {
  if (localeStore.currentLocale === 'de') {
    return {
      refreshing: 'Aktualisierung...',
      refreshContext: 'Kontext aktualisieren',
      workspaceErrorTitle: 'Tenant-Operationen nicht verfügbar',
      switchFailed: 'Tenant-Wechsel fehlgeschlagen.',
      loadFailed: 'Der aktuelle Tenant-Kontext konnte nicht geladen werden.',
      switchedTo: 'Gewechselt zu {name}. Der aktive Tenant-Kontext ist jetzt auf diese Organisation isoliert.',
    }
  }
  if (localeStore.currentLocale === 'en') {
    return {
      refreshing: 'Refreshing...',
      refreshContext: 'Refresh context',
      workspaceErrorTitle: 'Tenant operations unavailable',
      switchFailed: 'Could not switch tenant.',
      loadFailed: 'Could not load the current tenant context.',
      switchedTo: 'Switched to {name}. The active tenant context is now isolated to that organization.',
    }
  }
  return {
    refreshing: 'Actualisation...',
    refreshContext: 'Actualiser le contexte',
    workspaceErrorTitle: 'Les opérations tenant sont indisponibles',
    switchFailed: 'Impossible de changer de tenant.',
    loadFailed: 'Impossible de charger le contexte du tenant courant.',
    switchedTo: 'Basculé sur {name}. Le contexte actif est maintenant isolé à cette organisation.',
  }
})

const summaryCards = computed(() => [
  {
    id: 'active',
    label: 'Active tenant',
    value: currentMembership.value?.name ?? 'None',
    hint: currentMembership.value?.slug ? `Slug: ${currentMembership.value.slug}` : 'No tenant selected',
  },
  {
    id: 'memberships',
    label: 'Memberships',
    value: String(memberships.value.length),
    hint: memberships.value.length > 1 ? 'Multiple tenants available' : 'Single tenant account',
  },
  {
    id: 'roles',
    label: 'Current roles',
    value: currentMembership.value?.roles.join(', ') || 'None',
    hint: currentMembership.value?.profile_type ? `Profile: ${currentMembership.value.profile_type}` : 'No role context',
  },
  {
    id: 'recovery',
    label: 'Recovery evidence',
    value: settings.value?.operations.overall_status ?? 'unloaded',
    hint: settings.value?.operations.status_message ?? 'Loaded from current tenant settings',
  },
])

function enabledModuleCount(membership: TenantMembershipResponse) {
  return Object.values(membership.modules).filter(Boolean).length
}

function membershipHint(membership: TenantMembershipResponse) {
  const moduleCount = enabledModuleCount(membership)
  const roleLabel = membership.roles.length ? membership.roles.join(', ') : 'No assigned roles'
  return `${moduleCount} module(s) enabled · ${roleLabel}`
}

function recoveryBadgeClass(status: string) {
  if (status === 'healthy') return 'bg-success-subtle text-success'
  if (status === 'critical') return 'bg-danger-subtle text-danger'
  return 'bg-warning-subtle text-warning'
}

async function refreshTenantContext() {
  actionError.value = ''
  await run(async () => {
    const tenantId = currentTenantId.value
    if (!tenantId) {
      settings.value = null
      return
    }
    settings.value = await getTenantSettings(tenantId)
  })
  if (error.value == null) {
    return
  }
  error.value = error.value || copy.value.loadFailed
}

async function retryRefreshTenantContext() {
  actionError.value = ''
  await retry(async () => {
    const tenantId = currentTenantId.value
    if (!tenantId) {
      settings.value = null
      return
    }
    settings.value = await getTenantSettings(tenantId)
  })
  if (error.value == null) {
    return
  }
  error.value = error.value || copy.value.loadFailed
}

async function switchTenant(membership: TenantMembershipResponse) {
  if (membership.tenant_id === currentTenantId.value) return

  const confirmed = window.confirm(
    `Switch from ${currentMembership.value?.name ?? 'the current tenant'} to ${membership.name}? The workspace will refresh with the new tenant context.`,
  )
  if (!confirmed) return

  switchingTenantId.value = membership.tenant_id
  actionError.value = ''
  successMessage.value = ''

  try {
    const switched = await tenantStore.selectTenant(membership.tenant_id)
    if (!switched) {
      throw new Error('Switch failed')
    }
    await auth.fetchMe()
    await refreshTenantContext()
    successMessage.value = copy.value.switchedTo.replace('{name}', membership.name)
  } catch (err: unknown) {
    actionError.value = (err as { message?: string })?.message || copy.value.switchFailed
  } finally {
    switchingTenantId.value = ''
  }
}

watch(currentTenantId, () => {
  void refreshTenantContext()
})

onMounted(() => {
  void refreshTenantContext()
})
</script>

<style scoped>
.summary-card {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 1rem;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(247, 250, 252, 1) 100%);
  padding: 1rem;
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1.15;
  color: #0f172a;
  word-break: break-word;
}

.tenant-card {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 1rem;
  background: #fff;
  padding: 1rem;
}

.tenant-card-current {
  border-color: rgba(31, 79, 143, 0.28);
  box-shadow: 0 0 0 1px rgba(31, 79, 143, 0.08);
}

.tenant-brand {
  width: 0.95rem;
  height: 0.95rem;
  border-radius: 999px;
  margin-top: 0.3rem;
  flex-shrink: 0;
}

.quick-action {
  display: block;
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 0.95rem;
  background: #fff;
  padding: 0.9rem;
  text-decoration: none;
  color: inherit;
}

.quick-action:hover {
  border-color: rgba(31, 79, 143, 0.24);
  background: rgba(31, 79, 143, 0.03);
}

.demo-code {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 0.95rem;
  background: #0f172a;
  color: #e2e8f0;
  padding: 1rem;
  white-space: pre-wrap;
}
</style>
