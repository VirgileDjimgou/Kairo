<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-xl-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2" data-testid="admin-onboarding-kicker">
          First-run setup
        </div>
        <h1 class="h4 fw-bold mb-1" data-testid="admin-onboarding-title">Onboarding wizard</h1>
        <p class="text-muted mb-0">
          {{ introCopy }}
        </p>
      </div>
      <div class="d-flex gap-2 align-self-start">
        <RouterLink to="/admin/health" class="btn btn-outline-secondary" data-testid="admin-onboarding-health-button">
          <i class="bi bi-heart-pulse me-1"></i>Health center
        </RouterLink>
        <button class="btn om-primary-btn" type="button" :disabled="loading" @click="refresh">
          {{ loading ? 'Refreshing...' : 'Refresh setup state' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-warning border-0 shadow-sm mb-4">
      <i class="bi bi-exclamation-triangle me-2"></i>{{ error }}
    </div>

    <div class="row g-4">
      <div class="col-xl-8">
        <div class="card shadow-sm border-0 onboarding-card h-100" data-testid="admin-onboarding-checklist">
          <div class="card-body p-4 p-xl-5">
            <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-4">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  Launch checklist
                </div>
                <h2 class="h5 fw-bold mb-2">{{ statusTitle }}</h2>
                <p class="text-muted mb-0">
                  {{ statusMessage }}
                </p>
              </div>
              <div class="text-md-end">
                <div class="display-6 fw-bold lh-1" data-testid="admin-onboarding-progress">
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

            <div v-if="nextStep" class="alert alert-primary border-0 mb-4" data-testid="admin-onboarding-next-step">
              <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
                <div>
                  <div class="fw-semibold mb-1">Next best action</div>
                  <p class="small mb-0">
                    {{ nextStep.title }}: {{ nextStep.description }}
                  </p>
                </div>
                <RouterLink :to="nextStep.to" class="btn btn-sm btn-primary align-self-start">
                  {{ nextStep.actionLabel }}
                </RouterLink>
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
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              First actions
            </div>
            <h2 class="h6 fw-bold mb-3">What to do first</h2>
            <ol class="setup-list mb-0">
              <li>Confirm tenant branding and module toggles.</li>
              <li>Upload the first trusted document.</li>
              <li>Add or import members and review access.</li>
              <li>Publish the first announcement or event.</li>
              <li>Verify the health center and recovery evidence.</li>
            </ol>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Demo seed
            </div>
            <h2 class="h6 fw-bold mb-3">Populate a second tenant for browser demos</h2>
            <p class="small text-muted mb-3">
              Use the multi-tenant helper when you want a repeatable demo stack. Keep production data separate and import customer data explicitly.
            </p>

            <div class="seed-block mb-3" data-testid="admin-onboarding-seed-bash">
              <div class="small text-muted mb-2">macOS / Linux</div>
              <code>./seed/seed-multi-tenant.sh</code>
            </div>

            <div class="seed-block" data-testid="admin-onboarding-seed-powershell">
              <div class="small text-muted mb-2">Windows PowerShell</div>
              <code>.\seed\seed-multi-tenant.ps1</code>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Guided links
            </div>
            <div class="vstack gap-2" data-testid="admin-onboarding-links">
              <RouterLink
                v-for="link in guidedLinks"
                :key="link.to"
                :to="link.to"
                class="wizard-link"
              >
                <div class="fw-semibold">{{ link.label }}</div>
                <div class="small text-muted">{{ link.description }}</div>
              </RouterLink>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              Success criteria
            </div>
            <h2 class="h6 fw-bold mb-3">First week ready</h2>
            <ul class="success-list mb-0">
              <li>The admin can sign in and understand the tenant state immediately.</li>
              <li>The first document is visible and ingesting correctly.</li>
              <li>Members can be added or imported without confusion.</li>
              <li>Launch communications and events have a clear place to live.</li>
              <li>Recovery evidence is visible in the health center and settings.</li>
            </ul>
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
import { useTenantOnboarding } from '@/composables/useTenantOnboarding'

const authStore = useAuthStore()
const isPrincipalAdmin = computed(() => authStore.user?.roles.includes('principal_admin') ?? false)
const introCopy = computed(() =>
  isPrincipalAdmin.value
    ? 'Use this control-plane view to move from a blank tenant into a working launch configuration without mixing demo guidance with live production decisions.'
    : 'Use this setup view to move from a blank tenant into a working launch configuration with a clear sequence and a predictable demo seed path.',
)

const {
  loading,
  error,
  checklist,
  progressPercent,
  statusTitle,
  statusMessage,
  nextStep,
  refresh,
} = useTenantOnboarding()

const guidedLinks = [
  {
    label: 'Tenant settings',
    description: 'Branding, modules, and recovery evidence',
    to: '/admin/settings',
  },
  {
    label: 'Documents',
    description: 'Upload the first trusted source',
    to: '/admin/documents',
  },
  {
    label: 'Members',
    description: 'Import or create the first directory entries',
    to: '/admin/members',
  },
  {
    label: 'Access',
    description: 'Invite teammates and monitor onboarding',
    to: '/admin/access',
  },
  {
    label: 'Announcements',
    description: 'Publish the first communication',
    to: '/admin/announcements',
  },
  {
    label: 'Events',
    description: 'Schedule the first activity',
    to: '/admin/events',
  },
  {
    label: 'Tenant operations',
    description: 'Inspect memberships and switch context explicitly',
    to: '/admin/tenants',
  },
]

function stepIcon(stepId: string): string {
  const icons: Record<string, string> = {
    branding: 'bi bi-palette',
    documents: 'bi bi-file-earmark-text',
    finance: 'bi bi-cash-coin',
    members: 'bi bi-people',
    announcements: 'bi bi-megaphone',
    events: 'bi bi-calendar-event',
  }

  return icons[stepId] || 'bi bi-arrow-right'
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

.wizard-link {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 0.95rem;
  padding: 0.85rem 1rem;
  text-decoration: none;
  color: inherit;
  background: #fff;
}

.wizard-link:hover {
  border-color: var(--om-primary, #1f4f8f);
  box-shadow: 0 0.5rem 1rem rgba(31, 79, 143, 0.08);
}

.seed-block {
  border: 1px solid var(--om-border, #d9e2ec);
  border-radius: 0.95rem;
  padding: 0.85rem 1rem;
  background: #fff;
}

.setup-list,
.success-list {
  padding-left: 1.15rem;
}
</style>
