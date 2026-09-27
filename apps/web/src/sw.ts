/// <reference lib="webworker" />

import { clientsClaim } from 'workbox-core'
import { cleanupOutdatedCaches, precacheAndRoute } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { NetworkFirst } from 'workbox-strategies'

type PrecacheEntry = { url: string; revision?: string | null }
type PushPayload = { title?: string; body?: string; url?: string }

declare let self: ServiceWorkerGlobalScope & { __WB_MANIFEST: PrecacheEntry[] }

const DEFAULT_TARGET = '/dashboard'

self.skipWaiting()
clientsClaim()
// Never precache the HTML shell. A cache-first index.html can keep an old
// JavaScript bundle alive indefinitely and, in turn, preserve obsolete API URLs.
precacheAndRoute(self.__WB_MANIFEST.filter((entry) => typeof entry === 'string' || entry.url !== 'index.html'))
cleanupOutdatedCaches()

// Navigations are network-first so deployments immediately use the current
// HTML entrypoint. The cached response remains only as an offline fallback.
registerRoute(
  ({ request }) => request.mode === 'navigate',
  new NetworkFirst({ cacheName: 'kairo-pages', networkTimeoutSeconds: 5 }),
)

// Notification targets are backend-owned safe internal paths. Anything that is
// not a same-origin absolute path falls back to the dashboard so a payload can
// never navigate the PWA to an external URL.
function safeTarget(raw: unknown): string {
  if (typeof raw !== 'string' || !raw.startsWith('/') || raw.startsWith('//')) return DEFAULT_TARGET
  try {
    const resolved = new URL(raw, self.location.origin)
    if (resolved.origin !== self.location.origin) return DEFAULT_TARGET
    return `${resolved.pathname}${resolved.search}`
  } catch {
    return DEFAULT_TARGET
  }
}

self.addEventListener('push', (event) => {
  let payload: PushPayload | undefined
  try {
    payload = event.data?.json() as PushPayload | undefined
  } catch {
    payload = undefined
  }
  const options: NotificationOptions = {
    body: payload?.body ?? 'Une nouvelle notification est disponible.',
    icon: '/pwa-192x192.png',
    badge: '/pwa-192x192.png',
    data: { url: safeTarget(payload?.url) },
    tag: 'kairo-notification',
  }
  event.waitUntil(self.registration.showNotification(payload?.title ?? 'Kairo', options))
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const url = safeTarget((event.notification.data as { url?: string } | undefined)?.url)
  event.waitUntil((async () => {
    const windows = await self.clients.matchAll({ type: 'window', includeUncontrolled: true })
    const existing = windows[0]
    if (existing) {
      await existing.focus()
      await existing.navigate(url)
      return
    }
    await self.clients.openWindow(url)
  })())
})

// The browser can rotate or expire a subscription while the page is closed.
// Tell open clients so the authenticated page re-registers a fresh one.
self.addEventListener('pushsubscriptionchange', (event) => {
  event.waitUntil((async () => {
    const windows = await self.clients.matchAll({ type: 'window', includeUncontrolled: true })
    for (const client of windows) {
      client.postMessage({ type: 'kairo:push-subscription-changed' })
    }
  })())
})
