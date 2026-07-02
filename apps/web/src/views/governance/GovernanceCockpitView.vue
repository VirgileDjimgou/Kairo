<template>
  <div class="p-4 p-lg-5">
    <div class="governance-hero rounded-4 p-4 p-lg-5 mb-4" data-testid="governance-cockpit-hero">
      <div class="d-flex flex-column flex-xl-row justify-content-between gap-4 align-items-xl-end">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary mb-2">Executive oversight</div>
          <h1 class="h3 fw-bold mb-2">{{ heading }}</h1>
          <p class="text-muted mb-0 hero-copy" data-testid="governance-cockpit-subtitle">{{ subtitle }}</p>
        </div>
        <div class="d-flex gap-2 align-items-start">
          <button class="btn btn-outline-secondary btn-sm" type="button" @click="refresh" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
            Refresh
          </button>
          <RouterLink
            v-if="showFinanceAuditLink"
            to="/finance-audit"
            class="btn btn-primary btn-sm"
            data-testid="governance-finance-link"
          >
            <i class="bi bi-clipboard-data me-1"></i>Finance audit
          </RouterLink>
        </div>
      </div>

      <div class="row g-3 mt-3">
        <div class="col-md-4">
          <div class="metric-card h-100">
            <div class="small text-muted">Role scope</div>
            <div class="fs-4 fw-bold">{{ roleLabel }}</div>
            <div class="small text-secondary">Resolved from the authenticated tenant session.</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="metric-card h-100">
            <div class="small text-muted">Active announcements</div>
            <div class="fs-4 fw-bold">{{ announcementsCount }}</div>
            <div class="small text-secondary">Current member-facing notices.</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="metric-card h-100">
            <div class="small text-muted">Upcoming events</div>
            <div class="fs-4 fw-bold">{{ eventsCount }}</div>
            <div class="small text-secondary">Scheduled organization activity.</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger alert-dismissible small py-2 mb-4" role="alert">
      <i class="bi bi-exclamation-triangle me-1"></i>{{ error }}
      <button type="button" class="btn-close py-2" @click="error = ''"></button>
    </div>

    <div class="row g-4">
      <div class="col-xl-8">
        <div class="row g-3 mb-4">
          <div v-for="card in cards" :key="card.id" class="col-md-6 col-xxl-4">
            <div class="summary-card h-100" :class="toneClass(card.tone)">
              <div class="small text-muted mb-2">{{ card.label }}</div>
              <div class="summary-value mb-1">{{ card.value }}</div>
              <div class="small text-secondary mb-3">{{ card.hint }}</div>
              <RouterLink v-if="card.to" :to="card.to" class="btn btn-sm btn-outline-primary">Open</RouterLink>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">Executive actions</div>
                <h2 class="h6 fw-bold mb-1">Limited oversight shortcuts</h2>
                <p class="text-muted small mb-0">
                  These actions keep governance focused on read-first surfaces instead of broad system administration.
                </p>
              </div>
            </div>

            <div class="vstack gap-2">
              <RouterLink
                v-for="action in quickActions"
                :key="action.id"
                :to="action.to"
                class="action-card"
              >
                <div class="fw-semibold">{{ action.label }}</div>
                <div class="small text-muted">{{ action.description }}</div>
              </RouterLink>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">Context snapshots</div>
                <h2 class="h6 fw-bold mb-1">Role-sensitive visibility</h2>
                <p class="text-muted small mb-0">
                  The president sees a broader governance surface, while the vice president keeps a narrower oversight profile.
                </p>
              </div>
              <span class="badge bg-light text-dark border align-self-start">
                {{ hasAuditAccess ? 'Audit enabled' : 'Audit hidden' }}
              </span>
            </div>

            <div class="row g-3">
              <div class="col-md-6">
                <div class="snapshot-card h-100" data-testid="governance-finance-snapshot">
                  <div class="small text-muted mb-1">Finance</div>
                  <div class="fw-bold fs-5">{{ financeValue }}</div>
                  <div class="small text-secondary">
                    {{ financeHint }}
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="snapshot-card h-100">
                  <div class="small text-muted mb-1">Governance documents</div>
                  <div class="fw-bold fs-5">{{ documentsCount }}</div>
                  <div class="small text-secondary">
                    Reference documents visible to your tenant session.
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="snapshot-card h-100">
                  <div class="small text-muted mb-1">Member directory</div>
                  <div class="fw-bold fs-5">{{ membersCount }}</div>
                  <div class="small text-secondary">
                    Tenant membership scope for oversight and coordination.
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="snapshot-card h-100">
                  <div class="small text-muted mb-1">Audit trail</div>
                  <div class="fw-bold fs-5">{{ auditCount }}</div>
                  <div class="small text-secondary">
                    {{ hasAuditAccess ? 'Recent sensitive actions' : 'Hidden for this role' }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-xl-4">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">Current tenant</div>
            <div class="vstack gap-2 small">
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Tenant</span>
                <span class="fw-semibold text-end">{{ tenantStore.currentTenantName }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Roles</span>
                <span class="fw-semibold text-end">{{ authStore.user?.roles.join(', ') || '—' }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Announcements</span>
                <span class="fw-semibold text-end">{{ announcementsCount }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Events</span>
                <span class="fw-semibold text-end">{{ eventsCount }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">Role posture</div>
            <p class="small text-muted mb-3">
              The cockpit stays read-first. Anything beyond this screen continues to depend on backend capability checks.
            </p>
            <div class="vstack gap-2 small">
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">President view</span>
                <span class="fw-semibold text-end">{{ isPresident ? 'Enabled' : 'Not current role' }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Vice president view</span>
                <span class="fw-semibold text-end">{{ isVicePresident ? 'Enabled' : 'Not current role' }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">Principal admin</span>
                <span class="fw-semibold text-end">{{ isPrincipalAdmin ? 'Enabled' : 'Not current role' }}</span>
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
import { useGovernanceCockpit } from '@/composables/useGovernanceCockpit'

const authStore = useAuthStore()
const tenantStore = useTenantStore()
const {
  loading,
  error,
  heading,
  subtitle,
  cards,
  quickActions,
  refresh,
  isPresident,
  isVicePresident,
  isPrincipalAdmin,
  isAdmin,
} = useGovernanceCockpit()

const roleLabel = computed(() => {
  if (isPresident.value) return 'President'
  if (isVicePresident.value) return 'Vice President'
  if (isPrincipalAdmin.value) return 'Principal Admin'
  if (isAdmin.value) return 'Admin'
  return 'Executive role'
})

const financeCard = computed(() => cards.value.find((card) => card.id === 'finance'))

const documentsCount = computed(() => {
  const card = cards.value.find((item) => item.id === 'documents')
  return card ? card.value : '0'
})

const membersCount = computed(() => {
  const card = cards.value.find((item) => item.id === 'members')
  return card ? card.value : '0'
})

const announcementsCount = computed(() => {
  const card = cards.value.find((item) => item.id === 'announcements')
  return card ? card.value : '0'
})

const eventsCount = computed(() => {
  const card = cards.value.find((item) => item.id === 'events')
  return card ? card.value : '0'
})

const auditCount = computed(() => {
  const card = cards.value.find((item) => item.id === 'audit')
  return card ? card.value : '0'
})

const financeValue = computed(() => {
  return financeCard.value ? financeCard.value.value : '—'
})

const financeHint = computed(() => {
  return financeCard.value?.hint || 'No finance summary available'
})

const hasAuditAccess = computed(() => isPresident.value || isPrincipalAdmin.value || isAdmin.value)
const showFinanceAuditLink = computed(() => isPresident.value || isPrincipalAdmin.value || isAdmin.value)

function toneClass(tone: 'neutral' | 'success' | 'warning' | 'danger') {
  return {
    neutral: '',
    success: 'tone-success',
    warning: 'tone-warning',
    danger: 'tone-danger',
  }[tone]
}

onMounted(refresh)
</script>

<style scoped>
.governance-hero {
  background:
    radial-gradient(circle at top right, rgba(191, 219, 254, 0.28), transparent 30%),
    radial-gradient(circle at bottom left, rgba(37, 99, 235, 0.08), transparent 28%),
    linear-gradient(135deg, #f7fafc 0%, #ffffff 72%);
  border: 1px solid #e3e8ef;
}

.hero-copy {
  max-width: 46rem;
}

.metric-card,
.summary-card,
.snapshot-card,
.action-card {
  border: 1px solid #dbe3ed;
  border-radius: 1rem;
  background: #fff;
}

.metric-card,
.snapshot-card {
  padding: 1rem;
}

.summary-card {
  padding: 1rem;
}

.summary-value {
  font-size: 1.9rem;
  font-weight: 700;
  line-height: 1;
}

.action-card {
  display: block;
  padding: 0.9rem 1rem;
  text-decoration: none;
  color: inherit;
}

.action-card:hover {
  border-color: rgba(31, 79, 143, 0.24);
  background: rgba(31, 79, 143, 0.03);
}

.tone-success {
  border-color: rgba(25, 135, 84, 0.22);
}

.tone-warning {
  border-color: rgba(255, 193, 7, 0.26);
}

.tone-danger {
  border-color: rgba(220, 53, 69, 0.22);
}
</style>
