import { computed, ref } from 'vue'
import { useTenantStore } from '@/stores/tenant.store'
import { listDocuments } from '@/api/documents.api'
import { listMembers } from '@/api/membership.api'
import { getContributionSummary } from '@/api/contributions.api'
import { listActiveAnnouncements } from '@/api/announcements.api'
import { listPublicEvents } from '@/api/events.api'
import { listAuditEvents } from '@/api/audit.api'
import { listNotificationChannels } from '@/api/notifications.api'
import { getIngestionJobsHealth, type IngestionJobHealthResponse } from '@/api/admin.api'
import { getTenantSettings, type RecoveryEvidenceResponse } from '@/api/settings.api'
import { useRecoveryState } from '@/composables/useRecoveryState'
import { useTenantOnboarding } from '@/composables/useTenantOnboarding'
import { useLocaleStore } from '@/stores/locale.store'

export interface AdminOverviewMetric {
  id: string
  label: string
  value: string
  hint: string
  tone: 'neutral' | 'success' | 'warning' | 'danger'
  to: string
}

export interface AdminRiskItem {
  id: string
  title: string
  description: string
  tone: 'warning' | 'danger' | 'success'
  to: string
  actionLabel: string
}

export interface AdminQuickAction {
  id: string
  label: string
  description: string
  to: string
}

