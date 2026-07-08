<template>
  <div class="p-4 p-lg-5">
    <div class="governance-hero rounded-4 p-4 p-lg-5 mb-4" data-testid="governance-cockpit-hero">
      <div class="d-flex flex-column flex-xl-row justify-content-between gap-4 align-items-xl-end">
        <div>
          <div class="text-uppercase small fw-semibold text-secondary mb-2">{{ copy.heroKicker }}</div>
          <h1 class="h3 fw-bold mb-2">{{ heading }}</h1>
          <p class="text-muted mb-0 hero-copy" data-testid="governance-cockpit-subtitle">{{ subtitle }}</p>
        </div>
        <div class="d-flex gap-2 align-items-start">
          <button class="btn btn-outline-secondary btn-sm" type="button" @click="refresh" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
            {{ copy.refresh }}
          </button>
          <RouterLink
            v-if="showFinanceAuditLink"
            to="/finance-audit"
            class="btn btn-primary btn-sm"
            data-testid="governance-finance-link"
          >
            <i class="bi bi-clipboard-data me-1"></i>{{ copy.financeAudit }}
          </RouterLink>
        </div>
      </div>

      <div class="row g-3 mt-3">
        <div class="col-md-4">
          <div class="metric-card h-100">
            <div class="small text-muted">{{ copy.roleScope }}</div>
            <div class="fs-4 fw-bold">{{ roleLabel }}</div>
            <div class="small text-secondary">{{ copy.roleScopeHint }}</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="metric-card h-100">
            <div class="small text-muted">{{ copy.activeAnnouncements }}</div>
            <div class="fs-4 fw-bold">{{ announcementsCount }}</div>
            <div class="small text-secondary">{{ copy.activeAnnouncementsHint }}</div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="metric-card h-100">
            <div class="small text-muted">{{ copy.upcomingEvents }}</div>
            <div class="fs-4 fw-bold">{{ eventsCount }}</div>
            <div class="small text-secondary">{{ copy.upcomingEventsHint }}</div>
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
              <RouterLink v-if="card.to" :to="card.to" class="btn btn-sm btn-outline-primary">{{ copy.open }}</RouterLink>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-lg-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">{{ copy.executiveActions }}</div>
                <h2 class="h6 fw-bold mb-1">{{ copy.limitedShortcuts }}</h2>
                <p class="text-muted small mb-0">
                  {{ copy.limitedShortcutsHint }}
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
                <div class="text-uppercase small fw-semibold text-secondary mb-2">{{ copy.contextSnapshots }}</div>
                <h2 class="h6 fw-bold mb-1">{{ copy.roleSensitiveVisibility }}</h2>
                <p class="text-muted small mb-0">
                  {{ copy.roleSensitiveVisibilityHint }}
                </p>
              </div>
              <span class="badge bg-light text-dark border align-self-start">
                {{ hasAuditAccess ? copy.auditEnabled : copy.auditHidden }}
              </span>
            </div>

            <div class="row g-3">
              <div class="col-md-6">
                <div class="snapshot-card h-100" data-testid="governance-finance-snapshot">
                  <div class="small text-muted mb-1">{{ copy.finance }}</div>
                  <div class="fw-bold fs-5">{{ financeValue }}</div>
                  <div class="small text-secondary">
                    {{ financeHint }}
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="snapshot-card h-100">
                  <div class="small text-muted mb-1">{{ copy.governanceDocuments }}</div>
                  <div class="fw-bold fs-5">{{ documentsCount }}</div>
                  <div class="small text-secondary">
                    {{ copy.governanceDocumentsHint }}
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="snapshot-card h-100">
                  <div class="small text-muted mb-1">{{ copy.memberDirectory }}</div>
                  <div class="fw-bold fs-5">{{ membersCount }}</div>
                  <div class="small text-secondary">
                    {{ copy.memberDirectoryHint }}
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="snapshot-card h-100">
                  <div class="small text-muted mb-1">{{ copy.auditTrail }}</div>
                  <div class="fw-bold fs-5">{{ auditCount }}</div>
                  <div class="small text-secondary">
                    {{ hasAuditAccess ? copy.recentSensitiveActions : copy.hiddenForRole }}
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
            <div class="text-uppercase small fw-semibold text-secondary mb-2">{{ copy.currentTenant }}</div>
            <div class="vstack gap-2 small">
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.tenant }}</span>
                <span class="fw-semibold text-end">{{ tenantStore.currentTenantName }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.roles }}</span>
                <span class="fw-semibold text-end">{{ authStore.user?.roles.join(', ') || '—' }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.announcements }}</span>
                <span class="fw-semibold text-end">{{ announcementsCount }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.events }}</span>
                <span class="fw-semibold text-end">{{ eventsCount }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">{{ copy.rolePosture }}</div>
            <p class="small text-muted mb-3">
              {{ copy.rolePostureHint }}
            </p>
            <div class="vstack gap-2 small">
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.presidentView }}</span>
                <span class="fw-semibold text-end">{{ isPresident ? copy.enabled : copy.notCurrentRole }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.vicePresidentView }}</span>
                <span class="fw-semibold text-end">{{ isVicePresident ? copy.enabled : copy.notCurrentRole }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.principalAdmin }}</span>
                <span class="fw-semibold text-end">{{ isPrincipalAdmin ? copy.enabled : copy.notCurrentRole }}</span>
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
import { useLocaleStore } from '@/stores/locale.store'

