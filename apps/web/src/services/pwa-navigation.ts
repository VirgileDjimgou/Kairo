import type { Router } from 'vue-router'

export const PWA_NAVIGATE_MESSAGE = 'kairo:navigate'

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
    const target = safeInternalTarget(data.target)
    if (!target) return
    if (router.currentRoute.value.fullPath === target) return
    void router.push(target)
  })
}
