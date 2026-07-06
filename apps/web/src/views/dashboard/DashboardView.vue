<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-lg-row align-items-lg-end justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          {{ dashboardKicker }}
        </div>
        <h1 class="h4 fw-bold mb-1">Welcome back, {{ authStore.user?.display_name }}</h1>
        <p class="text-muted mb-0">
          {{ dashboardLead }}
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

    <div v-else class="card shadow-sm border-0 mb-4" data-testid="dashboard-workspace-focus">
      <div class="card-body p-4">
        <div class="d-flex flex-column flex-lg-row justify-content-between gap-3">
          <div>
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              {{ workspaceFocus.kicker }}
            </div>
            <h2 class="h5 fw-bold mb-1">{{ workspaceFocus.title }}</h2>
            <p class="text-muted mb-0">
              {{ workspaceFocus.description }}
            </p>
          </div>
          <RouterLink :to="workspaceFocus.primary.to" class="btn btn-primary align-self-start">
            {{ workspaceFocus.primary.label }}
          </RouterLink>
        </div>

        <div class="d-flex flex-wrap gap-2 mt-3">
          <RouterLink
            v-for="action in workspaceFocus.links"
            :key="action.to + action.label"
            :to="action.to"
            class="btn btn-outline-secondary btn-sm"
          >
            {{ action.label }}
          </RouterLink>
        </div>
      </div>
    </div>

    <div class="row g-4">
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

type WorkspaceFocusLink = {
  label: string
  to: string
}

type WorkspaceFocus = {
  kicker: string
  title: string
  description: string
  primary: WorkspaceFocusLink
  links: WorkspaceFocusLink[]
}

const authStore = useAuthStore()
const tenantStore = useTenantStore()
const userRoles = computed(() => authStore.user?.roles ?? [])
const isAdmin = computed(() => userRoles.value.includes('admin'))
const isPrincipalAdmin = computed(() => userRoles.value.includes('principal_admin'))
const isTreasurer = computed(() => userRoles.value.includes('treasurer'))
const isMemberOnly = computed(() => userRoles.value.includes('member') && userRoles.value.length === 1)
const isSecretaryGeneral = computed(() => userRoles.value.includes('secretary_general'))
const isCensor = computed(() => userRoles.value.includes('censor'))
const isSportsManager = computed(() => userRoles.value.includes('sports_manager'))
const isPresidentRole = computed(() => userRoles.value.includes('president'))
const isVicePresidentRole = computed(() => userRoles.value.includes('vice_president'))
const isAuditor = computed(() => userRoles.value.includes('auditor'))
const isPresident = computed(() => userRoles.value.includes('president'))
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

