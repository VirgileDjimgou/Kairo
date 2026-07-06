<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-xl-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          Operator health center
        </div>
        <h1 class="h4 fw-bold mb-1">Recovery evidence and dependency health</h1>
        <p class="text-muted mb-0">
          Review the current recovery posture, dependency status, and incident annotations without leaving the tenant.
        </p>
      </div>
      <div class="d-flex flex-wrap align-items-start gap-2">
        <RouterLink to="/admin" class="btn btn-outline-secondary">
          <i class="bi bi-arrow-left me-1"></i>Back to overview
        </RouterLink>
        <RouterLink to="/admin/settings" class="btn btn-outline-secondary">
          <i class="bi bi-gear me-1"></i>Tenant settings
        </RouterLink>
        <button class="btn om-primary-btn" type="button" @click="refresh" :disabled="loading">
          {{ loading ? 'Refreshing...' : 'Refresh health' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-warning border-0 shadow-sm mb-4">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
    </div>

    <div class="row g-4">
      <div class="col-xl-8">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  Live dependency health
                </div>
                <h2 class="h6 fw-bold mb-1">System status</h2>
                <p class="text-muted small mb-0">
                  The backend health probe is read-only and shows the current service posture for the active tenant.
                </p>
              </div>
              <span class="badge text-capitalize align-self-start" :class="statusBadgeClass(systemHealth?.status)">
                {{ systemHealth?.status || 'unknown' }}
              </span>
            </div>

            <div class="row g-3 mb-4" data-testid="health-center-summary">
              <div class="col-md-4" v-for="card in summaryCards" :key="card.label">
                <div class="metric-card h-100">
                  <div class="small text-muted">{{ card.label }}</div>
                  <div class="metric-value mb-1">{{ card.value }}</div>
                  <div class="small text-secondary">{{ card.hint }}</div>
                </div>
              </div>
            </div>

            <div class="table-responsive">
              <table class="table align-middle">
                <thead>
                  <tr>
                    <th scope="col">Service</th>
                    <th scope="col">Status</th>
                    <th scope="col">Latency</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="service in serviceRows" :key="service.name">
                    <td>
                      <div class="fw-semibold">{{ service.label }}</div>
                      <div class="small text-muted">{{ service.name }}</div>
                    </td>
                    <td>
                      <span class="badge text-capitalize" :class="service.badgeClass">{{ service.status }}</span>
                    </td>
                    <td class="text-nowrap">{{ service.latency }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  Recovery evidence
                </div>
                <h2 class="h6 fw-bold mb-1">Backup, restore, and alert posture</h2>
                <p class="text-muted small mb-0">
                  Freshness warnings stay visible so operators can see at a glance when evidence needs a refresh.
                </p>
              </div>
              <span class="badge text-capitalize align-self-start" :class="recoveryBadgeClass(recoveryStatus)">
                {{ recoveryStatus }}
              </span>
            </div>

            <div class="row g-3">
              <div class="col-md-6">
                <div class="mini-stat h-100">
                  <div class="small text-muted">Last backup</div>
                  <div class="fw-semibold">{{ formatDate(recovery?.last_backup_at) }}</div>
                  <div class="small text-muted">{{ recovery?.last_backup_reference || 'No backup reference recorded' }}</div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="mini-stat h-100">
                  <div class="small text-muted">Restore drill</div>
                  <div class="fw-semibold">{{ formatDate(recovery?.last_restore_drill_at) }}</div>
                  <div class="small text-muted text-capitalize">
                    {{ recovery?.last_restore_drill_status || 'unknown' }}
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="mini-stat h-100">
                  <div class="small text-muted">Alert posture</div>
                  <div class="fw-semibold text-capitalize">{{ recovery?.alert_posture || 'unknown' }}</div>
                  <div class="small text-muted">
                    {{ recovery?.alert_contacts_configured ? 'Alert contacts configured' : 'Alert contacts missing' }}
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="mini-stat h-100">
                  <div class="small text-muted">Freshness warnings</div>
                  <div class="fw-semibold" data-testid="health-center-warning-count">{{ freshnessWarnings.length }}</div>
                  <div class="small text-muted">Stale or missing signals that deserve attention</div>
                </div>
              </div>
            </div>

            <div v-if="freshnessWarnings.length" class="vstack gap-2 mt-4">
              <div v-for="warning in freshnessWarnings" :key="warning" class="alert alert-warning mb-0 border-0">
                {{ warning }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-4">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Incident annotations
            </div>
            <h2 class="h6 fw-bold mb-3">Current note</h2>
            <p class="text-muted small mb-3">
              {{ recovery?.notes || 'No incident annotation recorded yet.' }}
            </p>
            <RouterLink to="/admin/settings" class="btn btn-outline-secondary btn-sm w-100">
              Update recovery note
            </RouterLink>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Operational snapshot
            </div>
            <div class="vstack gap-2 small">
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">Tenant</span>
                <span class="fw-semibold text-end">{{ tenantStore.currentTenantName }}</span>
              </div>
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">Environment</span>
                <span class="fw-semibold text-end text-capitalize">{{ systemHealth?.env || 'unknown' }}</span>
              </div>
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">Version</span>
                <span class="fw-semibold text-end">{{ systemHealth?.version || 'unknown' }}</span>
              </div>
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">Modules reported</span>
                <span class="fw-semibold text-end">{{ systemHealth?.modules.length || 0 }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Fast paths
            </div>
            <div class="vstack gap-2">
              <RouterLink to="/admin/settings" class="quick-action">
                <div class="fw-semibold">Review tenant settings</div>
                <div class="small text-muted">Inspect recovery evidence and notes.</div>
              </RouterLink>
              <RouterLink to="/admin/tenants" class="quick-action">
                <div class="fw-semibold">Tenant operations</div>
                <div class="small text-muted">Switch tenant context explicitly.</div>
              </RouterLink>
              <RouterLink to="/admin/audit" class="quick-action">
                <div class="fw-semibold">Audit trail</div>
                <div class="small text-muted">Review sensitive operational actions.</div>
              </RouterLink>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { getTenantSettings, type RecoveryEvidenceResponse } from '@/api/settings.api'
import { getSystemHealth, type SystemHealthResponse } from '@/api/system.api'
import { useTenantStore } from '@/stores/tenant.store'

type ServiceRow = {
  name: string
  label: string
  status: string
  latency: string
  badgeClass: string
}

const tenantStore = useTenantStore()
const loading = ref(false)
const error = ref('')
const systemHealth = ref<SystemHealthResponse | null>(null)
const recovery = ref<RecoveryEvidenceResponse | null>(null)

const recoveryStatus = computed(() => recovery.value?.overall_status || 'unknown')

const freshnessWarnings = computed(() => {
  const warnings: string[] = []
  if (!recovery.value) {
    warnings.push('Recovery evidence has not been loaded yet.')
    return warnings
  }

  if (recovery.value.backup_is_stale) {
    warnings.push('Backup evidence is stale and should be refreshed.')
  }
  if (recovery.value.restore_drill_is_stale) {
    warnings.push('Restore drill evidence is stale and should be refreshed.')
  }
  if (!recovery.value.alert_is_healthy) {
    warnings.push('Alert contacts or alert posture need attention.')
  }
  return warnings
})

const summaryCards = computed(() => [
  {
    label: 'Overall status',
    value: systemHealth.value?.status || 'unknown',
    hint: recovery.value?.status_message || 'Waiting for the latest recovery evidence',
  },
  {
    label: 'Freshness warnings',
    value: String(freshnessWarnings.value.length),
    hint: 'Stale signals stay visible in this panel',
  },
  {
    label: 'Reported modules',
    value: String(systemHealth.value?.modules.length || 0),
    hint: 'Backend modules exposed by the health probe',
  },
])

const serviceRows = computed<ServiceRow[]>(() => {
  const checks = systemHealth.value?.checks || {}
  const labels: Record<string, string> = {
    database: 'Database',
    redis: 'Redis cache',
    minio: 'Object storage',
    qdrant: 'Vector store',
    ollama: 'LLM provider',
  }

  return Object.entries(checks).map(([name, check]) => ({
    name,
    label: labels[name] || name,
    status: check.status,
    latency: `${check.latency_ms} ms`,
    badgeClass: statusBadgeClass(check.status),
  }))
})

function statusBadgeClass(status?: string) {
  return {
    ok: 'bg-success-subtle text-success border border-success-subtle',
    healthy: 'bg-success-subtle text-success border border-success-subtle',
    degraded: 'bg-warning-subtle text-warning border border-warning-subtle',
    unavailable: 'bg-danger-subtle text-danger border border-danger-subtle',
    error: 'bg-danger-subtle text-danger border border-danger-subtle',
    critical: 'bg-danger-subtle text-danger border border-danger-subtle',
  }[status || 'unknown'] || 'bg-light text-dark border'
}

function recoveryBadgeClass(status?: string) {
  return {
    healthy: 'bg-success-subtle text-success border border-success-subtle',
    warning: 'bg-warning-subtle text-warning border border-warning-subtle',
    critical: 'bg-danger-subtle text-danger border border-danger-subtle',
  }[status || 'unknown'] || 'bg-light text-dark border'
}

function formatDate(value?: string | null) {
  if (!value) return 'Not recorded'
  return new Date(value).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

async function refresh() {
  loading.value = true
  error.value = ''
  try {
    const tenantId = tenantStore.currentTenant?.tenant_id
    if (!tenantId) {
      throw new Error('No active tenant selected')
    }

    const [health, settings] = await Promise.all([
      getSystemHealth(),
      getTenantSettings(tenantId),
    ])
    systemHealth.value = health
    recovery.value = settings.operations
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load health center'
  } finally {
    loading.value = false
  }
}

onMounted(refresh)
</script>

<style scoped>
.metric-card {
  display: block;
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 1rem;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(247, 250, 252, 1) 100%);
  padding: 1rem;
  color: inherit;
}

.metric-value {
  font-size: 1.8rem;
  font-weight: 700;
  line-height: 1;
  color: #0f172a;
}

.mini-stat {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 0.85rem;
  padding: 0.875rem;
  background: #fff;
}

.quick-action {
  display: block;
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 0.85rem;
  padding: 0.875rem;
  text-decoration: none;
  color: inherit;
  background: #fff;
}

.quick-action:hover {
  border-color: rgba(31, 79, 143, 0.24);
  box-shadow: 0 0.75rem 1.5rem rgba(15, 23, 42, 0.06);
}
</style>
