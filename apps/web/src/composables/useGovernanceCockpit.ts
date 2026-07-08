import { computed, ref } from 'vue'
import { listDocuments, type DocumentListItemResponse } from '@/api/documents.api'
import { listMembers, type MembershipProfileResponse } from '@/api/membership.api'
import { getContributionSummary, type ContributionSummary } from '@/api/contributions.api'
import { listActiveAnnouncements, type AnnouncementResponse } from '@/api/announcements.api'
import { listPublicEvents, type EventResponse } from '@/api/events.api'
import { listAuditEvents, type AuditEventResponse } from '@/api/audit.api'
import { useTenantStore } from '@/stores/tenant.store'
import { useAuthStore } from '@/stores/auth.store'
import { useLocaleStore } from '@/stores/locale.store'

export interface GovernanceCard {
  id: string
  label: string
  value: string
  hint: string
  tone: 'neutral' | 'success' | 'warning' | 'danger'
  to?: string
}

export interface GovernanceAction {
  id: string
  label: string
  description: string
  to: string
}

export function useGovernanceCockpit() {
  const authStore = useAuthStore()
  const tenantStore = useTenantStore()
  const localeStore = useLocaleStore()

  const loading = ref(false)
  const error = ref('')
  const members = ref<MembershipProfileResponse[]>([])
  const documents = ref<DocumentListItemResponse[]>([])
  const announcements = ref<AnnouncementResponse[]>([])
  const events = ref<EventResponse[]>([])
  const auditEvents = ref<AuditEventResponse[]>([])
  const contributionSummary = ref<ContributionSummary | null>(null)

  const userRoles = computed(() => authStore.user?.roles ?? [])
  const isPresident = computed(() => userRoles.value.includes('president'))
  const isVicePresident = computed(() => userRoles.value.includes('vice_president'))
  const isPrincipalAdmin = computed(() => userRoles.value.includes('principal_admin'))
  const isAdmin = computed(() => userRoles.value.includes('admin'))

  const hasAuditAccess = computed(() =>
    userRoles.value.some((role) => ['president', 'principal_admin', 'admin'].includes(role)),
  )

  const heading = computed(() => {
    if (isPresident.value) return localeStore.currentLocale === 'de' ? 'Governance-Cockpit des Praesidenten' : localeStore.currentLocale === 'en' ? 'President governance cockpit' : 'Cockpit de gouvernance du président'
    if (isVicePresident.value) return localeStore.currentLocale === 'de' ? 'Governance-Cockpit des Vizepraesidenten' : localeStore.currentLocale === 'en' ? 'Vice president governance cockpit' : 'Cockpit de gouvernance du vice-président'
    if (isPrincipalAdmin.value || isAdmin.value) return localeStore.currentLocale === 'de' ? 'Exekutives Governance-Cockpit' : localeStore.currentLocale === 'en' ? 'Executive governance cockpit' : 'Cockpit de gouvernance exécutive'
    return localeStore.currentLocale === 'de' ? 'Governance-Cockpit' : localeStore.currentLocale === 'en' ? 'Governance cockpit' : 'Cockpit de gouvernance'
  })

  const subtitle = computed(() => {
    if (isPresident.value) {
      return 'Cross-module oversight for strategic governance, with audit visibility and limited actions.'
    }
    if (isVicePresident.value) {
      return localeStore.currentLocale === 'de' ? 'Stellvertretende Aufsicht mit klarer Sichtbarkeit und ohne breite Systemkontrolle.' : localeStore.currentLocale === 'en' ? 'Deputy executive oversight focused on clear visibility, not broad system control.' : 'Supervision exécutive adjointe centrée sur une visibilité claire, sans contrôle global du système.'
    }
    return localeStore.currentLocale === 'de' ? 'Exekutive Aufsicht fuer Rollen, die eine reife vereinsweite Sicht ohne Hauptadmin-Rechte benoetigen.' : localeStore.currentLocale === 'en' ? 'Executive oversight for roles that need a mature association-wide view without principal-admin power.' : "Supervision exécutive pour les rôles qui ont besoin d'une vue globale mature de l'association sans droits de principal admin."
  })

  const cards = computed<GovernanceCard[]>(() => {
    const rows: GovernanceCard[] = [
      {
        id: 'documents',
        label: localeStore.currentLocale === 'de' ? 'Dokumente' : localeStore.currentLocale === 'en' ? 'Documents' : 'Documents',
        value: String(documents.value.length),
        hint: localeStore.currentLocale === 'de' ? 'Referenzdokumente der gouvernance du tenant' : localeStore.currentLocale === 'en' ? 'Governance references available to the tenant' : 'Références de gouvernance disponibles pour le tenant',
        tone: documents.value.length === 0 ? 'warning' : 'neutral',
      },
      {
        id: 'announcements',
        label: localeStore.currentLocale === 'de' ? 'Annonces actives' : localeStore.currentLocale === 'en' ? 'Active announcements' : 'Annonces actives',
        value: String(announcements.value.length),
        hint: localeStore.currentLocale === 'de' ? 'Publizierte Mitteilungen fuer Mitglieder' : localeStore.currentLocale === 'en' ? 'Published member-facing notices' : 'Annonces publiées visibles par les membres',
        tone: announcements.value.length === 0 ? 'warning' : 'neutral',
        to: '/announcements',
      },
      {
        id: 'events',
        label: localeStore.currentLocale === 'de' ? 'Bevorstehende Veranstaltungen' : localeStore.currentLocale === 'en' ? 'Upcoming events' : 'Événements à venir',
        value: String(events.value.length),
        hint: localeStore.currentLocale === 'de' ? 'Sichtbare geplante Vereinsaktivitaeten' : localeStore.currentLocale === 'en' ? 'Visible scheduled association activity' : "Activité planifiée visible de l'association",
        tone: events.value.length === 0 ? 'warning' : 'neutral',
        to: '/events',
      },
    ]

    if (tenantStore.isModuleEnabled('membership')) {
      rows.push({
        id: 'members',
        label: localeStore.currentLocale === 'de' ? 'Mitgliederverzeichnis' : localeStore.currentLocale === 'en' ? 'Member directory' : 'Répertoire des membres',
        value: String(members.value.length),
        hint: localeStore.currentLocale === 'de' ? 'Aktive Profile im Tenant' : localeStore.currentLocale === 'en' ? 'Active profiles in the tenant' : 'Profils actifs dans le tenant',
        tone: members.value.length === 0 ? 'warning' : 'neutral',
      })
    }

    if (contributionSummary.value) {
      const balance = Number(contributionSummary.value.total_balance)
      rows.push({
        id: 'finance',
        label: localeStore.currentLocale === 'de' ? 'Beitragssaldo' : localeStore.currentLocale === 'en' ? 'Contribution balance' : 'Solde des cotisations',
        value: `${contributionSummary.value.total_balance} EUR`,
        hint: localeStore.currentLocale === 'de' ? `${contributionSummary.value.total_count} Beitragsenregistrements` : localeStore.currentLocale === 'en' ? `${contributionSummary.value.total_count} contribution record(s)` : `${contributionSummary.value.total_count} enregistrement(s) de cotisation`,
        tone: balance > 0 ? 'warning' : 'success',
        to: '/finance-audit',
      })
    }

    if (hasAuditAccess.value) {
      rows.push({
        id: 'audit',
        label: localeStore.currentLocale === 'de' ? 'Audit-Protokoll' : localeStore.currentLocale === 'en' ? 'Audit trail' : "Journal d'audit",
        value: String(auditEvents.value.length),
        hint: localeStore.currentLocale === 'de' ? 'Kuerzlich sensible Aktionen' : localeStore.currentLocale === 'en' ? 'Recent sensitive actions' : 'Actions sensibles récentes',
        tone: auditEvents.value.length === 0 ? 'warning' : 'neutral',
        to: '/admin/audit',
      })
    }

    return rows
  })

  const quickActions = computed<GovernanceAction[]>(() => {
    const actions: GovernanceAction[] = [
      {
        id: 'events',
        label: localeStore.currentLocale === 'de' ? 'Veranstaltungen prüfen' : localeStore.currentLocale === 'en' ? 'Review events' : 'Consulter les événements',
        description: localeStore.currentLocale === 'de' ? 'Aktuellen Vereinskalender prüfen' : localeStore.currentLocale === 'en' ? 'Check the current association schedule' : "Vérifier le calendrier actuel de l'association",
        to: '/events',
      },
      {
        id: 'announcements',
        label: localeStore.currentLocale === 'de' ? 'Annonces öffnen' : localeStore.currentLocale === 'en' ? 'Open announcements' : 'Ouvrir les annonces',
        description: localeStore.currentLocale === 'de' ? 'Aktive Mitgliederkommunikation prüfen' : localeStore.currentLocale === 'en' ? 'Review active member communications' : 'Consulter les communications actives vers les membres',
        to: '/announcements',
      },
      {
        id: 'policies',
        label: localeStore.currentLocale === 'de' ? 'Regeln öffnen' : localeStore.currentLocale === 'en' ? 'Open policies' : 'Ouvrir les règlements',
        description: localeStore.currentLocale === 'de' ? 'Regeln und références prüfen' : localeStore.currentLocale === 'en' ? 'Inspect governance rules and references' : 'Consulter les règles et références de gouvernance',
        to: '/policies',
      },
    ]

    if (hasAuditAccess.value) {
      actions.unshift({
        id: 'audit',
        label: localeStore.currentLocale === 'de' ? 'Audit-Protokoll prüfen' : localeStore.currentLocale === 'en' ? 'Review audit trail' : "Consulter le journal d'audit",
        description: localeStore.currentLocale === 'de' ? 'Kuerzliche sensible Aktionen prüfen' : localeStore.currentLocale === 'en' ? 'Inspect recent sensitive actions' : 'Consulter les actions sensibles récentes',
        to: '/admin/audit',
      })
    }

    if (isPresident.value || isPrincipalAdmin.value || isAdmin.value) {
      actions.splice(1, 0, {
        id: 'finance',
        label: localeStore.currentLocale === 'de' ? 'Finanzaudit öffnen' : localeStore.currentLocale === 'en' ? 'Open finance audit' : "Ouvrir l'audit finances",
        description: localeStore.currentLocale === 'de' ? 'Beitragssummen und Salden prüfen' : localeStore.currentLocale === 'en' ? 'Review contribution totals and balances' : 'Consulter les totaux et soldes de cotisation',
        to: '/finance-audit',
      })
    }

    return actions
  })

  async function refresh() {
    loading.value = true
    error.value = ''

    try {
      const work: Promise<unknown>[] = [
        listDocuments().then((rows) => {
          documents.value = rows
        }),
        listActiveAnnouncements().then((rows) => {
          announcements.value = rows
        }),
        listPublicEvents().then((rows) => {
          events.value = rows
        }),
        listMembers().then((rows) => {
          members.value = rows
        }),
        getContributionSummary().then((rows) => {
          contributionSummary.value = rows
        }),
      ]

      if (hasAuditAccess.value) {
        work.push(
          listAuditEvents({ limit: 10 }).then((rows) => {
            auditEvents.value = rows
          }),
        )
      } else {
        auditEvents.value = []
      }

      await Promise.all(work)
    } catch (err: unknown) {
      error.value = (err as { message?: string })?.message || (localeStore.currentLocale === 'de' ? 'Le cockpit de gouvernance n’a pas pu être chargé.' : localeStore.currentLocale === 'en' ? 'Could not load the governance cockpit.' : "Le cockpit de gouvernance n'a pas pu être chargé.")
    } finally {
      loading.value = false
    }
  }

  return {
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
  }
}