export function useAdminOverview() {
  const localeStore = useLocaleStore()
  const tenantStore = useTenantStore()
  const onboarding = useTenantOnboarding()

  const { loading, error, isRecovering, run, retry, clearError } = useRecoveryState()
  const documentCount = ref(0)
  const memberCount = ref(0)
  const activeAnnouncementCount = ref(0)
  const upcomingEventCount = ref(0)
  const auditEventCount = ref(0)
  const configuredChannelCount = ref(0)
  const contributionSummary = ref<{
    total_count: number
    total_expected: string
    total_paid: string
    total_balance: string
  } | null>(null)
  const ingestionHealth = ref<IngestionJobHealthResponse | null>(null)
  const recoveryEvidence = ref<RecoveryEvidenceResponse | null>(null)
  const copy = computed(() => {
    if (localeStore.currentLocale === 'de') {
      return {
        documents: 'Dokumente',
        knowledgeBaseAssets: 'Wissensbasis-Bestände',
        failedIngestionJobs: (count: number) => `${count} fehlgeschlagene Ingestion-Aufträge`,
        auditEvents: 'Audit-Ereignisse',
        recentSensitiveActions: 'Letzte sensible Aktionen',
        members: 'Mitglieder',
        activeDirectorySize: 'Groesse des aktiven Verzeichnisses',
        openBalance: 'Offener Saldo',
        contributionRecords: (count: number) => `${count} Beitragsdatensaetze`,
        announcements: 'Ankuendigungen',
        activeNotices: 'Aktive Hinweise',
        upcomingEvents: 'Kommende Termine',
        scheduledTenantRhythm: 'Geplanter Tenant-Rhythmus',
        configuredChannels: 'Konfigurierte Kanaele',
        outboundDiagnostics: 'Optionale Ausgangsdiagnostik',
        recoveryEvidence: 'Wiederherstellungsnachweise',
        backupProofMissing: 'Backup- und Restore-Nachweise fehlen noch',
        unrecorded: 'nicht erfasst',
        knowledgeBaseEmpty: 'Wissensbasis ist leer',
        uploadFirstDocument: 'Laden Sie das erste vertrauenswürdige Dokument hoch, damit Chat und Retrieval nutzbar werden.',
        uploadDocuments: 'Dokumente hochladen',
        noMembers: 'Noch kein Mitgliederverzeichnis',
        addMembers: 'Fuegen Sie Mitglieder hinzu oder importieren Sie sie, damit der Tenant nicht leer wirkt.',
        openMembers: 'Mitglieder oeffnen',
        ingestionNeedsAttention: 'Dokumenten-Ingestion benötigt Aufmerksamkeit',
        failedIngestionDescription: (count: number) => `${count} Ingestion-Auftraege sind fehlgeschlagen. Fehler pruefen und bei Bedarf erneut ausfuehren.`,
        reviewDocuments: 'Dokumente pruefen',
        outstandingBalance: 'Offener Beitragsbestand',
        outstandingBalanceDescription: (amount: string) => `Ueber die aktuellen Beitragsdatensaetze sind noch ${amount} EUR offen.`,
        reviewContributions: 'Beitraege pruefen',
        updateEvidence: 'Nachweise aktualisieren',
        noImmediateWarnings: 'Keine unmittelbaren Betriebswarnungen',
        healthyTenant: 'Der Tenant hat die zentralen Startbausteine und es wurde kein dringendes Setup- oder Ingestion-Problem erkannt.',
        reviewAuditTrail: 'Audit-Protokoll pruefen',
        healthCenter: 'Health Center',
        healthCenterText: 'Abhaengigkeitsstatus und Wiederherstellungsnachweise pruefen',
        onboardingWizard: 'Onboarding-Assistent',
        onboardingWizardText: 'Die erste Einrichtung Schritt fuer Schritt durchgehen',
        tenantOperations: 'Tenant-Operationen',
        tenantOperationsText: 'Mitgliedschaften pruefen und Kontext explizit wechseln',
        tenantSettings: 'Tenant-Einstellungen',
        tenantSettingsText: 'Branding, Module und Konfiguration',
        documentsAction: 'Dokumente',
        documentsActionText: 'Uploads, Pruefungen und Wiederherstellung der Ingestion',
        access: 'Zugaenge',
        accessText: 'Kolleginnen und Kollegen einladen und Onboarding verfolgen',
        membersAction: 'Mitglieder',
        membersActionText: 'Mitgliederprofile importieren oder verwalten',
        announcementsAction: 'Ankuendigungen',
        announcementsActionText: 'Aktive Tenant-Kommunikation veroeffentlichen',
        eventsAction: 'Termine',
        eventsActionText: 'Kommende Meilensteine planen',
        channels: 'Kanaele',
        channelsText: 'Benachrichtigungsdiagnostik pruefen',
        loadError: 'Die Admin-Uebersicht konnte nicht geladen werden.',
      }
    }
    if (localeStore.currentLocale === 'en') {
      return {
        documents: 'Documents',
        knowledgeBaseAssets: 'Knowledge base assets',
        failedIngestionJobs: (count: number) => `${count} failed ingestion job(s)`,
        auditEvents: 'Audit events',
        recentSensitiveActions: 'Recent sensitive actions',
        members: 'Members',
        activeDirectorySize: 'Active directory size',
        openBalance: 'Open balance',
        contributionRecords: (count: number) => `${count} contribution record(s)`,
        announcements: 'Announcements',
        activeNotices: 'Currently active notices',
        upcomingEvents: 'Upcoming events',
        scheduledTenantRhythm: 'Scheduled tenant rhythm',
        configuredChannels: 'Configured channels',
        outboundDiagnostics: 'Optional outbound diagnostics',
        recoveryEvidence: 'Recovery evidence',
        backupProofMissing: 'Backup and restore proof not yet recorded',
        unrecorded: 'unrecorded',
        knowledgeBaseEmpty: 'Knowledge base is empty',
        uploadFirstDocument: 'Upload the first trusted document so chat and retrieval can become useful.',
        uploadDocuments: 'Upload documents',
        noMembers: 'No member directory yet',
        addMembers: 'Add or import members so the tenant stops feeling like a blank workspace.',
        openMembers: 'Open members',
        ingestionNeedsAttention: 'Document ingestion needs attention',
        failedIngestionDescription: (count: number) => `${count} ingestion job(s) failed. Review errors and retry where needed.`,
        reviewDocuments: 'Review documents',
        outstandingBalance: 'Outstanding contribution balance',
        outstandingBalanceDescription: (amount: string) => `There is still ${amount} EUR open across the current contribution records.`,
        reviewContributions: 'Review contributions',
        updateEvidence: 'Update evidence',
        noImmediateWarnings: 'No immediate operational warnings',
        healthyTenant: 'The tenant has the core launch ingredients and no urgent ingestion or setup issue was detected.',
        reviewAuditTrail: 'Review audit trail',
        healthCenter: 'Health center',
        healthCenterText: 'Review dependency status and recovery evidence',
        onboardingWizard: 'Onboarding wizard',
        onboardingWizardText: 'Walk through the first-run setup sequence',
        tenantOperations: 'Tenant operations',
        tenantOperationsText: 'Inspect memberships and switch context explicitly',
        tenantSettings: 'Tenant settings',
        tenantSettingsText: 'Branding, modules, and configuration',
        documentsAction: 'Documents',
        documentsActionText: 'Upload, inspect, and recover ingestion',
        access: 'Access',
        accessText: 'Invite teammates and monitor onboarding',
        membersAction: 'Members',
        membersActionText: 'Import or manage member profiles',
        announcementsAction: 'Announcements',
        announcementsActionText: 'Publish active tenant communications',
        eventsAction: 'Events',
        eventsActionText: 'Schedule upcoming milestones',
        channels: 'Channels',
        channelsText: 'Inspect notification diagnostics',
        loadError: 'Could not load the admin overview.',
      }
    }
    return {
      documents: 'Documents',
      knowledgeBaseAssets: 'Actifs de la base documentaire',
      failedIngestionJobs: (count: number) => `${count} tâche(s) d’ingestion en échec`,
      auditEvents: 'Événements d’audit',
      recentSensitiveActions: 'Actions sensibles récentes',
      members: 'Membres',
      activeDirectorySize: 'Taille de l’annuaire actif',
      openBalance: 'Solde ouvert',
      contributionRecords: (count: number) => `${count} enregistrement(s) de cotisation`,
      announcements: 'Annonces',
      activeNotices: 'Communications actuellement actives',
      upcomingEvents: 'Événements à venir',
      scheduledTenantRhythm: 'Rythme planifié du tenant',
      configuredChannels: 'Canaux configurés',
      outboundDiagnostics: 'Diagnostic sortant optionnel',
      recoveryEvidence: 'Preuves de reprise',
      backupProofMissing: 'Les preuves de sauvegarde et de restauration ne sont pas encore enregistrées',
      unrecorded: 'non enregistré',
      knowledgeBaseEmpty: 'La base documentaire est vide',
      uploadFirstDocument: 'Importez le premier document de confiance pour rendre le chat et la recherche utiles.',
      uploadDocuments: 'Importer des documents',
      noMembers: 'Aucun annuaire membre pour le moment',
      addMembers: 'Ajoutez ou importez des membres pour que le tenant ne ressemble plus à un espace vide.',
      openMembers: 'Ouvrir les membres',
      ingestionNeedsAttention: 'L’ingestion documentaire demande une attention',
      failedIngestionDescription: (count: number) => `${count} tâche(s) d’ingestion ont échoué. Vérifiez les erreurs et relancez si nécessaire.`,
      reviewDocuments: 'Vérifier les documents',
      outstandingBalance: 'Solde de cotisations en attente',
      outstandingBalanceDescription: (amount: string) => `Il reste encore ${amount} EUR ouverts sur les cotisations actuelles.`,
      reviewContributions: 'Vérifier les cotisations',
      updateEvidence: 'Mettre à jour les preuves',
      noImmediateWarnings: 'Aucune alerte opérationnelle immédiate',
      healthyTenant: 'Le tenant dispose des briques de lancement essentielles et aucun problème urgent de configuration ou d’ingestion n’a été détecté.',
      reviewAuditTrail: 'Vérifier la piste d’audit',
      healthCenter: 'Centre de santé',
      healthCenterText: 'Vérifier l’état des dépendances et les preuves de reprise',
      onboardingWizard: 'Assistant de démarrage',
      onboardingWizardText: 'Suivre la séquence de mise en route',
      tenantOperations: 'Opérations tenant',
      tenantOperationsText: 'Inspecter les appartenances et changer explicitement de contexte',
      tenantSettings: 'Réglages du tenant',
      tenantSettingsText: 'Identité visuelle, modules et configuration',
      documentsAction: 'Documents',
      documentsActionText: 'Importer, inspecter et relancer l’ingestion',
      access: 'Accès',
      accessText: 'Inviter des collègues et suivre l’onboarding',
      membersAction: 'Membres',
      membersActionText: 'Importer ou gérer les profils membres',
      announcementsAction: 'Annonces',
      announcementsActionText: 'Publier les communications actives du tenant',
      eventsAction: 'Événements',
      eventsActionText: 'Planifier les prochaines échéances',
      channels: 'Canaux',
      channelsText: 'Inspecter le diagnostic des notifications',
      loadError: 'Impossible de charger la vue d’ensemble admin.',
    }
  })

  const modules = computed(() => ({
    membership: tenantStore.isModuleEnabled('membership'),
    contributions: tenantStore.isModuleEnabled('contributions'),
    policies: tenantStore.isModuleEnabled('policies'),
    disciplinary: tenantStore.isModuleEnabled('disciplinary'),
    events: tenantStore.isModuleEnabled('events'),
    announcements: tenantStore.isModuleEnabled('announcements'),
    chat: tenantStore.isModuleEnabled('chat'),
    notifications: tenantStore.isModuleEnabled('notifications'),
  }))

  const summaryMetrics = computed<AdminOverviewMetric[]>(() => {
    const metrics: AdminOverviewMetric[] = [
      {
        id: 'documents',
        label: copy.value.documents,
        value: String(documentCount.value),
        hint: ingestionHealth.value?.failed_count
          ? copy.value.failedIngestionJobs(ingestionHealth.value.failed_count)
          : copy.value.knowledgeBaseAssets,
        tone: ingestionHealth.value?.failed_count ? 'warning' : 'neutral',
        to: '/admin/documents',
      },
      {
        id: 'audit',
        label: copy.value.auditEvents,
        value: String(auditEventCount.value),
        hint: copy.value.recentSensitiveActions,
        tone: 'neutral',
        to: '/admin/audit',
      },
    ]

    if (modules.value.membership) {
      metrics.push({
        id: 'members',
        label: copy.value.members,
        value: String(memberCount.value),
        hint: copy.value.activeDirectorySize,
        tone: memberCount.value === 0 ? 'warning' : 'neutral',
        to: '/admin/members',
      })
    }

    if (modules.value.contributions && contributionSummary.value) {
      const balance = Number(contributionSummary.value.total_balance)
      metrics.push({
        id: 'contributions',
        label: copy.value.openBalance,
        value: `${contributionSummary.value.total_balance} EUR`,
        hint: copy.value.contributionRecords(contributionSummary.value.total_count),
        tone: balance > 0 ? 'warning' : 'success',
        to: '/admin/contributions',
      })
    }

    if (modules.value.announcements) {
      metrics.push({
        id: 'announcements',
        label: copy.value.announcements,
        value: String(activeAnnouncementCount.value),
        hint: copy.value.activeNotices,
        tone: activeAnnouncementCount.value === 0 ? 'warning' : 'neutral',
        to: '/admin/announcements',
      })
    }

    if (modules.value.events) {
      metrics.push({
        id: 'events',
        label: copy.value.upcomingEvents,
        value: String(upcomingEventCount.value),
        hint: copy.value.scheduledTenantRhythm,
        tone: upcomingEventCount.value === 0 ? 'warning' : 'neutral',
        to: '/admin/events',
      })
    }

    if (modules.value.notifications) {
      metrics.push({
        id: 'channels',
        label: copy.value.configuredChannels,
        value: String(configuredChannelCount.value),
        hint: copy.value.outboundDiagnostics,
        tone: configuredChannelCount.value === 0 ? 'warning' : 'neutral',
        to: '/admin/notifications',
      })
    }

    if (recoveryEvidence.value) {
      metrics.push({
        id: 'recovery',
        label: copy.value.recoveryEvidence,
        value: recoveryEvidence.value.overall_status,
        hint: recoveryEvidence.value.status_message,
        tone:
          recoveryEvidence.value.overall_status === 'healthy'
            ? 'success'
            : recoveryEvidence.value.overall_status === 'warning'
              ? 'warning'
              : 'danger',
        to: '/admin/settings',
      })
    } else {
      metrics.push({
        id: 'recovery',
        label: copy.value.recoveryEvidence,
        value: copy.value.unrecorded,
        hint: copy.value.backupProofMissing,
        tone: 'warning',
        to: '/admin/settings',
      })
    }

    return metrics
  })

  const riskItems = computed<AdminRiskItem[]>(() => {
    const risks: AdminRiskItem[] = []

    if (documentCount.value === 0) {
      risks.push({
        id: 'no-documents',
        title: copy.value.knowledgeBaseEmpty,
        description: copy.value.uploadFirstDocument,
        tone: 'warning',
        to: '/admin/documents',
        actionLabel: copy.value.uploadDocuments,
      })
    }

    if (modules.value.membership && memberCount.value === 0) {
      risks.push({
        id: 'no-members',
        title: copy.value.noMembers,
        description: copy.value.addMembers,
        tone: 'warning',
        to: '/admin/members',
        actionLabel: copy.value.openMembers,
      })
    }

    if ((ingestionHealth.value?.failed_count ?? 0) > 0) {
      risks.push({
        id: 'failed-ingestion',
        title: copy.value.ingestionNeedsAttention,
        description: copy.value.failedIngestionDescription(ingestionHealth.value?.failed_count ?? 0),
        tone: 'danger',
        to: '/admin/documents',
        actionLabel: copy.value.reviewDocuments,
      })
    }

    if (modules.value.contributions && contributionSummary.value && Number(contributionSummary.value.total_balance) > 0) {
      risks.push({
        id: 'open-balance',
        title: copy.value.outstandingBalance,
        description: copy.value.outstandingBalanceDescription(contributionSummary.value.total_balance),
        tone: 'warning',
        to: '/admin/contributions',
        actionLabel: copy.value.reviewContributions,
      })
    }

    if (recoveryEvidence.value && recoveryEvidence.value.overall_status !== 'healthy') {
      risks.push({
        id: 'recovery-evidence',
        title: 'Recovery evidence needs refresh',
        description: recoveryEvidence.value.status_message,
        tone: recoveryEvidence.value.overall_status === 'critical' ? 'danger' : 'warning',
        to: '/admin/settings',
        actionLabel: copy.value.updateEvidence,
      })
    }

    if (risks.length === 0) {
      risks.push({
        id: 'healthy',
        title: copy.value.noImmediateWarnings,
        description: copy.value.healthyTenant,
        tone: 'success',
        to: '/admin/audit',
        actionLabel: copy.value.reviewAuditTrail,
      })
    }

    return risks
  })

  const quickActions = computed<AdminQuickAction[]>(() => {
    const actions: AdminQuickAction[] = [
      {
        id: 'health-center',
        label: copy.value.healthCenter,
        description: copy.value.healthCenterText,
        to: '/admin/health',
      },
      {
        id: 'onboarding-wizard',
        label: copy.value.onboardingWizard,
        description: copy.value.onboardingWizardText,
        to: '/admin/onboarding',
      },
      {
        id: 'tenant-operations',
        label: copy.value.tenantOperations,
        description: copy.value.tenantOperationsText,
        to: '/admin/tenants',
      },
      {
        id: 'settings',
        label: copy.value.tenantSettings,
        description: copy.value.tenantSettingsText,
        to: '/admin/settings',
      },
      {
        id: 'documents',
        label: copy.value.documentsAction,
        description: copy.value.documentsActionText,
        to: '/admin/documents',
      },
      {
        id: 'access',
        label: copy.value.access,
        description: copy.value.accessText,
        to: '/admin/access',
      },
      {
        id: 'audit',
        label: copy.value.auditEvents,
        description: copy.value.recentSensitiveActions,
        to: '/admin/audit',
      },
    ]

    if (modules.value.membership) {
      actions.push({
        id: 'members',
        label: copy.value.membersAction,
        description: copy.value.membersActionText,
        to: '/admin/members',
      })
    }

    if (modules.value.announcements) {
      actions.push({
        id: 'announcements',
        label: copy.value.announcementsAction,
        description: copy.value.announcementsActionText,
        to: '/admin/announcements',
      })
    }

    if (modules.value.events) {
      actions.push({
        id: 'events',
        label: copy.value.eventsAction,
        description: copy.value.eventsActionText,
        to: '/admin/events',
      })
    }

    if (modules.value.notifications) {
      actions.push({
        id: 'channels',
        label: copy.value.channels,
        description: copy.value.channelsText,
        to: '/admin/notifications',
      })
    }

    return actions
  })

  async function refresh() {
    clearError()
    await run(loadOverview)
  }

  async function retryRefresh() {
    await retry(loadOverview)
  }

  async function loadOverview() {
      await onboarding.refresh()
      const tenantId = tenantStore.currentTenant?.tenant_id

      const work: Promise<unknown>[] = [
        listDocuments().then((docs) => {
          documentCount.value = docs.length
        }),
        listAuditEvents({ limit: 20 }).then((events) => {
          auditEventCount.value = events.length
        }),
        getIngestionJobsHealth().then((health) => {
          ingestionHealth.value = health
        }),
      ]

      if (modules.value.membership) {
        work.push(
          listMembers().then((members) => {
            memberCount.value = members.length
          })
        )
      } else {
        memberCount.value = 0
      }

      if (modules.value.contributions) {
        work.push(
          getContributionSummary().then((summary) => {
            contributionSummary.value = summary
          })
        )
      } else {
        contributionSummary.value = null
      }

      if (modules.value.announcements) {
        work.push(
          listActiveAnnouncements().then((items) => {
            activeAnnouncementCount.value = items.length
          })
        )
      } else {
        activeAnnouncementCount.value = 0
      }

      if (modules.value.events) {
        work.push(
          listPublicEvents().then((items) => {
            upcomingEventCount.value = items.length
          })
        )
      } else {
        upcomingEventCount.value = 0
      }

      if (modules.value.notifications) {
        work.push(
          listNotificationChannels().then((channels) => {
            configuredChannelCount.value = channels.filter((item) => item.configured).length
          })
        )
      } else {
        configuredChannelCount.value = 0
      }

      if (tenantId) {
        work.push(
          getTenantSettings(tenantId).then((settings) => {
            recoveryEvidence.value = settings.operations
          }),
        )
      } else {
        recoveryEvidence.value = null
      }

      await Promise.all(work)
  }

  return {
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
    recoveryEvidence,
    refresh,
    retryRefresh,
  }
}
