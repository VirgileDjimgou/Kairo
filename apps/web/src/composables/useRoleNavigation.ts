import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { useTenantStore } from '@/stores/tenant.store'
import { useLocaleStore } from '@/stores/locale.store'

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
  const localeStore = useLocaleStore()
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
    isSecretaryGeneral.value || isPrincipalAdmin.value || isAdmin.value,
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
        label: localeStore.t('layout.personal'),
        items: [
          { label: localeStore.t('nav.dashboard'), to: '/dashboard', icon: 'bi-grid-1x2' },
          { label: localeStore.t('nav.myProfile'), to: '/members/profile', icon: 'bi-person-badge' },
          { label: localeStore.t('nav.accountSecurity'), to: '/account/security', icon: 'bi-shield-check' },
          { label: localeStore.t('nav.chat'), to: '/chat', icon: 'bi-chat-dots' },
        ].filter((item) => item.to !== '/chat' || tenantStore.isModuleEnabled('chat')),
      },
    ]

    if (isMember.value) {
      sections.push({
        label: localeStore.t('layout.read'),
        items: [
          { label: localeStore.t('nav.events'), to: '/events', icon: 'bi-calendar-event' },
          { label: localeStore.t('nav.announcements'), to: '/announcements', icon: 'bi-megaphone' },
          { label: localeStore.t('nav.policies'), to: '/policies', icon: 'bi-journal-text' },
        ].filter((item) => tenantStore.isModuleEnabled(item.to.slice(1))),
      })
      return sections
    }

    const workspaceItems: NavItem[] = []

    if (showSecretaryWorkspace.value) {
      workspaceItems.push({ label: localeStore.t('nav.secretaryWorkspace'), to: '/secretary', icon: 'bi-journal-richtext' })
    }
    if (showFinanceWorkspace.value) {
      workspaceItems.push({ label: localeStore.t('nav.financeWorkspace'), to: '/finance', icon: 'bi-cash-coin' })
    }
    if (showFinanceAuditWorkspace.value) {
      workspaceItems.push({ label: localeStore.t('nav.financeAudit'), to: '/finance-audit', icon: 'bi-clipboard-data' })
    }
    if (showGovernanceCockpit.value) {
      workspaceItems.push({ label: localeStore.t('nav.governanceCockpit'), to: '/governance', icon: 'bi-diagram-3' })
    }
    if (showCensorWorkspace.value) {
      workspaceItems.push({ label: localeStore.t('nav.disciplinaryConsole'), to: '/censor', icon: 'bi-shield-lock' })
    }
    if (showSportsWorkspace.value) {
      workspaceItems.push({ label: localeStore.t('nav.sportsWorkspace'), to: '/sports', icon: 'bi-trophy' })
    }
    if (isPrincipalAdmin.value || isAdmin.value) {
      workspaceItems.push({
        label: isPrincipalAdmin.value ? localeStore.t('nav.principalAdminPlane') : localeStore.t('nav.adminPlane'),
        to: '/admin',
        icon: 'bi-shield-lock',
      })
    }

    if (workspaceItems.length) {
      sections.push({
        label: localeStore.t('layout.workspaces'),
        items: workspaceItems,
      })
    }

    const communityItems: NavItem[] = [
      { label: localeStore.t('nav.events'), to: '/events', icon: 'bi-calendar-event' },
      { label: localeStore.t('nav.announcements'), to: '/announcements', icon: 'bi-megaphone' },
      { label: localeStore.t('nav.policies'), to: '/policies', icon: 'bi-journal-text' },
    ].filter((item) => tenantStore.isModuleEnabled(item.to.slice(1)))

    if (communityItems.length) {
      sections.push({
        label: localeStore.t('layout.community'),
        items: communityItems,
      })
    }

    return sections
  })

  const adminNavigation = computed<NavSection[]>(() => {
    const sections: NavSection[] = [
      {
        label: localeStore.t('layout.overview'),
        items: [
          { label: localeStore.t('nav.overview'), to: '/admin', icon: 'bi-speedometer2' },
          { label: localeStore.t('nav.onboardingWizard'), to: '/admin/onboarding', icon: 'bi-stars' },
          { label: localeStore.t('nav.healthCenter'), to: '/admin/health', icon: 'bi-heart-pulse' },
          { label: localeStore.t('nav.tenantOperations'), to: '/admin/tenants', icon: 'bi-diagram-3' },
        ],
      },
    ]

    const operations: NavItem[] = []
    if (tenantStore.isModuleEnabled('membership')) {
      operations.push({ label: localeStore.t('nav.members'), to: '/admin/members', icon: 'bi-people' })
    }
    if (tenantStore.isModuleEnabled('contributions')) {
      operations.push({ label: localeStore.t('nav.contributions'), to: '/admin/contributions', icon: 'bi-cash-stack' })
    }
    if (tenantStore.isModuleEnabled('policies')) {
      operations.push({ label: localeStore.t('nav.policies'), to: '/admin/policies', icon: 'bi-journal-text' })
    }
    if (tenantStore.isModuleEnabled('disciplinary')) {
      operations.push({ label: localeStore.t('nav.disciplinary'), to: '/admin/disciplinary', icon: 'bi-shield-lock' })
    }
    operations.push({ label: localeStore.t('nav.access'), to: '/admin/access', icon: 'bi-person-plus' })
    operations.push({ label: localeStore.t('nav.documents'), to: '/admin/documents', icon: 'bi-file-earmark-text' })

    if (operations.length) {
      sections.push({ label: localeStore.t('layout.operations'), items: operations })
    }

    const governance: NavItem[] = [{ label: localeStore.t('nav.auditTrail'), to: '/admin/audit', icon: 'bi-shield-check' }]
    if (tenantStore.isModuleEnabled('chat')) {
      governance.push({ label: localeStore.t('nav.chatAudit'), to: '/admin/chat-queries', icon: 'bi-journal-text' })
    }
    if (tenantStore.isModuleEnabled('events')) {
      governance.push({ label: localeStore.t('nav.events'), to: '/admin/events', icon: 'bi-calendar-event' })
    }
    if (tenantStore.isModuleEnabled('announcements')) {
      governance.push({ label: localeStore.t('nav.announcements'), to: '/admin/announcements', icon: 'bi-megaphone' })
    }
    if (tenantStore.isModuleEnabled('notifications')) {
      governance.push({ label: localeStore.t('nav.channels'), to: '/admin/notifications', icon: 'bi-broadcast-pin' })
    }

    sections.push({ label: localeStore.t('layout.governance'), items: governance })
    sections.push({ label: localeStore.t('layout.settings'), items: [{ label: localeStore.t('nav.settings'), to: '/admin/settings', icon: 'bi-gear' }] })

    return sections
  })

  const appHomeLabel = computed(() => {
    if (isMember.value) return localeStore.t('home.memberPortal')
    if (isSecretaryGeneral.value) return localeStore.t('home.secretaryWorkspace')
    if (isTreasurer.value) return localeStore.t('home.financeWorkspace')
    if (isAuditor.value) return localeStore.t('home.financeAudit')
    if (isCensor.value) return localeStore.t('home.disciplinaryConsole')
    if (isSportsManager.value) return localeStore.t('home.sportsWorkspace')
    if (showGovernanceCockpit.value) return localeStore.t('home.governanceCockpit')
    return isPrincipalAdmin.value ? localeStore.t('home.principalAdminPlane') : localeStore.t('home.organizationPortal')
  })

  const adminConsoleLabel = computed(() =>
    isPrincipalAdmin.value ? localeStore.t('layout.principalAdminConsole') : localeStore.t('layout.adminConsole'),
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
