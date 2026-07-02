import { computed, ref } from 'vue'
import { listDocuments, type DocumentListItemResponse } from '@/api/documents.api'
import { listMembers, type MembershipProfileResponse } from '@/api/membership.api'
import { getContributionSummary, type ContributionSummary } from '@/api/contributions.api'
import { listActiveAnnouncements, type AnnouncementResponse } from '@/api/announcements.api'
import { listPublicEvents, type EventResponse } from '@/api/events.api'
import { listAuditEvents, type AuditEventResponse } from '@/api/audit.api'
import { useTenantStore } from '@/stores/tenant.store'
import { useAuthStore } from '@/stores/auth.store'

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
    if (isPresident.value) return 'President governance cockpit'
    if (isVicePresident.value) return 'Vice president governance cockpit'
    if (isPrincipalAdmin.value || isAdmin.value) return 'Executive governance cockpit'
    return 'Governance cockpit'
  })

  const subtitle = computed(() => {
    if (isPresident.value) {
      return 'Cross-module oversight for strategic governance, with audit visibility and limited actions.'
    }
    if (isVicePresident.value) {
      return 'Deputy executive oversight focused on clear visibility, not broad system control.'
    }
    return 'Executive oversight for roles that need a mature association-wide view without principal-admin power.'
  })

  const cards = computed<GovernanceCard[]>(() => {
    const rows: GovernanceCard[] = [
      {
        id: 'documents',
        label: 'Documents',
        value: String(documents.value.length),
        hint: 'Governance references available to the tenant',
        tone: documents.value.length === 0 ? 'warning' : 'neutral',
      },
      {
        id: 'announcements',
        label: 'Active announcements',
        value: String(announcements.value.length),
        hint: 'Published member-facing notices',
        tone: announcements.value.length === 0 ? 'warning' : 'neutral',
        to: '/announcements',
      },
      {
        id: 'events',
        label: 'Upcoming events',
        value: String(events.value.length),
        hint: 'Visible scheduled association activity',
        tone: events.value.length === 0 ? 'warning' : 'neutral',
        to: '/events',
      },
    ]

    if (tenantStore.isModuleEnabled('membership')) {
      rows.push({
        id: 'members',
        label: 'Member directory',
        value: String(members.value.length),
        hint: 'Active profiles in the tenant',
        tone: members.value.length === 0 ? 'warning' : 'neutral',
      })
    }

    if (contributionSummary.value) {
      const balance = Number(contributionSummary.value.total_balance)
      rows.push({
        id: 'finance',
        label: 'Contribution balance',
        value: `${contributionSummary.value.total_balance} EUR`,
        hint: `${contributionSummary.value.total_count} contribution record(s)`,
        tone: balance > 0 ? 'warning' : 'success',
        to: '/finance-audit',
      })
    }

    if (hasAuditAccess.value) {
      rows.push({
        id: 'audit',
        label: 'Audit trail',
        value: String(auditEvents.value.length),
        hint: 'Recent sensitive actions',
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
        label: 'Review events',
        description: 'Check the current association schedule',
        to: '/events',
      },
      {
        id: 'announcements',
        label: 'Open announcements',
        description: 'Review active member communications',
        to: '/announcements',
      },
      {
        id: 'policies',
        label: 'Open policies',
        description: 'Inspect governance rules and references',
        to: '/policies',
      },
    ]

    if (hasAuditAccess.value) {
      actions.unshift({
        id: 'audit',
        label: 'Review audit trail',
        description: 'Inspect recent sensitive actions',
        to: '/admin/audit',
      })
    }

    if (isPresident.value || isPrincipalAdmin.value || isAdmin.value) {
      actions.splice(1, 0, {
        id: 'finance',
        label: 'Open finance audit',
        description: 'Review contribution totals and balances',
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
      error.value = (err as { message?: string })?.message || 'Could not load the governance cockpit.'
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
