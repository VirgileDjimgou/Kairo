import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { useTenantStore } from '@/stores/tenant.store'

type NavItem = {
  label: string
  to: string
  icon: string
}

type NavSection = {
  label: string
  items: NavItem[]
}

export function useRoleNavigation() {
  const authStore = useAuthStore()
  const tenantStore = useTenantStore()
  const roles = computed(() => authStore.user?.roles ?? [])

  const isMember = computed(() => roles.value.includes('member') && roles.value.length === 1)
  const isPrincipalAdmin = computed(() => roles.value.includes('principal_admin'))
  const isAdmin = computed(() => roles.value.includes('admin'))
  const isTreasurer = computed(() => roles.value.includes('treasurer'))
  const isSecretaryGeneral = computed(() => roles.value.includes('secretary_general'))
  const isAuditor = computed(() => roles.value.includes('auditor'))
  const isPresident = computed(() => roles.value.includes('president'))
  const isVicePresident = computed(() => roles.value.includes('vice_president'))
  const isCensor = computed(() => roles.value.includes('censor'))
  const isSportsManager = computed(() => roles.value.includes('sports_manager'))

  const showFinanceWorkspace = computed(() =>
    (isAdmin.value || isPrincipalAdmin.value || isTreasurer.value) &&
    tenantStore.isModuleEnabled('membership') &&
    tenantStore.isModuleEnabled('contributions'),
  )

  const showFinanceAuditWorkspace = computed(() =>
    (isAuditor.value || isPresident.value || isPrincipalAdmin.value || isAdmin.value) &&
    tenantStore.isModuleEnabled('membership') &&
    tenantStore.isModuleEnabled('contributions'),
  )

  const showSecretaryWorkspace = computed(() =>
    (isSecretaryGeneral.value || isPrincipalAdmin.value) &&
    tenantStore.isModuleEnabled('policies') &&
    tenantStore.isModuleEnabled('announcements'),
  )

  const showGovernanceCockpit = computed(() =>
    isPresident.value || isVicePresident.value || isPrincipalAdmin.value || isAdmin.value,
  )

  const showCensorWorkspace = computed(() =>
    (isCensor.value || isPresident.value || isPrincipalAdmin.value || isAdmin.value) &&
    tenantStore.isModuleEnabled('disciplinary'),
  )

  const showSportsWorkspace = computed(() =>
    (isSportsManager.value || isPrincipalAdmin.value || isAdmin.value) &&
    tenantStore.isModuleEnabled('events'),
  )

  const appNavigation = computed<NavSection[]>(() => {
    const sections: NavSection[] = [
      {
        label: 'Personal',
        items: [
          { label: 'Dashboard', to: '/dashboard', icon: 'bi-grid-1x2' },
          { label: 'My profile', to: '/members/profile', icon: 'bi-person-badge' },
          { label: 'Account security', to: '/account/security', icon: 'bi-shield-check' },
          { label: 'Chat', to: '/chat', icon: 'bi-chat-dots' },
        ].filter((item) => item.to !== '/chat' || tenantStore.isModuleEnabled('chat')),
      },
    ]

    if (isMember.value) {
      sections.push({
        label: 'Read',
        items: [
          { label: 'Events', to: '/events', icon: 'bi-calendar-event' },
          { label: 'Announcements', to: '/announcements', icon: 'bi-megaphone' },
          { label: 'Policies', to: '/policies', icon: 'bi-journal-text' },
        ].filter((item) => tenantStore.isModuleEnabled(item.to.slice(1))),
      })
      return sections
    }

    const workspaceItems: NavItem[] = []

    if (showSecretaryWorkspace.value) {
      workspaceItems.push({ label: 'Secretary workspace', to: '/secretary', icon: 'bi-journal-richtext' })
    }
    if (showFinanceWorkspace.value) {
      workspaceItems.push({ label: 'Finance workspace', to: '/finance', icon: 'bi-cash-coin' })
    }
    if (showFinanceAuditWorkspace.value) {
      workspaceItems.push({ label: 'Finance audit', to: '/finance-audit', icon: 'bi-clipboard-data' })
    }
    if (showGovernanceCockpit.value) {
      workspaceItems.push({ label: 'Governance cockpit', to: '/governance', icon: 'bi-diagram-3' })
    }
    if (showCensorWorkspace.value) {
      workspaceItems.push({ label: 'Disciplinary console', to: '/censor', icon: 'bi-shield-lock' })
    }
    if (showSportsWorkspace.value) {
      workspaceItems.push({ label: 'Sports workspace', to: '/sports', icon: 'bi-trophy' })
    }
    if (isPrincipalAdmin.value || isAdmin.value) {
      workspaceItems.push({
        label: isPrincipalAdmin.value ? 'Principal admin control plane' : 'Admin plane',
        to: '/admin',
        icon: 'bi-shield-lock',
      })
    }

    if (workspaceItems.length) {
      sections.push({
        label: 'Workspaces',
        items: workspaceItems,
      })
    }

    const communityItems: NavItem[] = [
      { label: 'Events', to: '/events', icon: 'bi-calendar-event' },
      { label: 'Announcements', to: '/announcements', icon: 'bi-megaphone' },
      { label: 'Policies', to: '/policies', icon: 'bi-journal-text' },
    ].filter((item) => tenantStore.isModuleEnabled(item.to.slice(1)))

    if (communityItems.length) {
      sections.push({
        label: 'Community',
        items: communityItems,
      })
    }

    return sections
  })

  const adminNavigation = computed<NavSection[]>(() => {
    const sections: NavSection[] = [
      {
        label: 'Overview',
        items: [{ label: 'Overview', to: '/admin', icon: 'bi-speedometer2' }],
      },
    ]

    const operations: NavItem[] = []
    if (tenantStore.isModuleEnabled('membership')) {
      operations.push({ label: 'Members', to: '/admin/members', icon: 'bi-people' })
    }
    if (tenantStore.isModuleEnabled('contributions')) {
      operations.push({ label: 'Contributions', to: '/admin/contributions', icon: 'bi-cash-stack' })
    }
    if (tenantStore.isModuleEnabled('policies')) {
      operations.push({ label: 'Policies', to: '/admin/policies', icon: 'bi-journal-text' })
    }
    if (tenantStore.isModuleEnabled('disciplinary')) {
      operations.push({ label: 'Disciplinary', to: '/admin/disciplinary', icon: 'bi-shield-lock' })
    }
    operations.push({ label: 'Access', to: '/admin/access', icon: 'bi-person-plus' })
    operations.push({ label: 'Documents', to: '/admin/documents', icon: 'bi-file-earmark-text' })

    if (operations.length) {
      sections.push({ label: 'Operations', items: operations })
    }

    const governance: NavItem[] = [{ label: 'Audit trail', to: '/admin/audit', icon: 'bi-shield-check' }]
    if (tenantStore.isModuleEnabled('chat')) {
      governance.push({ label: 'Chat audit', to: '/admin/chat-queries', icon: 'bi-journal-text' })
    }
    if (tenantStore.isModuleEnabled('events')) {
      governance.push({ label: 'Events', to: '/admin/events', icon: 'bi-calendar-event' })
    }
    if (tenantStore.isModuleEnabled('announcements')) {
      governance.push({ label: 'Announcements', to: '/admin/announcements', icon: 'bi-megaphone' })
    }
    if (tenantStore.isModuleEnabled('notifications')) {
      governance.push({ label: 'Channels', to: '/admin/notifications', icon: 'bi-broadcast-pin' })
    }

    sections.push({ label: 'Governance', items: governance })
    sections.push({ label: 'Settings', items: [{ label: 'Settings', to: '/admin/settings', icon: 'bi-gear' }] })

    return sections
  })

  const appHomeLabel = computed(() => {
    if (isMember.value) return 'Member portal'
    if (isSecretaryGeneral.value) return 'Secretary workspace'
    if (isTreasurer.value) return 'Finance workspace'
    if (isAuditor.value) return 'Finance audit'
    if (isCensor.value) return 'Disciplinary console'
    if (isSportsManager.value) return 'Sports workspace'
    if (showGovernanceCockpit.value) return 'Governance cockpit'
    return isPrincipalAdmin.value ? 'Principal admin control plane' : 'Organization portal'
  })

  const adminConsoleLabel = computed(() =>
    isPrincipalAdmin.value ? 'Principal Admin Control Plane' : 'Admin Console',
  )

  return {
    roles,
    isMember,
    isPrincipalAdmin,
    showFinanceWorkspace,
    showFinanceAuditWorkspace,
    showSecretaryWorkspace,
    showGovernanceCockpit,
    showCensorWorkspace,
    showSportsWorkspace,
    appNavigation,
    adminNavigation,
    appHomeLabel,
    adminConsoleLabel,
  }
}
