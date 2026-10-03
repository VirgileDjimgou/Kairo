import type { Router } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { useTenantStore } from '@/stores/tenant.store'

export const PWA_NAVIGATE_MESSAGE = 'kairo:navigate'
export const NOTIFICATION_INBOX_TARGET = '/notifications'

/**
 * Notification targets are backend-owned safe internal paths. The client
 * accepts only same-origin absolute paths, so a notification payload can never
 * navigate the PWA to an external URL. This is navigation safety only:
 * authentication, tenant and capability checks still run in the router guards
 * and the backend.
 */
export function safeInternalTarget(raw: unknown): string | null {
  if (typeof raw !== 'string') return null
  const value = raw.trim()
  if (!value.startsWith('/') || value.startsWith('//')) return null
  try {
    const resolved = new URL(value, window.location.origin)
    if (resolved.origin !== window.location.origin) return null
    return `${resolved.pathname}${resolved.search}`
  } catch {
    return null
  }
}

/**
 * Resolves a notification target against the actual router and the current
 * authentication/tenant state. An unsafe, unknown or inaccessible target falls
 * back to the authenticated notification inbox instead of the dashboard, so a
 * stale or forbidden deep link can never dump the user on an unrelated page.
 */
export function resolveNotificationTarget(router: Router, raw: unknown): string {
  const candidate = safeInternalTarget(raw)
  if (!candidate) return NOTIFICATION_INBOX_TARGET
  try {
    const resolved = router.resolve(candidate)
    if (!resolved.matched.length || resolved.redirectedFrom) return NOTIFICATION_INBOX_TARGET
    // A redirect record (for example the catch-all route) resolves to a
    // different path; treat that as an unknown target.
    const record = resolved.matched[resolved.matched.length - 1]
    if (record?.redirect || resolved.path !== candidate.split('?')[0]) return NOTIFICATION_INBOX_TARGET

    const auth = useAuthStore()
    if (!auth.isAuthenticated) return candidate

    const tenant = useTenantStore()
    const roles = auth.user?.roles ?? []
    const meta = resolved.meta as {
      allowedRoles?: string[]
      requiresFinanceWorkspace?: boolean
      module?: string
    }

    if (
      resolved.path.startsWith('/admin')
      && resolved.name !== 'admin-health-center'
      && !roles.some((role) => ['admin', 'principal_admin'].includes(role))
    ) {
      return NOTIFICATION_INBOX_TARGET
    }
    if (meta.allowedRoles && !meta.allowedRoles.some((role) => roles.includes(role))) {
      return NOTIFICATION_INBOX_TARGET
    }
    if (
      meta.requiresFinanceWorkspace
      && !['admin', 'treasurer', 'principal_admin'].some((role) => roles.includes(role))
    ) {
      return NOTIFICATION_INBOX_TARGET
    }
    if (
      meta.requiresFinanceWorkspace
      && (!tenant.isModuleEnabled('membership') || !tenant.isModuleEnabled('contributions'))
    ) {
      return NOTIFICATION_INBOX_TARGET
    }
    if (meta.module && !tenant.isModuleEnabled(meta.module)) {
      return NOTIFICATION_INBOX_TARGET
    }
    return candidate
  } catch {
    return NOTIFICATION_INBOX_TARGET
  }
}

/**
 * SERVICE WORKER -> NAVIGATE(targetPath) -> VUE ROUTER contract.
 *
 * The canonical Service Worker focuses an existing client and posts a
 * navigation message instead of forcing a full page reload. The router guard
 * then either opens the exact authorized target or sends an unauthenticated
 * visitor to `/login?redirect=<target>` so the destination survives sign-in.
 */
export function installNotificationNavigation(router: Router): void {
  if (!('serviceWorker' in navigator)) return
  navigator.serviceWorker.addEventListener('message', (event: MessageEvent) => {
    const data = event.data as { type?: string; target?: unknown } | undefined
    if (data?.type !== PWA_NAVIGATE_MESSAGE) return
    const target = resolveNotificationTarget(router, data.target)
    if (router.currentRoute.value.fullPath === target) return
    void router.push(target)
  })
}
