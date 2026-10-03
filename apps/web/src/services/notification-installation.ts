import {
  registerNotificationDevice,
  saveMobilePushToken,
  savePushSubscription,
} from '@/api/notifications.api'
import { firebaseVapidKey, firebaseWebConfig } from '@/firebase-config'

const installationKey = 'kairo_notification_installation_id'
const providerKey = 'kairo_notification_provider'
const REGISTRATION_RETRY_ATTEMPTS = 3
const REGISTRATION_RETRY_BASE_MS = 400

export type PushProvider = 'web_push' | 'firebase'

export interface InstallationMetadata {
  installation_id: string
  platform: string
  browser: string
  device_metadata: Record<string, string>
}

export function currentInstallationId(): string {
  const existing = localStorage.getItem(installationKey)
  if (existing) return existing
  const created = crypto.randomUUID()
  localStorage.setItem(installationKey, created)
  return created
}

export function pushSupported(): boolean {
  return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window
}

export async function getServiceWorkerRegistration(): Promise<ServiceWorkerRegistration> {
  const registration = await navigator.serviceWorker.getRegistration('/')
    ?? await navigator.serviceWorker.register('/sw.js', { scope: '/' })

  if (registration.active) return registration
  return navigator.serviceWorker.ready
}

export function detectBrowser(userAgent: string): string {
  if (/Edg\//.test(userAgent)) return 'Edge'
  if (/OPR\//.test(userAgent)) return 'Opera'
  if (/Firefox\//.test(userAgent)) return 'Firefox'
  if (/Chrome\//.test(userAgent)) return 'Chrome'
  if (/Safari\//.test(userAgent)) return 'Safari'
  return 'Unknown'
}

export function installationMetadata(): InstallationMetadata {
  const standalone =
    window.matchMedia('(display-mode: standalone)').matches
    || (navigator as Navigator & { standalone?: boolean }).standalone === true
  return {
    installation_id: currentInstallationId(),
    platform: navigator.platform || 'web',
    browser: detectBrowser(navigator.userAgent),
    device_metadata: {
      language: navigator.language,
      display_mode: standalone ? 'standalone' : 'browser',
      screen: `${window.screen.width}x${window.screen.height}`,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
    },
  }
}

export function selectedProvider(): PushProvider | null {
  const value = localStorage.getItem(providerKey)
  return value === 'web_push' || value === 'firebase' ? value : null
}

export function rememberProvider(provider: PushProvider): void {
  localStorage.setItem(providerKey, provider)
}

function emitRegistrationTelemetry(label: string, outcome: 'recovered' | 'failed', attempts: number): void {
  window.dispatchEvent(new CustomEvent('kairo:notification-registration-telemetry', {
    detail: { label, outcome, attempts },
  }))
  if (outcome === 'failed') {
    console.warn(`Kairo notification registration failed (${label}) after ${attempts} attempts`)
  }
}

/**
 * Bounded retry for registration requests. Transient network or API failures
 * are retried with backoff; the final failure emits a telemetry event instead
 * of silently dropping the push binding.
 */
export async function withRegistrationRetry<T>(operation: () => Promise<T>, label: string): Promise<T> {
  let lastError: unknown
  for (let attempt = 1; attempt <= REGISTRATION_RETRY_ATTEMPTS; attempt += 1) {
    try {
      const result = await operation()
      if (attempt > 1) emitRegistrationTelemetry(label, 'recovered', attempt)
      return result
    } catch (error) {
      lastError = error
      if (attempt < REGISTRATION_RETRY_ATTEMPTS) {
        await new Promise((resolve) => window.setTimeout(resolve, REGISTRATION_RETRY_BASE_MS * 2 ** (attempt - 1)))
      }
    }
  }
  emitRegistrationTelemetry(label, 'failed', REGISTRATION_RETRY_ATTEMPTS)
  throw lastError
}

export async function registerCurrentDevice(): Promise<void> {
  const metadata = installationMetadata()
  await withRegistrationRetry(() => registerNotificationDevice({
    installation_id: metadata.installation_id,
    platform: metadata.platform,
    browser: metadata.browser,
    device_metadata: metadata.device_metadata,
  }), 'device')
}

export async function persistWebPushSubscription(subscription: PushSubscription): Promise<void> {
  const keys = subscription.toJSON().keys
  const p256dh = keys?.p256dh
  const auth = keys?.auth
  if (!p256dh || !auth) throw new Error('Push subscription keys are unavailable')
  const metadata = installationMetadata()
  await withRegistrationRetry(() => savePushSubscription({
    installation_id: metadata.installation_id,
    platform: metadata.platform,
    browser: metadata.browser,
    device_metadata: metadata.device_metadata,
    endpoint: subscription.endpoint,
    p256dh,
    auth,
  }), 'web_push')
  rememberProvider('web_push')
}

/**
 * Firebase Web Messaging registration. The token is bound to the canonical
 * Service Worker registration so FCM background messages use the same worker
 * as VAPID Web Push. The backend remains the only recipient authority; FCM
 * topics are never used.
 */
export async function registerFirebaseWebToken(): Promise<void> {
  const config = firebaseWebConfig()
  if (!config) throw new Error('Firebase web messaging is not configured')
  const [{ getApps, initializeApp }, { getMessaging, getToken, isSupported }] = await Promise.all([
    import('firebase/app'),
    import('firebase/messaging'),
  ])
  if (!(await isSupported())) throw new Error('Firebase messaging is not supported in this browser')
  const app = getApps()[0] ?? initializeApp(config)
  const registration = await getServiceWorkerRegistration()
  const vapidKey = firebaseVapidKey()
  const token = await getToken(getMessaging(app), {
    serviceWorkerRegistration: registration,
    ...(vapidKey ? { vapidKey } : {}),
  })
  if (!token) throw new Error('Firebase did not return a registration token')
  const metadata = installationMetadata()
  await withRegistrationRetry(() => saveMobilePushToken({
    installation_id: metadata.installation_id,
    platform: metadata.platform,
    browser: metadata.browser,
    device_metadata: metadata.device_metadata,
    fcm_token: token,
  }), 'firebase')
  rememberProvider('firebase')
}

/**
 * Re-persists the existing binding for this installation on the current
 * session/tenant. Called on tenant switch and application start so a binding
 * revoked by sign-out or a previous tenant is re-enabled without asking the
 * user for permission again. It is a no-op when push was never enabled.
 */
export async function renewPushBinding(): Promise<void> {
  if (!pushSupported() || Notification.permission !== 'granted') return
  if (selectedProvider() === 'firebase') {
    if (!firebaseWebConfig()) return
    await registerFirebaseWebToken().catch(() => undefined)
    return
  }
  const registration = await navigator.serviceWorker.getRegistration('/')
  const subscription = await registration?.pushManager.getSubscription()
  if (!subscription) return
  await persistWebPushSubscription(subscription).catch(() => undefined)
}
