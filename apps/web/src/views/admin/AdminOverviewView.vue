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
        <RouterLink to="/admin/onboarding" class="btn btn-outline-secondary" data-testid="admin-overview-onboarding-button">
          <i class="bi bi-stars me-1"></i>{{ copy.onboardingWizard }}
        </RouterLink>
        <RouterLink to="/admin/health" class="btn btn-outline-secondary" data-testid="admin-overview-health-button">
          <i class="bi bi-heart-pulse me-1"></i>{{ copy.healthCenter }}
        </RouterLink>
        <RouterLink to="/admin/tenants" class="btn btn-outline-secondary">
          <i class="bi bi-diagram-3 me-1"></i>{{ copy.tenantOperations }}
        </RouterLink>
        <RouterLink to="/admin/settings" class="btn btn-outline-secondary">
          <i class="bi bi-gear me-1"></i>{{ copy.settings }}
        </RouterLink>
        <button class="btn om-primary-btn" type="button" @click="refresh" :disabled="loading || isRecovering">
          {{ loading ? copy.refreshing : copy.refreshOverview }}
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
          <p class="mb-0 small text-muted mt-1">{{ t('common.recoveryHint') }}</p>
        </div>
        <button class="btn btn-outline-secondary btn-sm align-self-start" type="button" @click="retryRefresh" :disabled="isRecovering">
          <span v-if="isRecovering" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
          {{ isRecovering ? t('common.loading') : t('common.retry') }}
        </button>
      </div>
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
                  {{ copy.operationalWatchlist }}
                </div>
                <h2 class="h6 fw-bold mb-1">{{ copy.warningsTitle }}</h2>
                <p class="text-muted small mb-0">
                  {{ copy.warningsLead }}
                </p>
              </div>
              <span class="badge bg-light text-dark border align-self-start">
                {{ riskItems.length }} {{ copy.itemsSuffix }}
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
                  {{ copy.onboardingContinuity }}
                </div>
                <h2 class="h6 fw-bold mb-1">{{ copy.launchReadiness }}</h2>
                <p class="text-muted small mb-0">
                  {{ copy.launchReadinessLead }}
                </p>
              </div>
              <div class="text-lg-end">
                <div class="fw-bold fs-4" data-testid="admin-overview-onboarding-progress">
                  {{ onboardingProgress }}%
                </div>
                <div class="small text-muted">{{ copy.checklistComplete }}</div>
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
                  <div class="fw-semibold mb-1">{{ copy.nextRecommendedAction }}</div>
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
              {{ copy.documentOperations }}
            </div>
            <h2 class="h6 fw-bold mb-3">{{ copy.ingestionHealth }}</h2>

            <div v-if="ingestionHealth" class="row g-2 mb-3">
              <div class="col-6">
                <div class="mini-stat">
                  <div class="small text-muted">{{ copy.queued }}</div>
                  <div class="fw-bold">{{ ingestionHealth.queued_count }}</div>
                </div>
              </div>
              <div class="col-6">
                <div class="mini-stat">
                  <div class="small text-muted">{{ copy.processing }}</div>
                  <div class="fw-bold">{{ ingestionHealth.processing_count }}</div>
                </div>
              </div>
              <div class="col-6">
                <div class="mini-stat">
                  <div class="small text-muted">{{ copy.failed }}</div>
                  <div class="fw-bold" :class="toneTextClass(ingestionHealth.failed_count > 0 ? 'danger' : 'success')">
                    {{ ingestionHealth.failed_count }}
                  </div>
                </div>
              </div>
              <div class="col-6">
                <div class="mini-stat">
                  <div class="small text-muted">{{ copy.retried }}</div>
                  <div class="fw-bold">{{ ingestionHealth.retried_count }}</div>
                </div>
              </div>
            </div>

            <div v-if="ingestionHealth?.recent_failures.length" class="small text-muted mb-3">
              {{ copy.latestFailure }}: {{ shortId(ingestionHealth.recent_failures[0]?.job_id ?? '') }}
            </div>

            <RouterLink to="/admin/documents" class="btn btn-outline-secondary btn-sm w-100">
              {{ copy.openDocumentOperations }}
            </RouterLink>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              {{ copy.quickActions }}
            </div>
            <div class="vstack gap-2" data-testid="admin-overview-quick-actions">
              <RouterLink
                v-for="action in quickActions"
                :key="action.id"
                :to="action.to"
                class="quick-action"
                :data-testid="`admin-quick-action-${action.id}`"
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
              {{ copy.tenantScope }}
            </div>
            <div class="vstack gap-2 small">
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.tenant }}</span>
                <span class="fw-semibold text-end">{{ tenantStore.currentTenantName }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.enabledModules }}</span>
                <span class="fw-semibold text-end">{{ enabledModuleCount }}</span>
              </div>
              <div class="d-flex justify-content-between gap-2">
                <span class="text-muted">{{ copy.openContributionBalance }}</span>
                <span class="fw-semibold text-end">
                  {{ contributionSummary?.total_balance ?? copy.na }}
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
import { useLocaleStore } from '@/stores/locale.store'
import { useTenantStore } from '@/stores/tenant.store'
import { useAdminOverview } from '@/composables/useAdminOverview'

