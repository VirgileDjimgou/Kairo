<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row align-items-lg-end justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          Tenant overview
        </div>
        <h1 class="h4 fw-bold mb-1">Welcome back, {{ authStore.user?.display_name }}</h1>
        <p class="text-muted mb-0">
          Your current tenant is <strong>{{ tenantStore.currentTenantName }}</strong>.
          The dashboard now highlights the next steps that matter most for a first-run setup.
        </p>
      </div>
      <span
        class="badge px-3 py-2"
        :class="isSetupMode ? 'bg-warning-subtle text-warning border border-warning-subtle' : 'bg-success-subtle text-success border border-success-subtle'"
      >
        <i class="bi bi-circle-fill me-1" style="font-size: 0.5rem"></i>
        {{ isSetupMode ? 'Setup mode' : 'Operational' }}
      </span>
    </div>

    <div v-if="loading" class="alert alert-info border-0 shadow-sm mb-4" role="alert">
      <div class="d-flex gap-3">
        <div class="spinner-border spinner-border-sm mt-1" role="status" aria-hidden="true"></div>
        <div>
          <h6 class="alert-heading mb-1">Loading tenant onboarding guidance</h6>
          <p class="mb-0 small">
            We are checking documents, members, announcements, and events so the checklist reflects the live tenant state.
          </p>
        </div>
      </div>
    </div>

    <div v-else-if="error" class="alert alert-warning border-0 shadow-sm mb-4" role="alert">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
    </div>

    <div v-else class="row g-4">
      <div class="col-xl-8">
        <div class="card shadow-sm border-0 onboarding-card h-100" data-testid="tenant-onboarding">
          <div class="card-body p-4 p-xl-5">
            <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-4">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  First-run checklist
                </div>
                <h2 class="h5 fw-bold mb-2">{{ statusTitle }}</h2>
                <p class="text-muted mb-0">
                  {{ statusMessage }}
                </p>
              </div>
              <div class="text-md-end">
                <div
                  class="display-6 fw-bold lh-1"
                  data-testid="tenant-onboarding-progress"
                >
                  {{ progressPercent }}%
                </div>
                <div class="small text-muted">complete</div>
              </div>
            </div>

            <div class="progress mb-4" style="height: 0.75rem">
              <div
                class="progress-bar"
                role="progressbar"
                :aria-valuenow="progressPercent"
                aria-valuemin="0"
                aria-valuemax="100"
                :style="{ width: `${progressPercent}%` }"
              ></div>
            </div>

            <div v-if="nextStep" class="alert alert-primary border-0 mb-4">
              <div class="d-flex align-items-start gap-3">
                <i class="bi bi-arrow-right-circle fs-4 flex-shrink-0"></i>
                <div>
                  <div class="fw-semibold mb-1">Next best action</div>
                  <p class="mb-2 small">
                    {{ nextStep.title }}: {{ nextStep.description }}
                  </p>
                  <RouterLink :to="nextStep.to" class="btn btn-sm btn-primary">
                    {{ nextStep.actionLabel }}
                  </RouterLink>
                </div>
              </div>
            </div>

            <div class="vstack gap-3">
              <article
                v-for="step in checklist"
                :key="step.id"
                class="checklist-item"
                :class="{ completed: step.completed }"
              >
                <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
                  <div class="d-flex gap-3">
                    <div class="step-icon" :class="{ completed: step.completed }">
                      <i :class="step.completed ? 'bi bi-check2' : stepIcon(step.id)"></i>
                    </div>
                    <div>
                      <div class="fw-semibold mb-1">{{ step.title }}</div>
                      <p class="small text-muted mb-0">{{ step.description }}</p>
                    </div>
                  </div>

                  <div class="text-md-end">
                    <span
                      class="badge mb-2"
                      :class="step.completed ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-secondary-subtle text-secondary border border-secondary-subtle'"
                    >
                      {{ step.completed ? 'Completed' : 'Pending' }}
                    </span>
                    <div>
                      <RouterLink :to="step.to" class="btn btn-sm btn-outline-primary">
                        {{ step.actionLabel }}
                      </RouterLink>
                    </div>
                  </div>
                </div>
              </article>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-4">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-1">
                  Tenant snapshot
                </div>
                <h2 class="h6 fw-bold mb-0">Live usage signals</h2>
              </div>
              <button class="btn btn-outline-secondary btn-sm" type="button" @click="refresh" :disabled="loading">
                Refresh
              </button>
            </div>

            <div class="row g-3">
              <div v-for="metric in summaryMetrics" :key="metric.label" class="col-6">
                <div class="metric-card h-100">
                  <div class="small text-muted">{{ metric.label }}</div>
                  <div class="fs-4 fw-bold lh-1 mb-1">{{ metric.value }}</div>
                  <div class="small text-secondary">{{ metric.hint }}</div>
                </div>
              </div>
            </div>

            <hr class="my-4" />

            <div class="small text-uppercase fw-semibold text-secondary mb-2">
              Current tenant
            </div>
            <div class="vstack gap-2 small">
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Tenant</span>
                <span class="fw-semibold text-end">{{ tenantStore.currentTenantName }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Role</span>
                <span class="fw-semibold text-end">
                  {{ authStore.user?.roles.join(', ') || '—' }}
                </span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Checklist complete</span>
                <span class="fw-semibold text-end">
                  {{ completedCount }} / {{ checklist.length }}
                </span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Last refresh</span>
                <span class="fw-semibold text-end">
                  {{ lastRefreshedAt ? formatDateTime(lastRefreshedAt) : 'Just loaded' }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Quick actions
            </div>
            <div class="vstack gap-2">
              <RouterLink
                v-for="action in quickActions"
                :key="action.to + action.label"
                :to="action.to"
                class="btn btn-outline-secondary text-start"
              >
                <i :class="action.icon" class="me-2"></i>{{ action.label }}
              </RouterLink>
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
import { useTenantOnboarding } from '@/composables/useTenantOnboarding'

const authStore = useAuthStore()
const tenantStore = useTenantStore()
const isAdmin = computed(() => authStore.user?.roles.includes('admin') ?? false)
const isTreasurer = computed(() => authStore.user?.roles.includes('treasurer') ?? false)
const isSecretaryGeneral = computed(() => authStore.user?.roles.includes('secretary_general') ?? false)
const isAuditor = computed(() => authStore.user?.roles.includes('auditor') ?? false)
const isPresident = computed(() => authStore.user?.roles.includes('president') ?? false)
const isPrincipalAdmin = computed(() => authStore.user?.roles.includes('principal_admin') ?? false)
const {
  loading,
  error,
  checklist,
  completedCount,
  progressPercent,
  statusTitle,
  statusMessage,
  summaryMetrics,
  nextStep,
  lastRefreshedAt,
  refresh,
} = useTenantOnboarding()

const quickActions = computed(() => {
  const actions: Array<{ label: string; to: string; icon: string }> = []

  if (isAdmin.value) {
    actions.push({ label: 'Review tenant settings', to: '/admin/settings', icon: 'bi bi-sliders' })
    actions.push({ label: 'Upload documents', to: '/admin/documents', icon: 'bi bi-file-earmark-text' })
    if (tenantStore.isModuleEnabled('membership')) {
      actions.push({ label: 'Import members', to: '/admin/members', icon: 'bi bi-people' })
    }
  } else if (isTreasurer.value) {
    actions.push({ label: 'Go to finance workspace', to: '/finance', icon: 'bi bi-cash-coin' })
    if (tenantStore.isModuleEnabled('membership')) {
      actions.push({ label: 'Review member profile', to: '/members/profile', icon: 'bi bi-person-badge' })
    }
  } else if (isSecretaryGeneral.value) {
    actions.push({ label: 'Open secretary workspace', to: '/secretary', icon: 'bi bi-journal-richtext' })
    actions.push({ label: 'Review documents', to: '/secretary/documents', icon: 'bi bi-file-earmark-text' })
    if (tenantStore.isModuleEnabled('policies')) {
      actions.push({ label: 'Review policies', to: '/secretary/policies', icon: 'bi bi-journal-text' })
    }
  } else if (isAuditor.value || isPresident.value || isPrincipalAdmin.value) {
    actions.push({ label: 'Open finance audit', to: '/finance-audit', icon: 'bi bi-clipboard-data' })
    if (tenantStore.isModuleEnabled('membership')) {
      actions.push({ label: 'Review member directory', to: '/members/profile', icon: 'bi bi-person-badge' })
    }
  }

  if (tenantStore.isModuleEnabled('announcements')) {
    actions.push({
      label: isAdmin.value || isSecretaryGeneral.value ? 'Publish announcement' : 'Review announcements',
      to: isAdmin.value ? '/admin/announcements' : isSecretaryGeneral.value ? '/secretary/announcements' : '/announcements',
      icon: 'bi bi-megaphone',
    })
  }

  if (tenantStore.isModuleEnabled('events')) {
    actions.push({
      label: isAdmin.value ? 'Schedule event' : 'Review events',
      to: isAdmin.value ? '/admin/events' : '/events',
      icon: 'bi bi-calendar-event',
    })
  }

  return actions
})

const isSetupMode = computed(() => {
  return progressPercent.value < 100 && completedCount.value === 0
})

function stepIcon(stepId: string): string {
  const map: Record<string, string> = {
    branding: 'bi bi-palette',
    documents: 'bi bi-file-earmark-text',
    members: 'bi bi-people',
    announcements: 'bi bi-megaphone',
    events: 'bi bi-calendar-event',
  }

  return map[stepId] || 'bi bi-arrow-right'
}

function formatDateTime(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

onMounted(refresh)
</script>

<style scoped>
.onboarding-card {
  border-radius: 1.25rem;
}

.checklist-item {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 1rem;
  background: #fff;
  padding: 1rem;
}

.checklist-item.completed {
  background: linear-gradient(180deg, rgba(25, 135, 84, 0.03), rgba(25, 135, 84, 0.01));
}

.step-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.85rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(31, 79, 143, 0.08);
  color: var(--om-primary, #1f4f8f);
  flex-shrink: 0;
}

.step-icon.completed {
  background: rgba(25, 135, 84, 0.12);
  color: #198754;
}

.metric-card {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 0.95rem;
  padding: 0.9rem;
  background: #fff;
}
</style>
