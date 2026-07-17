<template>
  <div class="p-4 p-lg-5">
    <div class="d-flex flex-column flex-xl-row justify-content-between gap-3 mb-4">
      <div>
        <div class="text-uppercase small fw-semibold text-secondary mb-2">
          {{ copy.kicker }}
        </div>
        <h1 class="h4 fw-bold mb-1">{{ copy.title }}</h1>
        <p class="text-muted mb-0">
          {{ copy.lead }}
        </p>
      </div>
      <div class="d-flex flex-wrap align-items-start gap-2">
        <RouterLink to="/admin" class="btn btn-outline-secondary">
          <i class="bi bi-arrow-left me-1"></i>{{ copy.backToOverview }}
        </RouterLink>
        <RouterLink to="/admin/settings" class="btn btn-outline-secondary">
          <i class="bi bi-gear me-1"></i>{{ copy.tenantSettings }}
        </RouterLink>
        <button class="btn om-primary-btn" type="button" @click="refresh" :disabled="loading || isRecovering">
          {{ loading ? copy.refreshing : copy.refreshHealth }}
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
        <button class="btn btn-outline-secondary btn-sm align-self-start" type="button" @click="retryRefresh" :disabled="isRecovering">
          <span v-if="isRecovering" class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
          {{ isRecovering ? localeStore.t('common.loading') : localeStore.t('common.retry') }}
        </button>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-xl-8">
        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-3">
              <div>
                <div class="text-uppercase small fw-semibold text-secondary mb-2">
                  {{ copy.liveDependencyHealth }}
                </div>
                <h2 class="h6 fw-bold mb-1">{{ copy.systemStatus }}</h2>
                <p class="text-muted small mb-0">
                  {{ copy.systemStatusText }}
                </p>
              </div>
              <span class="badge text-capitalize align-self-start" :class="statusBadgeClass(systemHealth?.status)">
                {{ formatStatus(systemHealth?.status) }}
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
                    <th scope="col">{{ copy.service }}</th>
                    <th scope="col">{{ copy.status }}</th>
                    <th scope="col">{{ copy.latency }}</th>
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
                  {{ copy.recoveryEvidence }}
                </div>
                <h2 class="h6 fw-bold mb-1">{{ copy.recoveryTitle }}</h2>
                <p class="text-muted small mb-0">
                  {{ copy.recoveryLead }}
                </p>
              </div>
              <span class="badge text-capitalize align-self-start" :class="recoveryBadgeClass(recoveryStatus)">
                {{ formatStatus(recoveryStatus) }}
              </span>
            </div>

            <div class="row g-3">
              <div class="col-md-6">
                <div class="mini-stat h-100">
                  <div class="small text-muted">{{ copy.lastBackup }}</div>
                  <div class="fw-semibold">{{ formatDate(recovery?.last_backup_at) }}</div>
                  <div class="small text-muted">{{ recovery?.last_backup_reference || copy.noBackupReference }}</div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="mini-stat h-100">
                  <div class="small text-muted">{{ copy.restoreDrill }}</div>
                  <div class="fw-semibold">{{ formatDate(recovery?.last_restore_drill_at) }}</div>
                  <div class="small text-muted text-capitalize">
                    {{ formatStatus(recovery?.last_restore_drill_status) }}
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="mini-stat h-100">
                  <div class="small text-muted">{{ copy.alertPosture }}</div>
                  <div class="fw-semibold text-capitalize">{{ formatStatus(recovery?.alert_posture) }}</div>
                  <div class="small text-muted">
                    {{ recovery?.alert_contacts_configured ? copy.alertContactsConfigured : copy.alertContactsMissing }}
                  </div>
                </div>
              </div>
              <div class="col-md-6">
                <div class="mini-stat h-100">
                  <div class="small text-muted">{{ copy.freshnessWarnings }}</div>
                  <div class="fw-semibold" data-testid="health-center-warning-count">{{ freshnessWarnings.length }}</div>
                  <div class="small text-muted">{{ copy.freshnessWarningsHint }}</div>
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
              {{ copy.incidentAnnotations }}
            </div>
            <h2 class="h6 fw-bold mb-3">{{ copy.currentNote }}</h2>
            <p class="text-muted small mb-3">
              {{ recovery?.notes || copy.noIncidentNote }}
            </p>
            <RouterLink to="/admin/settings" class="btn btn-outline-secondary btn-sm w-100">
              {{ copy.updateRecoveryNote }}
            </RouterLink>
          </div>
        </div>

        <div class="card shadow-sm border-0 mb-4">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              {{ copy.operationalSnapshot }}
            </div>
            <div class="vstack gap-2 small">
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">{{ copy.tenant }}</span>
                <span class="fw-semibold text-end">{{ tenantStore.currentTenantName }}</span>
              </div>
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">{{ copy.environment }}</span>
                <span class="fw-semibold text-end text-capitalize">{{ systemHealth?.env || copy.unknown }}</span>
              </div>
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">{{ copy.version }}</span>
                <span class="fw-semibold text-end">{{ systemHealth?.version || copy.unknown }}</span>
              </div>
              <div class="d-flex justify-content-between gap-3">
                <span class="text-muted">{{ copy.modulesReported }}</span>
                <span class="fw-semibold text-end">{{ systemHealth?.modules.length || 0 }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="card shadow-sm border-0">
          <div class="card-body p-4">
            <div class="text-uppercase small fw-semibold text-secondary mb-2">
              {{ copy.fastPaths }}
            </div>
            <div class="vstack gap-2">
              <RouterLink to="/admin/settings" class="quick-action">
                <div class="fw-semibold">{{ copy.reviewTenantSettings }}</div>
                <div class="small text-muted">{{ copy.reviewTenantSettingsText }}</div>
              </RouterLink>
              <RouterLink to="/admin/tenants" class="quick-action">
                <div class="fw-semibold">{{ copy.tenantOperations }}</div>
                <div class="small text-muted">{{ copy.tenantOperationsText }}</div>
              </RouterLink>
              <RouterLink to="/admin/audit" class="quick-action">
                <div class="fw-semibold">{{ copy.auditTrail }}</div>
                <div class="small text-muted">{{ copy.auditTrailText }}</div>
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
import { useRecoveryState } from '@/composables/useRecoveryState'
import { useLocaleStore } from '@/stores/locale.store'
import { useTenantStore } from '@/stores/tenant.store'

type ServiceRow = {
  name: string
  label: string
  status: string
  latency: string
  badgeClass: string
}

const localeStore = useLocaleStore()
const tenantStore = useTenantStore()
const { loading, error, isRecovering, run, retry, clearError } = useRecoveryState()
const systemHealth = ref<SystemHealthResponse | null>(null)
const recovery = ref<RecoveryEvidenceResponse | null>(null)

const copy = computed(() => {
  if (localeStore.currentLocale === 'de') {
    return {
      kicker: 'Betriebszustand',
      title: 'Wiederherstellungsnachweise und Abhängigkeitsstatus',
      lead: 'Prüfen Sie Wiederherstellungsstatus, Dienstzustand und Vorfallhinweise, ohne den aktiven Tenant zu verlassen.',
      backToOverview: 'Zur Übersicht',
      tenantSettings: 'Tenant-Einstellungen',
      refreshing: 'Aktualisierung...',
      refreshHealth: 'Status aktualisieren',
      liveDependencyHealth: 'Live-Abhängigkeitsstatus',
      systemStatus: 'Systemstatus',
      systemStatusText: 'Die Backend-Prüfung ist schreibgeschützt und zeigt den aktuellen Dienstzustand des aktiven Tenants.',
      service: 'Dienst',
      status: 'Status',
      latency: 'Latenz',
      recoveryEvidence: 'Wiederherstellungsnachweise',
      recoveryTitle: 'Backup-, Restore- und Alarmstatus',
      recoveryLead: 'Warnhinweise zur Aktualität bleiben sichtbar, damit fehlende Nachweise sofort auffallen.',
      lastBackup: 'Letztes Backup',
      noBackupReference: 'Kein Backup-Verweis hinterlegt',
      restoreDrill: 'Restore-Test',
      alertPosture: 'Alarmstatus',
      alertContactsConfigured: 'Alarmkontakte konfiguriert',
      alertContactsMissing: 'Alarmkontakte fehlen',
      freshnessWarnings: 'Aktualitätswarnungen',
      freshnessWarningsHint: 'Veraltete oder fehlende Signale mit Handlungsbedarf',
      incidentAnnotations: 'Vorfallhinweise',
      currentNote: 'Aktuelle Notiz',
      noIncidentNote: 'Noch kein Vorfallhinweis erfasst.',
      updateRecoveryNote: 'Wiederherstellungsnotiz aktualisieren',
      operationalSnapshot: 'Betriebssnapshot',
      tenant: 'Tenant',
      environment: 'Umgebung',
      version: 'Version',
      modulesReported: 'Gemeldete Module',
      fastPaths: 'Schnellzugriffe',
      reviewTenantSettings: 'Tenant-Einstellungen prüfen',
      reviewTenantSettingsText: 'Wiederherstellungsnachweise und Hinweise einsehen.',
      tenantOperations: 'Tenant-Operationen',
      tenantOperationsText: 'Tenant-Kontext explizit wechseln.',
      auditTrail: 'Audit-Protokoll',
      auditTrailText: 'Sensible Betriebsaktionen prüfen.',
      unknown: 'unbekannt',
      statusLabels: {
        unknown: 'unbekannt',
        healthy: 'stabil',
        warning: 'warnung',
        critical: 'kritisch',
        completed: 'abgeschlossen',
        failed: 'fehlgeschlagen',
        passed: 'bestanden',
        ok: 'ok',
        degraded: 'beeinträchtigt',
        unavailable: 'nicht verfügbar',
        error: 'fehler',
      },
      warningRecoveryNotLoaded: 'Wiederherstellungsnachweise wurden noch nicht geladen.',
      warningBackupStale: 'Backup-Nachweise sind veraltet und sollten aktualisiert werden.',
      warningRestoreStale: 'Restore-Test-Nachweise sind veraltet und sollten aktualisiert werden.',
      warningAlertNeedsAttention: 'Alarmkontakte oder Alarmstatus benötigen Aufmerksamkeit.',
      summaryOverallStatus: 'Gesamtstatus',
      summaryFreshnessWarnings: 'Aktualitätswarnungen',
      summaryFreshnessWarningsHint: 'Veraltete Signale bleiben in diesem Bereich sichtbar',
      summaryReportedModules: 'Gemeldete Module',
      summaryReportedModulesHint: 'Vom Health-Probe gemeldete Backend-Module',
      summaryWaitingRecovery: 'Warte auf aktuelle Wiederherstellungsnachweise',
      notRecorded: 'Nicht erfasst',
      loadError: 'Health Center konnte nicht geladen werden',
      workspaceErrorTitle: 'Health Center nicht verfügbar',
    }
  }
  if (localeStore.currentLocale === 'en') {
    return {
      kicker: 'Operator health center',
      title: 'Recovery evidence and dependency health',
      lead: 'Review the current recovery posture, dependency status, and incident annotations without leaving the active tenant.',
      backToOverview: 'Back to overview',
      tenantSettings: 'Tenant settings',
      refreshing: 'Refreshing...',
      refreshHealth: 'Refresh health',
      liveDependencyHealth: 'Live dependency health',
      systemStatus: 'System status',
      systemStatusText: 'The backend health probe is read-only and shows the current service posture for the active tenant.',
      service: 'Service',
      status: 'Status',
      latency: 'Latency',
      recoveryEvidence: 'Recovery evidence',
      recoveryTitle: 'Backup, restore, and alert posture',
      recoveryLead: 'Freshness warnings stay visible so operators can see at a glance when evidence needs a refresh.',
      lastBackup: 'Last backup',
      noBackupReference: 'No backup reference recorded',
      restoreDrill: 'Restore drill',
      alertPosture: 'Alert posture',
      alertContactsConfigured: 'Alert contacts configured',
      alertContactsMissing: 'Alert contacts missing',
      freshnessWarnings: 'Freshness warnings',
      freshnessWarningsHint: 'Stale or missing signals that deserve attention',
      incidentAnnotations: 'Incident annotations',
      currentNote: 'Current note',
      noIncidentNote: 'No incident annotation recorded yet.',
      updateRecoveryNote: 'Update recovery note',
      operationalSnapshot: 'Operational snapshot',
      tenant: 'Tenant',
      environment: 'Environment',
      version: 'Version',
      modulesReported: 'Modules reported',
      fastPaths: 'Fast paths',
      reviewTenantSettings: 'Review tenant settings',
      reviewTenantSettingsText: 'Inspect recovery evidence and notes.',
      tenantOperations: 'Tenant operations',
      tenantOperationsText: 'Switch tenant context explicitly.',
      auditTrail: 'Audit trail',
      auditTrailText: 'Review sensitive operational actions.',
      unknown: 'unknown',
      statusLabels: {
        unknown: 'unknown',
        healthy: 'healthy',
        warning: 'warning',
        critical: 'critical',
        completed: 'completed',
        failed: 'failed',
        passed: 'passed',
        ok: 'ok',
        degraded: 'degraded',
        unavailable: 'unavailable',
        error: 'error',
      },
      warningRecoveryNotLoaded: 'Recovery evidence has not been loaded yet.',
      warningBackupStale: 'Backup evidence is stale and should be refreshed.',
      warningRestoreStale: 'Restore drill evidence is stale and should be refreshed.',
      warningAlertNeedsAttention: 'Alert contacts or alert posture need attention.',
      summaryOverallStatus: 'Overall status',
      summaryFreshnessWarnings: 'Freshness warnings',
      summaryFreshnessWarningsHint: 'Stale signals stay visible in this panel',
      summaryReportedModules: 'Reported modules',
      summaryReportedModulesHint: 'Backend modules exposed by the health probe',
      summaryWaitingRecovery: 'Waiting for the latest recovery evidence',
      notRecorded: 'Not recorded',
      loadError: 'Failed to load health center',
      workspaceErrorTitle: 'Health center unavailable',
    }
  }
  return {
    kicker: 'Centre de santé opérationnel',
    title: 'Preuves de reprise et état des dépendances',
    lead: 'Consultez l’état de reprise, la santé des dépendances et les annotations d’incident sans quitter le tenant actif.',
    backToOverview: 'Retour à la vue d’ensemble',
    tenantSettings: 'Réglages du tenant',
    refreshing: 'Actualisation...',
    refreshHealth: 'Actualiser la santé',
    liveDependencyHealth: 'Santé des dépendances en direct',
    systemStatus: 'État du système',
    systemStatusText: 'La sonde backend est en lecture seule et affiche l’état actuel des services pour le tenant actif.',
    service: 'Service',
    status: 'Statut',
    latency: 'Latence',
    recoveryEvidence: 'Preuves de reprise',
    recoveryTitle: 'Sauvegarde, restauration et posture d’alerte',
    recoveryLead: 'Les alertes de fraîcheur restent visibles pour repérer immédiatement les preuves à remettre à jour.',
    lastBackup: 'Dernière sauvegarde',
    noBackupReference: 'Aucune référence de sauvegarde enregistrée',
    restoreDrill: 'Exercice de restauration',
    alertPosture: 'Posture d’alerte',
    alertContactsConfigured: 'Contacts d’alerte configurés',
    alertContactsMissing: 'Contacts d’alerte manquants',
    freshnessWarnings: 'Alertes de fraîcheur',
    freshnessWarningsHint: 'Signaux obsolètes ou manquants à surveiller',
    incidentAnnotations: 'Annotations d’incident',
    currentNote: 'Note actuelle',
    noIncidentNote: 'Aucune annotation d’incident enregistrée pour le moment.',
    updateRecoveryNote: 'Mettre à jour la note de reprise',
    operationalSnapshot: 'Instantané opérationnel',
    tenant: 'Tenant',
    environment: 'Environnement',
    version: 'Version',
    modulesReported: 'Modules remontés',
    fastPaths: 'Accès rapides',
    reviewTenantSettings: 'Vérifier les réglages du tenant',
    reviewTenantSettingsText: 'Consulter les preuves de reprise et les notes.',
    tenantOperations: 'Opérations tenant',
    tenantOperationsText: 'Changer explicitement de contexte tenant.',
    auditTrail: 'Piste d’audit',
    auditTrailText: 'Examiner les actions opérationnelles sensibles.',
    unknown: 'inconnu',
    statusLabels: {
      unknown: 'inconnu',
      healthy: 'sain',
      warning: 'avertissement',
      critical: 'critique',
      completed: 'terminé',
      failed: 'échoué',
      passed: 'réussi',
      ok: 'ok',
      degraded: 'dégradé',
      unavailable: 'indisponible',
      error: 'erreur',
    },
    warningRecoveryNotLoaded: 'Les preuves de reprise ne sont pas encore chargées.',
    warningBackupStale: 'Les preuves de sauvegarde sont obsolètes et doivent être actualisées.',
    warningRestoreStale: 'Les preuves d’exercice de restauration sont obsolètes et doivent être actualisées.',
    warningAlertNeedsAttention: 'Les contacts d’alerte ou la posture d’alerte demandent une attention particulière.',
    summaryOverallStatus: 'Statut global',
    summaryFreshnessWarnings: 'Alertes de fraîcheur',
    summaryFreshnessWarningsHint: 'Les signaux obsolètes restent visibles dans ce panneau',
    summaryReportedModules: 'Modules remontés',
    summaryReportedModulesHint: 'Modules backend exposés par la sonde de santé',
    summaryWaitingRecovery: 'En attente des dernières preuves de reprise',
    notRecorded: 'Non enregistré',
    loadError: 'Impossible de charger le centre de santé',
    workspaceErrorTitle: 'Le centre de santé est indisponible',
  }
})

const recoveryStatus = computed(() => recovery.value?.overall_status || 'unknown')

const freshnessWarnings = computed(() => {
  const warnings: string[] = []
  if (!recovery.value) {
    warnings.push(copy.value.warningRecoveryNotLoaded)
    return warnings
  }

  if (recovery.value.backup_is_stale) {
    warnings.push(copy.value.warningBackupStale)
  }
  if (recovery.value.restore_drill_is_stale) {
    warnings.push(copy.value.warningRestoreStale)
  }
  if (!recovery.value.alert_is_healthy) {
    warnings.push(copy.value.warningAlertNeedsAttention)
  }
  return warnings
})

const summaryCards = computed(() => [
  {
    label: copy.value.summaryOverallStatus,
    value: formatStatus(systemHealth.value?.status),
    hint: recovery.value?.status_message || copy.value.summaryWaitingRecovery,
  },
  {
    label: copy.value.summaryFreshnessWarnings,
    value: String(freshnessWarnings.value.length),
    hint: copy.value.summaryFreshnessWarningsHint,
  },
  {
    label: copy.value.summaryReportedModules,
    value: String(systemHealth.value?.modules.length || 0),
    hint: copy.value.summaryReportedModulesHint,
  },
])

const serviceRows = computed<ServiceRow[]>(() => {
  const checks = systemHealth.value?.checks || {}
  const labels: Record<string, string> = {
    database: 'Database',
    redis: 'Redis cache',
    minio: 'Object storage',
    qdrant: 'Vector store',
    llm_provider: 'LLM provider',
    embedding_provider: 'Embedding provider',
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

function formatStatus(value?: string | null) {
  if (!value) return copy.value.unknown
  return copy.value.statusLabels[value as keyof typeof copy.value.statusLabels] || value
}

function formatDate(value?: string | null) {
  if (!value) return copy.value.notRecorded
  return new Date(value).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

async function loadHealthCenter() {
  const tenantId = tenantStore.currentTenant?.tenant_id
  if (!tenantId) {
    throw new Error(copy.value.loadError)
  }

  const [health, settings] = await Promise.all([
    getSystemHealth(),
    getTenantSettings(tenantId),
  ])
  systemHealth.value = health
  recovery.value = settings.operations
}

async function refresh() {
  clearError()
  await run(loadHealthCenter)
}

async function retryRefresh() {
  await retry(loadHealthCenter)
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