const workspaceFocus = computed<WorkspaceFocus>(() => {
  if (isPrincipalAdmin.value) {
    return {
      kicker: 'Principal admin control plane',
      title: 'Tenant operations, settings, and sensitive review',
      description:
        'Use the control plane for tenant-wide administration while keeping isolation, review paths, and settings in one place.',
      primary: { label: 'Open principal admin control plane', to: '/admin/settings' },
      links: [
        { label: 'Tenant operations', to: '/admin/tenants' },
        { label: 'Manage access', to: '/admin/access' },
      ],
    }
  }

  if (isMemberOnly.value) {
    return {
      kicker: 'Read-only member portal',
      title: 'My profile, balance, and member updates',
      description:
        'Open the member portal for your own profile, contribution summary, and the latest association updates you are allowed to read.',
      primary: { label: 'Open my profile', to: '/members/profile' },
      links: [
        { label: 'Ask the assistant', to: '/chat' },
        { label: 'Review events', to: '/events' },
      ],
    }
  }

  if (isTreasurer.value) {
    return {
      kicker: 'Treasury workspace',
      title: 'Balances, contribution records, and payments',
      description:
        'Use the finance workspace to review balances, payment activity, and the member records needed for treasury follow-up.',
      primary: { label: 'Go to finance workspace', to: '/finance' },
      links: [
        { label: 'Review member profile', to: '/members/profile' },
        { label: 'Open finance audit', to: '/finance-audit' },
      ],
    }
  }

  if (isSecretaryGeneral.value) {
    return {
      kicker: 'Secretary workspace',
      title: 'Documents, policies, and announcements',
      description:
        'Stay inside the secretary workspace to update documents, maintain policies, and publish association announcements.',
      primary: { label: 'Open secretary workspace', to: '/secretary' },
      links: [
        { label: 'Review documents', to: '/secretary/documents' },
        { label: 'Review policies', to: '/secretary/policies' },
      ],
    }
  }

  if (isAuditor.value) {
    return {
      kicker: 'Finance audit',
      title: 'Read-only oversight and audit-ready records',
      description:
        'Inspect finance totals and audit-ready records without mutation controls or unnecessary workspace clutter.',
      primary: { label: 'Open finance audit', to: '/finance-audit' },
      links: [
        { label: 'Review member directory', to: '/members/profile' },
        { label: 'Review finance workspace', to: '/finance' },
      ],
    }
  }

  if (isCensor.value) {
    return {
      kicker: 'Disciplinary console',
      title: 'Privacy-safe record review',
      description:
        'Work inside the disciplinary console with strict privacy boundaries so only authorized records stay visible.',
      primary: { label: 'Manage disciplinary records', to: '/censor' },
      links: [
        { label: 'Review policies', to: '/policies' },
        { label: 'Ask the assistant', to: '/chat' },
      ],
    }
  }

  if (isSportsManager.value) {
    return {
      kicker: 'Sports workspace',
      title: 'Training sessions, fixtures, and club activity',
      description:
        'Manage sports events from a focused workspace that keeps fixtures, updates, and community activity in one place.',
      primary: { label: 'Open sports workspace', to: '/sports' },
      links: [
        { label: 'Review events', to: '/events' },
        { label: 'Ask the assistant', to: '/chat' },
      ],
    }
  }

  if (isPresidentRole.value || isVicePresidentRole.value) {
    return {
      kicker: 'Executive oversight',
      title: 'Governance, member visibility, and coordination',
      description:
        'Use the governance cockpit for oversight, coordination, and a clean path to the association spaces that matter most.',
      primary: { label: 'Open governance cockpit', to: '/governance' },
      links: [
        { label: 'Review finance audit', to: '/finance-audit' },
        { label: 'Read announcements', to: '/announcements' },
      ],
    }
  }

  return {
    kicker: 'Tenant overview',
    title: 'The next step that matters most',
    description:
      'Use the dashboard to jump into the next workspace that matters most for your role and the current tenant state.',
    primary: { label: 'Open dashboard', to: '/dashboard' },
    links: [
      { label: 'Admin settings', to: '/admin/settings' },
      { label: 'Ask the assistant', to: '/chat' },
    ],
  }
})

