import { computed, type ComputedRef } from 'vue'
import { useLocaleStore } from '@/stores/locale.store'
import { useTenantStore } from '@/stores/tenant.store'
import type { DashboardRoleFlags } from './useDashboardRoles'

export interface DashboardQuickAction {
  label: string
  to: string
  icon: string
}

export function useDashboardQuickActions(roles: DashboardRoleFlags): {
  quickActions: ComputedRef<DashboardQuickAction[]>
  filteredQuickActions: ComputedRef<DashboardQuickAction[]>
} {
  const localeStore = useLocaleStore()
  const t = (key: string) => localeStore.t(key)
  const tenantStore = useTenantStore()

  const quickActions = computed(() => {
    const actions: Array<{ label: string; to: string; icon: string }> = []

    if (roles.isMemberOnly.value) {
      actions.push({ label: t('dashboard.action.profile'), to: '/members/profile', icon: 'bi bi-person-badge' })
      if (tenantStore.isModuleEnabled('chat')) {
        actions.push({ label: t('dashboard.action.assistant'), to: '/chat', icon: 'bi bi-chat-dots' })
      }
      if (tenantStore.isModuleEnabled('events')) {
        actions.push({ label: t('dashboard.action.events'), to: '/events', icon: 'bi bi-calendar-event' })
      }
      if (tenantStore.isModuleEnabled('announcements')) {
        actions.push({ label: t('dashboard.action.announcements'), to: '/announcements', icon: 'bi bi-megaphone' })
      }
    } else if (roles.isAdmin.value || roles.isPrincipalAdmin.value) {
      actions.push({
        label:
          roles.isPrincipalAdmin.value
            ? (t('dashboard.action.adminControlPlane'))
            : (t('dashboard.action.tenantSettings')),
        to: '/admin/settings',
        icon: 'bi bi-sliders',
      })
      actions.push({ label: t('dashboard.action.onboardingWizard'), to: '/admin/onboarding', icon: 'bi bi-stars' })
      actions.push({ label: t('dashboard.action.uploadDocuments'), to: '/admin/documents', icon: 'bi bi-file-earmark-text' })
      if (tenantStore.isModuleEnabled('membership')) {
        actions.push({ label: t('dashboard.action.importMembers'), to: '/admin/members', icon: 'bi bi-people' })
      }
    } else if (roles.isTreasurer.value) {
      actions.push({ label: t('dashboard.action.financeWorkspace'), to: '/finance', icon: 'bi bi-cash-coin' })
      if (tenantStore.isModuleEnabled('membership')) {
        actions.push({ label: t('dashboard.action.memberProfile'), to: '/members/profile', icon: 'bi bi-person-badge' })
      }
    } else if (roles.isSecretaryGeneral.value) {
      actions.push({ label: t('dashboard.action.secretaryWorkspace'), to: '/secretary', icon: 'bi bi-journal-richtext' })
      actions.push({ label: t('dashboard.action.documents'), to: '/secretary/documents', icon: 'bi bi-file-earmark-text' })
      if (tenantStore.isModuleEnabled('policies')) {
        actions.push({ label: t('dashboard.action.policies'), to: '/secretary/policies', icon: 'bi bi-journal-text' })
      }
      if (tenantStore.isModuleEnabled('announcements')) {
        actions.push({ label: t('dashboard.action.secretaryAnnouncements'), to: '/secretary/announcements', icon: 'bi bi-megaphone' })
      }
    } else if (roles.isAuditor.value || roles.isPresident.value) {
      actions.push({ label: t('dashboard.action.financeAudit'), to: '/finance-audit', icon: 'bi bi-clipboard-data' })
      if (tenantStore.isModuleEnabled('policies')) {
        actions.push({ label: t('dashboard.action.policies'), to: '/policies', icon: 'bi bi-journal-text' })
      }
    }

    if (roles.canOpenHealthCenter.value) {
      actions.push({
        label: t('dashboard.action.health'),
        to: '/admin/health',
        icon: 'bi bi-heart-pulse',
      })
    }

    if (tenantStore.isModuleEnabled('disciplinary') && (roles.isCensor.value || roles.isPresident.value || roles.isPrincipalAdmin.value || roles.isAdmin.value)) {
      actions.push({
        label: roles.isCensor.value
          ? (t('dashboard.action.disciplineManage'))
          : (t('dashboard.action.disciplineOversight')),
        to: '/censor',
        icon: 'bi bi-shield-lock',
      })
    }

    if (tenantStore.isModuleEnabled('announcements')) {
      actions.push({
        label: roles.isAdmin.value || roles.isPrincipalAdmin.value || roles.isSecretaryGeneral.value ? (t('dashboard.action.publishAnnouncement')) : (t('dashboard.action.reviewAnnouncements')),
        to: roles.isAdmin.value || roles.isPrincipalAdmin.value ? '/admin/announcements' : roles.isSecretaryGeneral.value ? '/secretary/announcements' : '/announcements',
        icon: 'bi bi-megaphone',
      })
    }

    if (tenantStore.isModuleEnabled('events')) {
      if (roles.isSportsManager.value || roles.isPrincipalAdmin.value || roles.isAdmin.value) {
        actions.push({
          label: t('dashboard.action.sportsWorkspace'),
          to: '/sports',
          icon: 'bi bi-trophy',
        })
      }
      actions.push({
        label: roles.isAdmin.value || roles.isPrincipalAdmin.value ? (t('dashboard.action.scheduleEvent')) : (t('dashboard.action.events')),
        to: roles.isAdmin.value || roles.isPrincipalAdmin.value ? '/admin/events' : '/events',
        icon: 'bi bi-calendar-event',
      })
    }

    if (roles.isPresidentRole.value || roles.isVicePresidentRole.value || roles.isPrincipalAdmin.value || roles.isAdmin.value) {
      actions.push({
        label: t('dashboard.action.governance'),
        to: '/governance',
        icon: 'bi bi-diagram-3',
      })
    }

    return actions
  })

  const filteredQuickActions = computed(() =>
    quickActions.value.filter((action, index, source) => source.findIndex((item) => item.to === action.to) === index),
  )

  return { quickActions, filteredQuickActions }
}
