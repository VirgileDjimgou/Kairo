import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { useTenantStore } from '@/stores/tenant.store'
import { useLocaleStore } from '@/stores/locale.store'
import { listActiveAnnouncements } from '@/api/announcements.api'
import { listPublicEvents } from '@/api/events.api'
import { listDocuments } from '@/api/documents.api'
import { listMembers } from '@/api/membership.api'
import { useRecoveryState } from '@/composables/useRecoveryState'

export interface OnboardingStep {
  id: string
  title: string
  description: string
  completed: boolean
  actionLabel: string
  to: string
  adminOnly?: boolean
}

export interface OnboardingSummaryMetric {
  label: string
  value: string
  hint: string
}

export function useTenantOnboarding() {
  const authStore = useAuthStore()
  const tenantStore = useTenantStore()
  const localeStore = useLocaleStore()

  const { loading, error, isRecovering, run, retry, clearError } = useRecoveryState()
  const documentCount = ref<number | null>(null)
  const memberCount = ref<number | null>(null)
  const eventCount = ref<number | null>(null)
  const announcementCount = ref<number | null>(null)
  const lastRefreshedAt = ref<string | null>(null)

  const isAdmin = computed(() => authStore.user?.roles.includes('admin') ?? false)
  const isPrincipalAdmin = computed(() => authStore.user?.roles.includes('principal_admin') ?? false)
  const isTreasurer = computed(() => authStore.user?.roles.includes('treasurer') ?? false)
  const isSetupMode = computed(() => {
    const docs = documentCount.value ?? 0
    const members = memberCount.value ?? 0
    return docs === 0 && (!isAdmin.value || members === 0)
  })

  const hasCustomBranding = computed(() => {
    const branding = tenantStore.currentTenant?.branding
    if (!branding) return false

    return Boolean(branding.logo_url?.trim()) || branding.primary_color !== '#1f4f8f'
  })

  const checklist = computed<OnboardingStep[]>(() => {
    const steps: OnboardingStep[] = [
      {
        id: 'branding',
        title: localeStore.currentLocale === 'de' ? 'Tenant-Branding bestätigen' : localeStore.currentLocale === 'en' ? 'Confirm tenant branding' : 'Confirmer le branding du tenant',
        description:
          localeStore.currentLocale === 'de' ? 'Prüfen Sie Organisationsname, Hauptfarbe und Logo in den Tenant-Einstellungen.' : localeStore.currentLocale === 'en' ? 'Review the organization name, primary color, and logo in tenant settings so the shell feels ready for customers.' : "Vérifiez le nom de l'organisation, la couleur principale et le logo dans les réglages du tenant.",
        completed: hasCustomBranding.value,
        actionLabel: localeStore.currentLocale === 'de' ? 'Tenant-Einstellungen öffnen' : localeStore.currentLocale === 'en' ? 'Open tenant settings' : 'Ouvrir les réglages du tenant',
        to: '/admin/settings',
        adminOnly: true,
      },
      {
        id: 'documents',
        title: localeStore.currentLocale === 'de' ? 'Premier document importieren' : localeStore.currentLocale === 'en' ? 'Upload the first document' : 'Importer le premier document',
        description:
          documentCount.value && documentCount.value > 0
            ? (localeStore.currentLocale === 'de' ? `Es gibt bereits ${documentCount.value} Dokument(e). Erweitern Sie die Wissensbasis weiter.` : localeStore.currentLocale === 'en' ? `You already have ${documentCount.value} document${documentCount.value > 1 ? 's' : ''}. Keep building the knowledge base.` : `Vous avez déjà ${documentCount.value} document(s). Continuez à enrichir la base documentaire.`)
            : (localeStore.currentLocale === 'de' ? 'Starten Sie mit einer Regel, einer Begruessungsnotiz oder einem verlaesslichen Betriebsdokument.' : localeStore.currentLocale === 'en' ? 'Start with a policy, welcome note, or operational document that the team can trust.' : 'Commencez par un règlement, une note de bienvenue ou un document opérationnel fiable.'),
        completed: (documentCount.value ?? 0) > 0,
        actionLabel:
          (documentCount.value ?? 0) > 0 ? (localeStore.currentLocale === 'de' ? 'Dokumente prüfen' : localeStore.currentLocale === 'en' ? 'Review documents' : 'Consulter les documents') : (localeStore.currentLocale === 'de' ? 'Erstes Dokument importieren' : localeStore.currentLocale === 'en' ? 'Upload first document' : 'Importer le premier document'),
        to: '/admin/documents',
        adminOnly: true,
      },
    ]

    if (tenantStore.isModuleEnabled('membership') && tenantStore.isModuleEnabled('contributions') && (isAdmin.value || isTreasurer.value)) {
      steps.push({
        id: 'finance',
        title: localeStore.currentLocale === 'de' ? 'Finanzbereich prüfen' : localeStore.currentLocale === 'en' ? 'Review the finance workspace' : "Consulter l'espace finances",
        description:
          localeStore.currentLocale === 'de' ? 'Prüfen Sie Mitgliedersalden, Beiträge und Zahlungen im Finanzbereich.' : localeStore.currentLocale === 'en' ? 'Check member balances, create contribution records, and record incoming payments from the dedicated finance surface.' : "Consultez les soldes membres, créez les cotisations et enregistrez les paiements depuis l'espace finances.",
        completed: (memberCount.value ?? 0) > 0,
        actionLabel: localeStore.currentLocale === 'de' ? 'Finanzbereich öffnen' : localeStore.currentLocale === 'en' ? 'Open finance workspace' : "Ouvrir l'espace finances",
        to: '/finance',
      })
    }

    if (tenantStore.isModuleEnabled('membership')) {
      steps.push({
        id: 'members',
        title: localeStore.currentLocale === 'de' ? 'Mitglieder hinzufügen oder importieren' : localeStore.currentLocale === 'en' ? 'Add or import members' : 'Ajouter ou importer des membres',
        description:
          memberCount.value && memberCount.value > 0
            ? (localeStore.currentLocale === 'de' ? `Es gibt ${memberCount.value} Mitgliederprofile in diesem Tenant.` : localeStore.currentLocale === 'en' ? `There are ${memberCount.value} member profile${memberCount.value > 1 ? 's' : ''} in this tenant.` : `Il y a ${memberCount.value} profil(s) membre dans ce tenant.`)
            : (localeStore.currentLocale === 'de' ? 'Importieren Sie ein CSV oder fügen Sie das erste Mitglied hinzu.' : localeStore.currentLocale === 'en' ? 'Import a CSV or add the first member profile so the tenant has a real working directory.' : 'Importez un CSV ou ajoutez le premier profil membre.'),
        completed: (memberCount.value ?? 0) > 0,
        actionLabel: (memberCount.value ?? 0) > 0 ? (localeStore.currentLocale === 'de' ? 'Mitglieder verwalten' : localeStore.currentLocale === 'en' ? 'Manage members' : 'Gérer les membres') : (localeStore.currentLocale === 'de' ? 'Mitglieder öffnen' : localeStore.currentLocale === 'en' ? 'Open members' : 'Ouvrir les membres'),
        to: '/admin/members',
        adminOnly: true,
      })
    }

    if (tenantStore.isModuleEnabled('announcements')) {
      steps.push({
        id: 'announcements',
        title: localeStore.currentLocale === 'de' ? 'Erste Ankuendigung veroeffentlichen' : localeStore.currentLocale === 'en' ? 'Publish a first announcement' : 'Publier une première annonce',
        description:
          announcementCount.value && announcementCount.value > 0
            ? (localeStore.currentLocale === 'de' ? `Es gibt ${announcementCount.value} aktive Ankuendigung(en).` : localeStore.currentLocale === 'en' ? `There are ${announcementCount.value} active announcement${announcementCount.value > 1 ? 's' : ''}.` : `Il y a ${announcementCount.value} annonce(s) active(s).`)
            : (localeStore.currentLocale === 'de' ? 'Teilen Sie eine Begruessungsnachricht oder eine Startnotiz.' : localeStore.currentLocale === 'en' ? 'Share a welcome message, launch note, or support contact so people see the tenant as active.' : 'Partagez un message de bienvenue, une note de lancement ou un contact de support.'),
        completed: (announcementCount.value ?? 0) > 0,
        actionLabel:
          (announcementCount.value ?? 0) > 0 ? (localeStore.currentLocale === 'de' ? 'Ankuendigungen prüfen' : localeStore.currentLocale === 'en' ? 'Review announcements' : 'Consulter les annonces') : (localeStore.currentLocale === 'de' ? 'Ankuendigung erstellen' : localeStore.currentLocale === 'en' ? 'Create announcement' : 'Créer une annonce'),
        to: isAdmin.value || isPrincipalAdmin.value ? '/admin/announcements' : '/announcements',
      })
    }

    if (tenantStore.isModuleEnabled('events')) {
      steps.push({
        id: 'events',
        title: localeStore.currentLocale === 'de' ? 'Erstes Ereignis planen' : localeStore.currentLocale === 'en' ? 'Schedule the first event' : 'Planifier le premier événement',
        description:
          eventCount.value && eventCount.value > 0
            ? (localeStore.currentLocale === 'de' ? `Es gibt ${eventCount.value} bevorstehende Veranstaltung(en).` : localeStore.currentLocale === 'en' ? `There are ${eventCount.value} upcoming event${eventCount.value > 1 ? 's' : ''}.` : `Il y a ${eventCount.value} événement(s) à venir.`)
            : (localeStore.currentLocale === 'de' ? 'Fuegen Sie ein Treffen oder ein Gemeinschaftsereignis hinzu.' : localeStore.currentLocale === 'en' ? 'Add a meeting, onboarding call, or community event to give the tenant an immediate rhythm.' : 'Ajoutez une réunion, un appel de prise en main ou un événement communautaire.'),
        completed: (eventCount.value ?? 0) > 0,
        actionLabel: (eventCount.value ?? 0) > 0 ? (localeStore.currentLocale === 'de' ? 'Veranstaltungen prüfen' : localeStore.currentLocale === 'en' ? 'Review events' : 'Consulter les événements') : (localeStore.currentLocale === 'de' ? 'Ereignis erstellen' : localeStore.currentLocale === 'en' ? 'Create event' : 'Créer un événement'),
        to: isAdmin.value || isPrincipalAdmin.value ? '/admin/events' : '/events',
      })
    }

    return steps.filter((step) => !step.adminOnly || isAdmin.value || isPrincipalAdmin.value)
  })

  const completedCount = computed(() => checklist.value.filter((step) => step.completed).length)
  const progressPercent = computed(() => {
    if (checklist.value.length === 0) return 0
    return Math.round((completedCount.value / checklist.value.length) * 100)
  })

  const statusTitle = computed(() => {
    if (isSetupMode.value) {
      return localeStore.currentLocale === 'de' ? 'Dieser Tenant ist noch im Einrichtungsmodus' : localeStore.currentLocale === 'en' ? 'This tenant is still in setup mode' : 'Ce tenant est encore en mode initialisation'
    }
    if (progressPercent.value >= 100) {
      return localeStore.currentLocale === 'de' ? 'Das Tenant-Onboarding wirkt abgeschlossen' : localeStore.currentLocale === 'en' ? 'Tenant onboarding looks complete' : "La configuration du tenant semble complète"
    }
    return localeStore.currentLocale === 'de' ? 'Die Tenant-Einrichtung laeuft noch' : localeStore.currentLocale === 'en' ? 'Tenant setup is in progress' : 'La configuration du tenant est en cours'
  })

  const statusMessage = computed(() => {
    if (isSetupMode.value) {
      return localeStore.currentLocale === 'de' ? 'Nutzen Sie die folgende Checkliste, um aus einem leeren Tenant eine betriebsbereite Umgebung zu machen.' : localeStore.currentLocale === 'en' ? 'Use the checklist below to move from a blank tenant into a working environment with documents, members, and first communications.' : 'Utilisez la checklist ci-dessous pour passer d’un tenant vide à un environnement opérationnel.'
    }
    if (progressPercent.value >= 100) {
      return localeStore.currentLocale === 'de' ? 'Der Tenant verfuegt bereits ueber die wesentlichen Startelemente.' : localeStore.currentLocale === 'en' ? 'The tenant already has the key launch ingredients. Keep the content fresh and maintain the setup hygiene.' : 'Le tenant dispose déjà des éléments essentiels de lancement.'
    }
    return localeStore.currentLocale === 'de' ? 'Einige Startschritte sind bereits abgeschlossen. Finalisieren Sie den Rest fuer einen voll nutzbaren Tenant.' : localeStore.currentLocale === 'en' ? 'Some launch steps are already complete. Finish the remaining items so the tenant feels intentional and usable.' : 'Certaines étapes sont déjà terminées. Finalisez le reste pour rendre le tenant pleinement utilisable.'
  })

  const summaryMetrics = computed<OnboardingSummaryMetric[]>(() => {
    const metrics: OnboardingSummaryMetric[] = [
      {
        label: localeStore.currentLocale === 'de' ? 'Dokumente' : localeStore.currentLocale === 'en' ? 'Documents' : 'Documents',
        value: documentCount.value === null ? '—' : String(documentCount.value),
        hint: localeStore.currentLocale === 'de' ? 'Reife der Wissensbasis' : localeStore.currentLocale === 'en' ? 'Knowledge base readiness' : 'Maturité de la base documentaire',
      },
      {
        label: localeStore.currentLocale === 'de' ? 'Mitglieder' : localeStore.currentLocale === 'en' ? 'Members' : 'Membres',
        value: memberCount.value === null ? '—' : String(memberCount.value),
        hint: localeStore.currentLocale === 'de' ? 'Betriebsbereites Verzeichnis' : localeStore.currentLocale === 'en' ? 'Operational directory' : 'Annuaire opérationnel',
      },
      {
        label: localeStore.currentLocale === 'de' ? 'Ankuendigungen' : localeStore.currentLocale === 'en' ? 'Announcements' : 'Annonces',
        value: announcementCount.value === null ? '—' : String(announcementCount.value),
        hint: localeStore.currentLocale === 'de' ? 'Oeffentliche Kommunikation' : localeStore.currentLocale === 'en' ? 'Public communication' : 'Communication publique',
      },
      {
        label: localeStore.currentLocale === 'de' ? 'Veranstaltungen' : localeStore.currentLocale === 'en' ? 'Events' : 'Événements',
        value: eventCount.value === null ? '—' : String(eventCount.value),
        hint: localeStore.currentLocale === 'de' ? 'Rhythmus der Gemeinschaft' : localeStore.currentLocale === 'en' ? 'Community cadence' : 'Rythme communautaire',
      },
    ]

    return metrics
  })

  const nextStep = computed(() => checklist.value.find((step) => !step.completed) ?? null)

  async function loadOnboarding() {
    const documentPromise = listDocuments()
    const announcementPromise = tenantStore.isModuleEnabled('announcements')
      ? listActiveAnnouncements()
      : Promise.resolve([])
    const eventPromise = tenantStore.isModuleEnabled('events')
      ? listPublicEvents()
      : Promise.resolve([])
    const memberPromise =
      (isAdmin.value || isPrincipalAdmin.value) && tenantStore.isModuleEnabled('membership')
        ? listMembers()
        : Promise.resolve([])

    const [documents, announcements, events, members] = await Promise.all([
      documentPromise,
      announcementPromise,
      eventPromise,
      memberPromise,
    ])

    documentCount.value = documents.length
    announcementCount.value = announcements.length
    eventCount.value = events.length
    memberCount.value = members.length
    lastRefreshedAt.value = new Date().toISOString()
  }

  async function refresh() {
    clearError()
    await run(loadOnboarding)
  }

  async function retryRefresh() {
    await retry(loadOnboarding)
  }

  return {
    loading,
    error,
    isRecovering,
    documentCount,
    memberCount,
    eventCount,
    announcementCount,
    lastRefreshedAt,
    checklist,
    completedCount,
    progressPercent,
    statusTitle,
    statusMessage,
    summaryMetrics,
    nextStep,
    refresh,
    retryRefresh,
  }
}