const quickActions = computed(() => {
  const actions: Array<{ label: string; to: string; icon: string }> = []

  if (isMemberOnly.value) {
    actions.push({ label: 'Open my profile', to: '/members/profile', icon: 'bi bi-person-badge' })
    if (tenantStore.isModuleEnabled('chat')) {
      actions.push({ label: 'Ask the assistant', to: '/chat', icon: 'bi bi-chat-dots' })
    }
    if (tenantStore.isModuleEnabled('events')) {
      actions.push({ label: 'Review events', to: '/events', icon: 'bi bi-calendar-event' })
    }
    if (tenantStore.isModuleEnabled('announcements')) {
      actions.push({ label: 'Read announcements', to: '/announcements', icon: 'bi bi-megaphone' })
    }
  } else if (isAdmin.value || isPrincipalAdmin.value) {
    actions.push({
      label: isPrincipalAdmin.value ? 'Open principal admin control plane' : 'Review tenant settings',
      to: '/admin/settings',
      icon: 'bi bi-sliders',
    })
    actions.push({ label: 'Open onboarding wizard', to: '/admin/onboarding', icon: 'bi bi-stars' })
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

  if (
    isAuditor.value ||
    isPresidentRole.value ||
    isVicePresidentRole.value ||
    isSecretaryGeneral.value ||
    isTreasurer.value ||
    isCensor.value ||
    isSportsManager.value ||
    isPrincipalAdmin.value ||
    isAdmin.value
  ) {
    actions.push({
      label: 'Open health center',
      to: '/admin/health',
      icon: 'bi bi-heart-pulse',
    })
  }

  if (tenantStore.isModuleEnabled('disciplinary') && (isCensor.value || isPresident.value || isPrincipalAdmin.value || isAdmin.value)) {
    actions.push({
      label: isCensor.value ? 'Manage disciplinary records' : 'Review disciplinary oversight',
      to: '/censor',
      icon: 'bi bi-shield-lock',
    })
  }

  if (tenantStore.isModuleEnabled('announcements')) {
    actions.push({
      label: isAdmin.value || isPrincipalAdmin.value || isSecretaryGeneral.value ? 'Publish announcement' : 'Review announcements',
      to: isAdmin.value || isPrincipalAdmin.value ? '/admin/announcements' : isSecretaryGeneral.value ? '/secretary/announcements' : '/announcements',
      icon: 'bi bi-megaphone',
    })
  }

  if (tenantStore.isModuleEnabled('events')) {
    if (isSportsManager.value || isPrincipalAdmin.value || isAdmin.value) {
      actions.push({
        label: 'Open sports workspace',
        to: '/sports',
        icon: 'bi bi-trophy',
      })
    }
    actions.push({
      label: isAdmin.value || isPrincipalAdmin.value ? 'Schedule event' : 'Review events',
      to: isAdmin.value || isPrincipalAdmin.value ? '/admin/events' : '/events',
      icon: 'bi bi-calendar-event',
    })
  }

  if (isPresidentRole.value || isVicePresidentRole.value || isPrincipalAdmin.value || isAdmin.value) {
    actions.push({
      label: 'Open governance cockpit',
      to: '/governance',
      icon: 'bi bi-diagram-3',
    })
  }

  return actions
})

const isSetupMode = computed(() => {
  return progressPercent.value < 100 && completedCount.value === 0
})

const dashboardKicker = computed(() => {
  if (isPrincipalAdmin.value) return 'Principal admin control plane'
  if (isMemberOnly.value) return 'Member portal'
  if (isTreasurer.value) return 'Finance workspace'
  if (isSecretaryGeneral.value) return 'Secretary workspace'
  if (isAuditor.value) return 'Finance audit'
  if (isCensor.value) return 'Disciplinary console'
  if (isSportsManager.value) return 'Sports workspace'
  if (isPresidentRole.value || isVicePresidentRole.value) return 'Governance cockpit'
  return 'Tenant overview'
})

const dashboardLead = computed(() => {
  if (isPrincipalAdmin.value) {
    return `Your current tenant is ${tenantStore.currentTenantName}. Use the control plane for tenant-wide administration without breaking isolation.`
  }
  if (isMemberOnly.value) {
    return `Your current tenant is ${tenantStore.currentTenantName}. Review your personal profile, contribution statement, and read-only association updates.`
  }
  if (isTreasurer.value) {
    return `Your current tenant is ${tenantStore.currentTenantName}. Review finance tasks, member balances, and payment activity from the dedicated workspace.`
  }
  if (isSecretaryGeneral.value) {
    return `Your current tenant is ${tenantStore.currentTenantName}. Keep documents, policies, and announcements tidy from the secretary workspace.`
  }
  if (isAuditor.value) {
    return `Your current tenant is ${tenantStore.currentTenantName}. Inspect finance totals and audit-ready records without mutation controls.`
  }
  if (isCensor.value) {
    return `Your current tenant is ${tenantStore.currentTenantName}. Work inside the disciplinary console with privacy boundaries preserved.`
  }
  if (isSportsManager.value) {
    return `Your current tenant is ${tenantStore.currentTenantName}. Manage sports events in a focused workspace with no extra noise.`
  }
  if (isPresidentRole.value || isVicePresidentRole.value) {
    return `Your current tenant is ${tenantStore.currentTenantName}. Use the governance cockpit for focused oversight across the association.`
  }
  return `Your current tenant is ${tenantStore.currentTenantName}. The dashboard highlights the next steps that matter most.`
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
