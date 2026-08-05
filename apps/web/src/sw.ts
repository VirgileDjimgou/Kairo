/// <reference lib="webworker" />

import { clientsClaim } from 'workbox-core'
import { cleanupOutdatedCaches, precacheAndRoute } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { NetworkFirst } from 'workbox-strategies'

type PrecacheEntry = { url: string; revision?: string | null }

declare let self: ServiceWorkerGlobalScope & { __WB_MANIFEST: PrecacheEntry[] }

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

self.addEventListener('push', (event) => {
  const payload = event.data?.json() as { title?: string; body?: string; url?: string } | undefined
  const title = payload?.title ?? 'Kairo'
  const options: NotificationOptions = {
    body: payload?.body ?? 'Une nouvelle notification est disponible.',
    icon: '/pwa-192x192.png',
    badge: '/pwa-192x192.png',
    data: { url: payload?.url ?? '/dashboard' },
    tag: 'kairo-notification',
  }
  event.waitUntil(self.registration.showNotification(title, options))
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const url = String((event.notification.data as { url?: string } | undefined)?.url ?? '/dashboard')
  event.waitUntil((async () => {
    const windows = await self.clients.matchAll({ type: 'window', includeUncontrolled: true })
    const existing = windows[0]
    if (existing) {
      await existing.focus()
      existing.navigate(url)
      return
    }
    await self.clients.openWindow(url)
  })())
})
