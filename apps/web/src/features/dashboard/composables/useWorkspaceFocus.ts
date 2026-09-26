import { computed, type ComputedRef } from 'vue'
import { useLocaleStore } from '@/stores/locale.store'
import { useTenantStore } from '@/stores/tenant.store'
import type { DashboardRoleFlags } from './useDashboardRoles'

export interface WorkspaceFocusLink {
  label: string
  to: string
}

export interface WorkspaceFocus {
  kicker: string
  title: string
  description: string
  primary: WorkspaceFocusLink
  links: WorkspaceFocusLink[]
}

export function useWorkspaceFocus(roles: DashboardRoleFlags): ComputedRef<WorkspaceFocus> {
  const localeStore = useLocaleStore()
  const t = (key: string) => localeStore.t(key)
  const tenantStore = useTenantStore()

  return computed<WorkspaceFocus>(() => {
    if (roles.isPrincipalAdmin.value) {
      return {
        kicker: t('dashboard.focus.principalAdmin.kicker'),
        title: t('dashboard.focus.principalAdmin.title'),
        description:
          t('dashboard.focus.principalAdmin.description'),
        primary: { label: t('dashboard.focus.principalAdmin.primary'), to: '/admin/settings' },
        links: [
          { label: t('dashboard.focus.principalAdmin.link.tenants'), to: '/admin/tenants' },
          { label: t('dashboard.focus.principalAdmin.link.access'), to: '/admin/access' },
        ],
      }
    }

    if (roles.isMemberOnly.value) {
      return {
        kicker: t('dashboard.focus.member.kicker'),
        title: t('dashboard.focus.member.title'),
        description:
          t('dashboard.focus.member.description'),
        primary: { label: t('dashboard.focus.member.primary'), to: '/members/profile' },
        links: [
          { label: t('dashboard.focus.member.link.assistant'), to: '/chat' },
          { label: t('dashboard.focus.member.link.events'), to: '/events' },
        ],
      }
    }

    if (roles.isTreasurer.value) {
      return {
        kicker: t('dashboard.focus.treasurer.kicker'),
        title: t('dashboard.focus.treasurer.title'),
        description:
          t('dashboard.focus.treasurer.description'),
        primary: { label: t('dashboard.focus.treasurer.primary'), to: '/finance' },
        links: [
          { label: t('dashboard.focus.treasurer.link.memberProfile'), to: '/members/profile' },
          { label: t('dashboard.focus.treasurer.link.health'), to: '/admin/health' },
        ],
      }
    }

    if (roles.isSecretaryGeneral.value) {
      return {
        kicker: t('dashboard.focus.secretary.kicker'),
        title: t('dashboard.focus.secretary.title'),
        description:
          t('dashboard.focus.secretary.description'),
        primary: { label: t('dashboard.focus.secretary.primary'), to: '/secretary' },
        links: [
          { label: t('dashboard.focus.secretary.link.documents'), to: '/secretary/documents' },
          ...(tenantStore.isModuleEnabled('policies')
            ? [{ label: t('dashboard.focus.secretary.link.policies'), to: '/secretary/policies' }]
            : []),
          ...(tenantStore.isModuleEnabled('announcements')
            ? [{ label: t('dashboard.focus.secretary.link.announcements'), to: '/secretary/announcements' }]
            : []),
        ],
      }
    }

    if (roles.isAuditor.value) {
      return {
        kicker: t('dashboard.focus.auditor.kicker'),
        title: t('dashboard.focus.auditor.title'),
        description:
          t('dashboard.focus.auditor.description'),
        primary: { label: t('dashboard.focus.auditor.primary'), to: '/finance-audit' },
        links: [
          { label: t('dashboard.focus.auditor.link.policies'), to: '/policies' },
          { label: t('dashboard.focus.auditor.link.health'), to: '/admin/health' },
        ],
      }
    }

    if (roles.isCensor.value) {
      return {
        kicker: t('dashboard.focus.censor.kicker'),
        title: t('dashboard.focus.censor.title'),
        description:
          t('dashboard.focus.censor.description'),
        primary: { label: t('dashboard.focus.censor.primary'), to: '/censor' },
        links: [
          { label: t('dashboard.focus.censor.link.policies'), to: '/policies' },
          { label: t('dashboard.focus.censor.link.assistant'), to: '/chat' },
        ],
      }
    }

    if (roles.isSportsManager.value) {
      return {
        kicker: t('dashboard.focus.sports.kicker'),
        title: t('dashboard.focus.sports.title'),
        description:
          t('dashboard.focus.sports.description'),
        primary: { label: t('dashboard.focus.sports.primary'), to: '/sports' },
        links: [
          { label: t('dashboard.focus.sports.link.events'), to: '/events' },
          { label: t('dashboard.focus.sports.link.assistant'), to: '/chat' },
        ],
      }
    }

    if (roles.isPresidentRole.value || roles.isVicePresidentRole.value) {
      return {
        kicker: t('dashboard.focus.executive.kicker'),
        title: t('dashboard.focus.executive.title'),
        description:
          t('dashboard.focus.executive.description'),
        primary: { label: t('dashboard.focus.executive.primary'), to: '/governance' },
        links: [
          { label: t('dashboard.focus.executive.link.financeAudit'), to: '/finance-audit' },
          { label: t('dashboard.focus.executive.link.announcements'), to: '/announcements' },
        ],
      }
    }

    return {
      kicker: t('dashboard.focus.fallback.kicker'),
      title: t('dashboard.focus.fallback.title'),
      description:
        t('dashboard.focus.fallback.description'),
      primary: { label: t('dashboard.focus.fallback.primary'), to: '/dashboard' },
      links: [
        { label: t('dashboard.focus.fallback.link.settings'), to: '/admin/settings' },
        { label: t('dashboard.focus.fallback.link.assistant'), to: '/chat' },
      ],
    }
  })
}
