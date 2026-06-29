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
import { useTenantOnboarding } from '@/composables/useTenantOnboarding'

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
  const tenantStore = useTenantStore()
  const onboarding = useTenantOnboarding()

  const loading = ref(false)
  const error = ref('')
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
        label: 'Documents',
        value: String(documentCount.value),
        hint: ingestionHealth.value?.failed_count
          ? `${ingestionHealth.value.failed_count} failed ingestion job(s)`
          : 'Knowledge base assets',
        tone: ingestionHealth.value?.failed_count ? 'warning' : 'neutral',
        to: '/admin/documents',
      },
      {
        id: 'audit',
        label: 'Audit events',
        value: String(auditEventCount.value),
        hint: 'Recent sensitive actions',
        tone: 'neutral',
        to: '/admin/audit',
      },
    ]

    if (modules.value.membership) {
      metrics.push({
        id: 'members',
        label: 'Members',
        value: String(memberCount.value),
        hint: 'Active directory size',
        tone: memberCount.value === 0 ? 'warning' : 'neutral',
        to: '/admin/members',
      })
    }

    if (modules.value.contributions && contributionSummary.value) {
      const balance = Number(contributionSummary.value.total_balance)
      metrics.push({
        id: 'contributions',
        label: 'Open balance',
        value: `${contributionSummary.value.total_balance} EUR`,
        hint: `${contributionSummary.value.total_count} contribution record(s)`,
        tone: balance > 0 ? 'warning' : 'success',
        to: '/admin/contributions',
      })
    }

    if (modules.value.announcements) {
      metrics.push({
        id: 'announcements',
        label: 'Announcements',
        value: String(activeAnnouncementCount.value),
        hint: 'Currently active notices',
        tone: activeAnnouncementCount.value === 0 ? 'warning' : 'neutral',
        to: '/admin/announcements',
      })
    }

    if (modules.value.events) {
      metrics.push({
        id: 'events',
        label: 'Upcoming events',
        value: String(upcomingEventCount.value),
        hint: 'Scheduled tenant rhythm',
        tone: upcomingEventCount.value === 0 ? 'warning' : 'neutral',
        to: '/admin/events',
      })
    }

    if (modules.value.notifications) {
      metrics.push({
        id: 'channels',
        label: 'Configured channels',
        value: String(configuredChannelCount.value),
        hint: 'Optional outbound diagnostics',
        tone: configuredChannelCount.value === 0 ? 'warning' : 'neutral',
        to: '/admin/notifications',
      })
    }

    return metrics
  })

  const riskItems = computed<AdminRiskItem[]>(() => {
    const risks: AdminRiskItem[] = []

    if (documentCount.value === 0) {
      risks.push({
        id: 'no-documents',
        title: 'Knowledge base is empty',
        description: 'Upload the first trusted document so chat and retrieval can become useful.',
        tone: 'warning',
        to: '/admin/documents',
        actionLabel: 'Upload documents',
      })
    }

    if (modules.value.membership && memberCount.value === 0) {
      risks.push({
        id: 'no-members',
        title: 'No member directory yet',
        description: 'Add or import members so the tenant stops feeling like a blank workspace.',
        tone: 'warning',
        to: '/admin/members',
        actionLabel: 'Open members',
      })
    }

    if ((ingestionHealth.value?.failed_count ?? 0) > 0) {
      risks.push({
        id: 'failed-ingestion',
        title: 'Document ingestion needs attention',
        description: `${ingestionHealth.value?.failed_count} ingestion job(s) failed. Review errors and retry where needed.`,
        tone: 'danger',
        to: '/admin/documents',
        actionLabel: 'Review documents',
      })
    }

    if (modules.value.contributions && contributionSummary.value && Number(contributionSummary.value.total_balance) > 0) {
      risks.push({
        id: 'open-balance',
        title: 'Outstanding contribution balance',
        description: `There is still ${contributionSummary.value.total_balance} EUR open across the current contribution records.`,
        tone: 'warning',
        to: '/admin/contributions',
        actionLabel: 'Review contributions',
      })
    }

    if (risks.length === 0) {
      risks.push({
        id: 'healthy',
        title: 'No immediate operational warnings',
        description: 'The tenant has the core launch ingredients and no urgent ingestion or setup issue was detected.',
        tone: 'success',
        to: '/admin/audit',
        actionLabel: 'Review audit trail',
      })
    }

    return risks
  })

  const quickActions = computed<AdminQuickAction[]>(() => {
    const actions: AdminQuickAction[] = [
      {
        id: 'settings',
        label: 'Tenant settings',
        description: 'Branding, modules, and configuration',
        to: '/admin/settings',
      },
      {
        id: 'documents',
        label: 'Documents',
        description: 'Upload, inspect, and recover ingestion',
        to: '/admin/documents',
      },
      {
        id: 'access',
        label: 'Access',
        description: 'Invite teammates and monitor onboarding',
        to: '/admin/access',
      },
      {
        id: 'audit',
        label: 'Audit trail',
        description: 'Review sensitive admin activity',
        to: '/admin/audit',
      },
    ]

    if (modules.value.membership) {
      actions.push({
        id: 'members',
        label: 'Members',
        description: 'Import or manage member profiles',
        to: '/admin/members',
      })
    }

    if (modules.value.announcements) {
      actions.push({
        id: 'announcements',
        label: 'Announcements',
        description: 'Publish active tenant communications',
        to: '/admin/announcements',
      })
    }

    if (modules.value.events) {
      actions.push({
        id: 'events',
        label: 'Events',
        description: 'Schedule upcoming milestones',
        to: '/admin/events',
      })
    }

    if (modules.value.notifications) {
      actions.push({
        id: 'channels',
        label: 'Channels',
        description: 'Inspect notification diagnostics',
        to: '/admin/notifications',
      })
    }

    return actions
  })

  async function refresh() {
    loading.value = true
    error.value = ''

    try {
      await onboarding.refresh()

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

      await Promise.all(work)
    } catch (err: unknown) {
      error.value = (err as { message?: string })?.message || 'Could not load the admin overview.'
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    modules,
    summaryMetrics,
    riskItems,
    quickActions,
    onboarding,
    ingestionHealth,
    contributionSummary,
    refresh,
  }
}