const authStore = useAuthStore()
const tenantStore = useTenantStore()
const localeStore = useLocaleStore()
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
  if (localeStore.currentLocale === 'de') {
    if (isPresident.value) return 'Praesident'
    if (isVicePresident.value) return 'Vizepraesident'
    if (isPrincipalAdmin.value) return 'Hauptadministrator'
    if (isAdmin.value) return 'Administrator'
    return 'Exekutive Rolle'
  }
  if (localeStore.currentLocale === 'en') {
    if (isPresident.value) return 'President'
    if (isVicePresident.value) return 'Vice President'
    if (isPrincipalAdmin.value) return 'Principal Admin'
    if (isAdmin.value) return 'Admin'
    return 'Executive role'
  }
  if (isPresident.value) return 'Président'
  if (isVicePresident.value) return 'Vice-président'
  if (isPrincipalAdmin.value) return 'Administrateur principal'
  if (isAdmin.value) return 'Administrateur'
  return 'Rôle exécutif'
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
  return financeCard.value?.hint || (localeStore.currentLocale === 'de' ? 'Aucun résumé financier disponible' : localeStore.currentLocale === 'en' ? 'No finance summary available' : 'Aucun résumé financier disponible')
})

const hasAuditAccess = computed(() => isPresident.value || isPrincipalAdmin.value || isAdmin.value)
const showFinanceAuditLink = computed(() => isPresident.value || isPrincipalAdmin.value || isAdmin.value)

