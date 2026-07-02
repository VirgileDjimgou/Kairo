<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-xl-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2" data-testid="admin-overview-hub-label">
          {{ hubLabel }}
        </div>
        <h1 class="h4 fw-bold mb-1" data-testid="admin-overview-title">{{ overviewTitle }}</h1>
        <p class="text-muted mb-0">
          {{ overviewSubtitle }}
        </p>
      </div>
      <div class="d-flex align-items-start gap-2">
        <RouterLink to="/admin/settings" class="btn btn-outline-secondary">
          <i class="bi bi-gear me-1"></i>Settings
        </RouterLink>
        <button class="btn om-primary-btn" type="button" @click="refresh" :disabled="loading">
          {{ loading ? 'Refreshing...' : 'Refresh overview' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-warning border-0 shadow-sm mb-4">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
    </div>

    <div class="row g-4">
      <div class="col-xl-8">
        <div class="row g-3 mb-4" data-testid="admin-overview-metrics">
          <div v-for="metric in summaryMetrics" :key="metric.id" class="col-md-6 col-xxl-4">
            <RouterLink :to="metric.to" class="metric-card h-100 text-decoration-none">
              <div class="small text-muted mb-2">{{ metric.label }}</div>
              <div class="metric-value mb-2">{{ metric.value }}</div>
              <div class="small" :class="toneTextClass(metric.tone)">{{ metric.hint }}</div>
            </RouterLink>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  Operational watchlist
                </div>
                <h2 class="h6 fw-bold mb-1">Warnings and readiness gaps</h2>
                <p class="text-muted small mb-0">
                  This panel surfaces the setup or operational issues most likely to slow down a tenant admin.
                </p>
              </div>
              <span class="badge bg-light text-dark border align-self-start">
                {{ riskItems.length }} item(s)
              </span>
            </div>

            <div class="vstack gap-3">
              <article
                v-for="risk in riskItems"
                :key="risk.id"
                class="risk-card"
                :class="toneBorderClass(risk.tone)"
              >
                <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
                  <div>
                    <div class="fw-semibold mb-1">{{ risk.title }}</div>
                    <p class="small text-muted mb-0">{{ risk.description }}</p>
                  </div>
                  <RouterLink :to="risk.to" class="btn btn-sm btn-outline-primary align-self-start">
                    {{ risk.actionLabel }}
                  </RouterLink>
                </div>
              </article>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  Onboarding continuity
                </div>
                <h2 class="h6 fw-bold mb-1">Launch readiness</h2>
                <p class="text-muted small mb-0">
                  Reuses the tenant setup logic from the member-facing dashboard so admins see the same launch picture.
                </p>
              </div>
              <div class="text-lg-end">
                <div class="fw-bold fs-4" data-testid="admin-overview-onboarding-progress">
                  {{ onboardingProgress }}%
                </div>
                <div class="small text-muted">checklist complete</div>
              </div>
            </div>

            <div class="progress mb-3" style="height: 0.75rem">
              <div
                class="progress-bar"
                role="progressbar"
                :aria-valuenow="onboardingProgress"
                aria-valuemin="0"
                aria-valuemax="100"
                :style="{ width: `${onboardingProgress}%` }"
              ></div>
            </div>

            <div v-if="onboardingNextStep" class="alert alert-primary border-0 mb-0">
              <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
                <div>
                  <div class="fw-semibold mb-1">Next recommended admin action</div>
                  <p class="small mb-0">
                    {{ onboardingNextStep.title }}: {{ onboardingNextStep.description }}
                  </p>
                </div>
                <RouterLink :to="onboardingNextStep.to" class="btn btn-sm btn-primary align-self-start">
                  {{ onboardingNextStep.actionLabel }}
                </RouterLink>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-4">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Document operations
            </div>
            <h2 class="h6 fw-bold mb-3">Ingestion health</h2>

            <div v-if="ingestionHealth" class="row g-2 mb-3">
              <div class="col-6">
                <div class="mini-stat">
                  <div class="small text-muted">Queued</div>
                  <div class="fw-bold">{{ ingestionHealth.queued_count }}</div>
                </div>
              </div>
              <div class="col-6">
                <div class="mini-stat">
                  <div class="small text-muted">Processing</div>
                  <div class="fw-bold">{{ ingestionHealth.processing_count }}</div>
                </div>
              </div>
              <div class="col-6">
                <div class="mini-stat">
                  <div class="small text-muted">Failed</div>
                  <div class="fw-bold" :class="toneTextClass(ingestionHealth.failed_count > 0 ? 'danger' : 'success')">
                    {{ ingestionHealth.failed_count }}
                  </div>
                </div>
              </div>
              <div class="col-6">
                <div class="mini-stat">
                  <div class="small text-muted">Retried</div>
                  <div class="fw-bold">{{ ingestionHealth.retried_count }}</div>
                </div>
              </div>
            </div>

            <div v-if="ingestionHealth?.recent_failures.length" class="small text-muted mb-3">
              Latest failure: {{ shortId(ingestionHealth.recent_failures[0].job_id) }}
            </div>

            <RouterLink to="/admin/documents" class="btn btn-outline-secondary btn-sm w-100">
              Open document operations
            </RouterLink>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Quick actions
            </div>
            <div class="vstack gap-2" data-testid="admin-overview-quick-actions">
              <RouterLink
                v-for="action in quickActions"
                :key="action.id"
                :to="action.to"
                class="quick-action"
              >
                <div class="fw-semibold">{{ action.label }}</div>
                <div class="small text-muted">{{ action.description }}</div>
              </RouterLink>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Tenant scope
            </div>
            <div class="vstack gap-2 small">
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Tenant</span>
                <span class="fw-semibold text-end">{{ tenantStore.currentTenantName }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Enabled modules</span>
                <span class="fw-semibold text-end">{{ enabledModuleCount }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Open contribution balance</span>
                <span class="fw-semibold text-end">
                  {{ contributionSummary?.total_balance ?? 'n/a' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useTenantStore } from '@/stores/tenant.store'
import { useAdminOverview } from '@/composables/useAdminOverview'

const authStore = useAuthStore()
const tenantStore = useTenantStore()
const userRoles = computed(() => authStore.user?.roles ?? [])
const isPrincipalAdmin = computed(() => userRoles.value.includes('principal_admin'))
const hubLabel = computed(() => (isPrincipalAdmin.value ? 'Principal administration' : 'Administration'))
const overviewTitle = computed(() => (isPrincipalAdmin.value ? 'Principal admin overview' : 'Admin overview'))
const overviewSubtitle = computed(() =>
  isPrincipalAdmin.value
    ? 'A tenant-wide control plane for role assignments, settings, module toggles, and sensitive review.'
    : 'A single screen for tenant readiness, operational signals, and the next action that deserves attention.',
)
const {
  loading,
  error,
  modules,
  summaryMetrics,
  riskItems,
  quickActions,
  onboarding,
  ingestionHealth,
  contributionSummary,
  refresh,
} = useAdminOverview()

const enabledModuleCount = computed(() => {
  return Object.values(modules.value).filter(Boolean).length
})

const onboardingProgress = computed(() => onboarding.progressPercent.value)
const onboardingNextStep = computed(() => onboarding.nextStep.value)

function toneTextClass(tone: 'neutral' | 'success' | 'warning' | 'danger') {
  return {
    neutral: 'text-secondary',
    success: 'text-success',
    warning: 'text-warning',
    danger: 'text-danger',
  }[tone]
}

function toneBorderClass(tone: 'warning' | 'danger' | 'success') {
  return {
    warning: 'border-warning-subtle',
    danger: 'border-danger-subtle',
    success: 'border-success-subtle',
  }[tone]
}

function shortId(value: string) {
  return value.slice(0, 8)
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
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}

.metric-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 1rem 2rem rgba(15, 23, 42, 0.06);
  border-color: rgba(31, 79, 143, 0.24);
}

.metric-value {
  font-size: 1.8rem;
  font-weight: 700;
  line-height: 1;
  color: #0f172a;
}

.risk-card {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 1rem;
  background: #fff;
  padding: 1rem;
}

.mini-stat {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 0.85rem;
  padding: 0.75rem;
  background: #fff;
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
</style>
