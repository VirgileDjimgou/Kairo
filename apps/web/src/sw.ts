/// <reference lib="webworker" />

import { clientsClaim } from 'workbox-core'
import { cleanupOutdatedCaches, precacheAndRoute } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { NetworkFirst } from 'workbox-strategies'
import { getApps, initializeApp } from 'firebase/app'
import { getMessaging, isSupported as messagingIsSupported, onBackgroundMessage } from 'firebase/messaging/sw'
import type { MessagePayload } from 'firebase/messaging/sw'
import { firebaseWebConfig } from './firebase-config'

type PrecacheEntry = { url: string; revision?: string | null }
type PushPayload = { title?: string; body?: string; url?: string }

declare let self: ServiceWorkerGlobalScope & { __WB_MANIFEST: PrecacheEntry[] }

const DEFAULT_TARGET = '/notifications'
const PWA_NAVIGATE_MESSAGE = 'kairo:navigate'
const GENERIC_TITLE = 'Kairo'
const GENERIC_BODY = 'Une nouvelle notification est disponible.'

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

function showNotification(title: string, body: string, target: unknown): Promise<void> {
  const options: NotificationOptions = {
    body,
    icon: '/pwa-192x192.png',
    badge: '/pwa-192x192.png',
    data: { url: safeTarget(target) },
    tag: 'kairo-notification',
  }
  return self.registration.showNotification(title, options)
}

// FCM messages are delivered as push events with a Firebase-specific shape.
// They are handled by the Firebase background handler below; the standards-based
// Web Push handler must not display them a second time.
function isFirebaseMessage(payload: unknown): boolean {
  if (!payload || typeof payload !== 'object') return false
  const candidate = payload as Record<string, unknown>
  return (
    typeof candidate.from === 'string' ||
    'messageId' in candidate ||
    'fcmMessageId' in candidate
  )
}

let firebaseReady = false

async function setupFirebaseBackgroundMessaging(): Promise<void> {
  const config = firebaseWebConfig()
  if (!config) return
  try {
    if (!(await messagingIsSupported())) return
    const app = getApps()[0] ?? initializeApp(config)
    const messaging = getMessaging(app)
    onBackgroundMessage(messaging, (payload: MessagePayload) => {
      const target = payload.data?.target_path ?? payload.data?.url
      return showNotification(
        payload.notification?.title ?? GENERIC_TITLE,
        payload.notification?.body ?? GENERIC_BODY,
        target,
      )
    })
    firebaseReady = true
  } catch {
    // FCM stays disabled; standards-based Web Push keeps working.
  }
}

void setupFirebaseBackgroundMessaging()

// Standard Web Push (VAPID) from the Kairo notification outbox.
self.addEventListener('push', (event) => {
  let payload: unknown
  try {
    payload = event.data?.json()
  } catch {
    payload = undefined
  }
  if (firebaseReady && isFirebaseMessage(payload)) return
  const typed = (payload ?? {}) as PushPayload
  event.waitUntil(showNotification(typed.title ?? GENERIC_TITLE, typed.body ?? GENERIC_BODY, typed.url))
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const url = safeTarget((event.notification.data as { url?: string } | undefined)?.url)
  event.waitUntil((async () => {
    const windows = await self.clients.matchAll({ type: 'window', includeUncontrolled: true })
    const existing = windows[0]
    if (existing) {
      await existing.focus()
      // SERVICE WORKER -> NAVIGATE(targetPath) -> VUE ROUTER. The client
      // navigates in-app; it never reloads through the dashboard.
      existing.postMessage({ type: PWA_NAVIGATE_MESSAGE, target: url })
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