const copy = computed(() => {
  if (localeStore.currentLocale === 'de') {
    return {
      heroKicker: 'Exekutive Aufsicht',
      refresh: 'Aktualisieren',
      financeAudit: 'Finanzaudit',
      roleScope: 'Rollenumfang',
      roleScopeHint: 'Aus der authentifizierten Tenant-Sitzung abgeleitet.',
      activeAnnouncements: 'Aktive Ankuendigungen',
      activeAnnouncementsHint: 'Aktuelle Mitteilungen fuer Mitglieder.',
      upcomingEvents: 'Bevorstehende Veranstaltungen',
      upcomingEventsHint: 'Geplante Vereinsaktivitaet.',
      open: 'Oeffnen',
      executiveActions: 'Exekutive Aktionen',
      limitedShortcuts: 'Begrenzte Aufsichtsverknuepfungen',
      limitedShortcutsHint: 'Diese Aktionen halten die Gouvernance auf leseorientierten Flaechen und vermeiden breite Administration.',
      contextSnapshots: 'Kontext-Snapshots',
      roleSensitiveVisibility: 'Rollensensible Sichtbarkeit',
      roleSensitiveVisibilityHint: 'Der Praesident sieht breiter, der Vizepraesident enger und zielgerichteter.',
      auditEnabled: 'Audit aktiv',
      auditHidden: 'Audit ausgeblendet',
      finance: 'Finanzen',
      governanceDocuments: 'Governance-Dokumente',
      governanceDocumentsHint: 'Referenzdokumente, die in Ihrer Tenant-Sitzung sichtbar sind.',
      memberDirectory: 'Mitgliederverzeichnis',
      memberDirectoryHint: 'Mitgliedersicht fuer Aufsicht und Koordination.',
      auditTrail: 'Audit-Protokoll',
      recentSensitiveActions: 'Kuerzliche sensible Aktionen',
      hiddenForRole: 'Fuer diese Rolle verborgen',
      currentTenant: 'Aktueller Tenant',
      tenant: 'Tenant',
      roles: 'Rollen',
      announcements: 'Ankuendigungen',
      events: 'Veranstaltungen',
      rolePosture: 'Rollenhaltung',
      rolePostureHint: 'Das Cockpit bleibt leseorientiert. Weitergehende Aktionen prueft weiterhin das Backend.',
      presidentView: 'Praesidentenansicht',
      vicePresidentView: 'Vizepraesidentenansicht',
      principalAdmin: 'Hauptadministrator',
      enabled: 'Aktiv',
      notCurrentRole: 'Nicht aktuelle Rolle',
    }
  }
  if (localeStore.currentLocale === 'en') {
    return {
      heroKicker: 'Executive oversight',
      refresh: 'Refresh',
      financeAudit: 'Finance audit',
      roleScope: 'Role scope',
      roleScopeHint: 'Resolved from the authenticated tenant session.',
      activeAnnouncements: 'Active announcements',
      activeAnnouncementsHint: 'Current member-facing notices.',
      upcomingEvents: 'Upcoming events',
      upcomingEventsHint: 'Scheduled organization activity.',
      open: 'Open',
      executiveActions: 'Executive actions',
      limitedShortcuts: 'Limited oversight shortcuts',
      limitedShortcutsHint: 'These actions keep governance focused on read-first surfaces instead of broad system administration.',
      contextSnapshots: 'Context snapshots',
      roleSensitiveVisibility: 'Role-sensitive visibility',
      roleSensitiveVisibilityHint: 'The president sees a broader governance surface, while the vice president keeps a narrower profile.',
      auditEnabled: 'Audit enabled',
      auditHidden: 'Audit hidden',
      finance: 'Finance',
      governanceDocuments: 'Governance documents',
      governanceDocumentsHint: 'Reference documents visible to your tenant session.',
      memberDirectory: 'Member directory',
      memberDirectoryHint: 'Tenant membership scope for oversight and coordination.',
      auditTrail: 'Audit trail',
      recentSensitiveActions: 'Recent sensitive actions',
      hiddenForRole: 'Hidden for this role',
      currentTenant: 'Current tenant',
      tenant: 'Tenant',
      roles: 'Roles',
      announcements: 'Announcements',
      events: 'Events',
      rolePosture: 'Role posture',
      rolePostureHint: 'The cockpit stays read-first. Anything beyond this screen continues to depend on backend capability checks.',
      presidentView: 'President view',
      vicePresidentView: 'Vice president view',
      principalAdmin: 'Principal admin',
      enabled: 'Enabled',
      notCurrentRole: 'Not current role',
    }
  }
  return {
    heroKicker: 'Supervision exécutive',
    refresh: 'Actualiser',
    financeAudit: 'Audit finances',
    roleScope: 'Périmètre du rôle',
    roleScopeHint: 'Déduit depuis la session tenant authentifiée.',
    activeAnnouncements: 'Annonces actives',
    activeAnnouncementsHint: 'Communications visibles par les membres.',
    upcomingEvents: 'Événements à venir',
    upcomingEventsHint: "Activité planifiée de l'association.",
    open: 'Ouvrir',
    executiveActions: 'Actions exécutives',
    limitedShortcuts: 'Raccourcis de supervision limités',
    limitedShortcutsHint: 'Ces actions gardent la gouvernance centrée sur la lecture, sans administration trop large.',
    contextSnapshots: 'Instantanés de contexte',
    roleSensitiveVisibility: 'Visibilité sensible au rôle',
    roleSensitiveVisibilityHint: 'Le président voit plus large, tandis que le vice-président garde une vue plus resserrée.',
    auditEnabled: 'Audit actif',
    auditHidden: 'Audit masqué',
    finance: 'Finances',
    governanceDocuments: 'Documents de gouvernance',
    governanceDocumentsHint: 'Documents de référence visibles dans votre session tenant.',
    memberDirectory: 'Répertoire des membres',
    memberDirectoryHint: 'Périmètre membre utile à la supervision et à la coordination.',
    auditTrail: "Journal d'audit",
    recentSensitiveActions: 'Actions sensibles récentes',
    hiddenForRole: 'Masqué pour ce rôle',
    currentTenant: 'Tenant actuel',
    tenant: 'Tenant',
    roles: 'Rôles',
    announcements: 'Annonces',
    events: 'Événements',
    rolePosture: 'Posture du rôle',
    rolePostureHint: 'Le cockpit reste orienté lecture. Toute action plus sensible reste validée par le backend.',
    presidentView: 'Vue président',
    vicePresidentView: 'Vue vice-président',
    principalAdmin: 'Administrateur principal',
    enabled: 'Actif',
    notCurrentRole: 'Rôle non courant',
  }
})

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