const authStore = useAuthStore()
const localeStore = useLocaleStore()
const tenantStore = useTenantStore()
const t = (key: string) => localeStore.t(key)
const userRoles = computed(() => authStore.user?.roles ?? [])
const isPrincipalAdmin = computed(() => userRoles.value.includes('principal_admin'))
const copy = computed(() => {
  if (localeStore.currentLocale === 'de') {
    return {
      onboardingWizard: 'Onboarding-Assistent',
      healthCenter: 'Health Center',
      tenantOperations: 'Tenant-Operationen',
      settings: 'Einstellungen',
      refreshing: 'Aktualisierung...',
      refreshOverview: 'Übersicht aktualisieren',
      operationalWatchlist: 'Betriebliche Watchlist',
      warningsTitle: 'Warnungen und Bereitschaftslücken',
      warningsLead: 'Dieses Panel zeigt Einrichtungs- oder Betriebsprobleme, die Tenant-Admins am ehesten bremsen.',
      itemsSuffix: 'Eintrag(e)',
      onboardingContinuity: 'Onboarding-Kontinuität',
      launchReadiness: 'Startbereitschaft',
      launchReadinessLead: 'Nutzen dieselbe Tenant-Setup-Logik wie das Mitglieds-Dashboard, damit Admins das gleiche Startbild sehen.',
      checklistComplete: 'Checkliste abgeschlossen',
      nextRecommendedAction: 'Nächste empfohlene Admin-Aktion',
      documentOperations: 'Dokumentenbetrieb',
      ingestionHealth: 'Ingestion-Status',
      queued: 'Wartend',
      processing: 'In Bearbeitung',
      failed: 'Fehlgeschlagen',
      retried: 'Erneut versucht',
      latestFailure: 'Letzter Fehler',
      openDocumentOperations: 'Dokumentenbetrieb öffnen',
      quickActions: 'Schnellaktionen',
      tenantScope: 'Tenant-Umfang',
      tenant: 'Tenant',
      enabledModules: 'Aktive Module',
      openContributionBalance: 'Offener Beitragsbestand',
      hubAdmin: 'Administration',
      hubPrincipal: 'Hauptadministration',
      titleAdmin: 'Admin-Übersicht',
      titlePrincipal: 'Übersicht Hauptadmin',
      subtitleAdmin: 'Ein gemeinsamer Bildschirm für Tenant-Bereitschaft, Betriebssignale und die nächste sinnvolle Aktion.',
      subtitlePrincipal: 'Eine tenant-weite Steuerzentrale für Rollen, Einstellungen, Modulschalter und sensible Prüfungen.',
      workspaceErrorTitle: 'Admin-Uebersicht nicht verfügbar',
      na: 'n/v',
    }
  }
  if (localeStore.currentLocale === 'en') {
    return {
      onboardingWizard: 'Onboarding wizard',
      healthCenter: 'Health center',
      tenantOperations: 'Tenant operations',
      settings: 'Settings',
      refreshing: 'Refreshing...',
      refreshOverview: 'Refresh overview',
      operationalWatchlist: 'Operational watchlist',
      warningsTitle: 'Warnings and readiness gaps',
      warningsLead: 'This panel surfaces the setup or operational issues most likely to slow down a tenant admin.',
      itemsSuffix: 'item(s)',
      onboardingContinuity: 'Onboarding continuity',
      launchReadiness: 'Launch readiness',
      launchReadinessLead: 'Reuses the tenant setup logic from the member-facing dashboard so admins see the same launch picture.',
      checklistComplete: 'checklist complete',
      nextRecommendedAction: 'Next recommended admin action',
      documentOperations: 'Document operations',
      ingestionHealth: 'Ingestion health',
      queued: 'Queued',
      processing: 'Processing',
      failed: 'Failed',
      retried: 'Retried',
      latestFailure: 'Latest failure',
      openDocumentOperations: 'Open document operations',
      quickActions: 'Quick actions',
      tenantScope: 'Tenant scope',
      tenant: 'Tenant',
      enabledModules: 'Enabled modules',
      openContributionBalance: 'Open contribution balance',
      hubAdmin: 'Administration',
      hubPrincipal: 'Principal administration',
      titleAdmin: 'Admin overview',
      titlePrincipal: 'Principal admin overview',
      subtitleAdmin: 'A single screen for tenant readiness, operational signals, and the next action that deserves attention.',
      subtitlePrincipal: 'A tenant-wide control plane for role assignments, settings, module toggles, and sensitive review.',
      workspaceErrorTitle: 'Admin overview unavailable',
      na: 'n/a',
    }
  }
  return {
    onboardingWizard: 'Assistant de démarrage',
    healthCenter: 'Centre de santé',
    tenantOperations: 'Opérations tenant',
    settings: 'Réglages',
    refreshing: 'Actualisation...',
    refreshOverview: 'Actualiser la vue d’ensemble',
    operationalWatchlist: 'Liste de vigilance opérationnelle',
    warningsTitle: 'Avertissements et écarts de préparation',
    warningsLead: 'Ce panneau remonte les problèmes de configuration ou d’exploitation les plus susceptibles de ralentir un administrateur de tenant.',
    itemsSuffix: 'élément(s)',
    onboardingContinuity: 'Continuité du démarrage',
    launchReadiness: 'Préparation au lancement',
    launchReadinessLead: 'Réutilise la logique de configuration du tenant du tableau de bord membre pour donner la même lecture aux administrateurs.',
    checklistComplete: 'checklist complétée',
    nextRecommendedAction: 'Prochaine action administrateur recommandée',
    documentOperations: 'Opérations documentaires',
    ingestionHealth: 'Santé de l’ingestion',
    queued: 'En file',
    processing: 'En cours',
    failed: 'Échoué',
    retried: 'Relancé',
    latestFailure: 'Dernier échec',
    openDocumentOperations: 'Ouvrir les opérations documentaires',
    quickActions: 'Actions rapides',
    tenantScope: 'Périmètre du tenant',
    tenant: 'Tenant',
    enabledModules: 'Modules activés',
    openContributionBalance: 'Solde de cotisations ouvert',
    hubAdmin: 'Administration',
    hubPrincipal: 'Administration principale',
    titleAdmin: 'Vue d’ensemble admin',
    titlePrincipal: 'Vue d’ensemble administrateur principal',
    subtitleAdmin: 'Un écran unique pour la préparation du tenant, les signaux opérationnels et la prochaine action utile.',
    subtitlePrincipal: 'Un poste de pilotage à l’échelle du tenant pour les rôles, les réglages, les modules et les revues sensibles.',
    workspaceErrorTitle: "La vue d'ensemble admin est indisponible",
    na: 'n/d',
  }
})
const hubLabel = computed(() => (isPrincipalAdmin.value ? copy.value.hubPrincipal : copy.value.hubAdmin))
const overviewTitle = computed(() => (isPrincipalAdmin.value ? copy.value.titlePrincipal : copy.value.titleAdmin))
const overviewSubtitle = computed(() =>
  isPrincipalAdmin.value
    ? copy.value.subtitlePrincipal
    : copy.value.subtitleAdmin,
)
const {
  loading,
  error,
  isRecovering,
  modules,
  summaryMetrics,
  riskItems,
  quickActions,
  onboarding,
  ingestionHealth,
  contributionSummary,
  refresh,
  retryRefresh,
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
