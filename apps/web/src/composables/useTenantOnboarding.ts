import { computed, ref } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { useTenantStore } from '@/stores/tenant.store'
import { listActiveAnnouncements } from '@/api/announcements.api'
import { listPublicEvents } from '@/api/events.api'
import { listDocuments } from '@/api/documents.api'
import { listMembers } from '@/api/membership.api'

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

  const loading = ref(false)
  const error = ref('')
  const documentCount = ref<number | null>(null)
  const memberCount = ref<number | null>(null)
  const eventCount = ref<number | null>(null)
  const announcementCount = ref<number | null>(null)
  const lastRefreshedAt = ref<string | null>(null)

  const isAdmin = computed(() => authStore.user?.roles.includes('admin') ?? false)
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
        title: 'Confirm tenant branding',
        description:
          'Review the organization name, primary color, and logo in tenant settings so the shell feels ready for customers.',
        completed: hasCustomBranding.value,
        actionLabel: 'Open tenant settings',
        to: '/admin/settings',
        adminOnly: true,
      },
      {
        id: 'documents',
        title: 'Upload the first document',
        description:
          documentCount.value && documentCount.value > 0
            ? `You already have ${documentCount.value} document${documentCount.value > 1 ? 's' : ''}. Keep building the knowledge base.`
            : 'Start with a policy, welcome note, or operational document that the team can trust.',
        completed: (documentCount.value ?? 0) > 0,
        actionLabel:
          (documentCount.value ?? 0) > 0 ? 'Review documents' : 'Upload first document',
        to: '/admin/documents',
        adminOnly: true,
      },
    ]

    if (tenantStore.isModuleEnabled('membership') && tenantStore.isModuleEnabled('contributions') && (isAdmin.value || isTreasurer.value)) {
      steps.push({
        id: 'finance',
        title: 'Review the finance workspace',
        description:
          'Check member balances, create contribution records, and record incoming payments from the dedicated finance surface.',
        completed: (memberCount.value ?? 0) > 0,
        actionLabel: 'Open finance workspace',
        to: '/finance',
      })
    }

    if (tenantStore.isModuleEnabled('membership')) {
      steps.push({
        id: 'members',
        title: 'Add or import members',
        description:
          memberCount.value && memberCount.value > 0
            ? `There are ${memberCount.value} member profile${memberCount.value > 1 ? 's' : ''} in this tenant.`
            : 'Import a CSV or add the first member profile so the tenant has a real working directory.',
        completed: (memberCount.value ?? 0) > 0,
        actionLabel: (memberCount.value ?? 0) > 0 ? 'Manage members' : 'Open members',
        to: '/admin/members',
        adminOnly: true,
      })
    }

    if (tenantStore.isModuleEnabled('announcements')) {
      steps.push({
        id: 'announcements',
        title: 'Publish a first announcement',
        description:
          announcementCount.value && announcementCount.value > 0
            ? `There are ${announcementCount.value} active announcement${announcementCount.value > 1 ? 's' : ''}.`
            : 'Share a welcome message, launch note, or support contact so people see the tenant as active.',
        completed: (announcementCount.value ?? 0) > 0,
        actionLabel:
          (announcementCount.value ?? 0) > 0 ? 'Review announcements' : 'Create announcement',
        to: '/admin/announcements',
      })
    }

    if (tenantStore.isModuleEnabled('events')) {
      steps.push({
        id: 'events',
        title: 'Schedule the first event',
        description:
          eventCount.value && eventCount.value > 0
            ? `There are ${eventCount.value} upcoming event${eventCount.value > 1 ? 's' : ''}.`
            : 'Add a meeting, onboarding call, or community event to give the tenant an immediate rhythm.',
        completed: (eventCount.value ?? 0) > 0,
        actionLabel: (eventCount.value ?? 0) > 0 ? 'Review events' : 'Create event',
        to: '/admin/events',
      })
    }

    return steps.filter((step) => !step.adminOnly || isAdmin.value)
  })

  const completedCount = computed(() => checklist.value.filter((step) => step.completed).length)
  const progressPercent = computed(() => {
    if (checklist.value.length === 0) return 0
    return Math.round((completedCount.value / checklist.value.length) * 100)
  })

  const statusTitle = computed(() => {
    if (isSetupMode.value) {
      return 'This tenant is still in setup mode'
    }
    if (progressPercent.value >= 100) {
      return 'Tenant onboarding looks complete'
    }
    return 'Tenant setup is in progress'
  })

  const statusMessage = computed(() => {
    if (isSetupMode.value) {
      return 'Use the checklist below to move from a blank tenant into a working environment with documents, members, and first communications.'
    }
    if (progressPercent.value >= 100) {
      return 'The tenant already has the key launch ingredients. Keep the content fresh and maintain the setup hygiene.'
    }
    return 'Some launch steps are already complete. Finish the remaining items so the tenant feels intentional and usable.'
  })

  const summaryMetrics = computed<OnboardingSummaryMetric[]>(() => {
    const metrics: OnboardingSummaryMetric[] = [
      {
        label: 'Documents',
        value: documentCount.value === null ? '—' : String(documentCount.value),
        hint: 'Knowledge base readiness',
      },
      {
        label: 'Members',
        value: memberCount.value === null ? '—' : String(memberCount.value),
        hint: 'Operational directory',
      },
      {
        label: 'Announcements',
        value: announcementCount.value === null ? '—' : String(announcementCount.value),
        hint: 'Public communication',
      },
      {
        label: 'Events',
        value: eventCount.value === null ? '—' : String(eventCount.value),
        hint: 'Community cadence',
      },
    ]

    return metrics
  })

  const nextStep = computed(() => checklist.value.find((step) => !step.completed) ?? null)

  async function refresh() {
    loading.value = true
    error.value = ''

    try {
      const documentPromise = listDocuments().catch(() => [])
      const announcementPromise = tenantStore.isModuleEnabled('announcements')
        ? listActiveAnnouncements().catch(() => [])
        : Promise.resolve([])
      const eventPromise = tenantStore.isModuleEnabled('events')
        ? listPublicEvents().catch(() => [])
        : Promise.resolve([])
      const memberPromise =
        isAdmin.value && tenantStore.isModuleEnabled('membership')
          ? listMembers().catch(() => [])
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
    } catch (err: unknown) {
      error.value = (err as { message?: string })?.message || 'Could not load onboarding guidance.'
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
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
  }
}
