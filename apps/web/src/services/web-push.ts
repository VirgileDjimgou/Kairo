import { getPushConfiguration, revokeNotificationDevice } from '@/api/notifications.api'
import { firebaseWebConfig } from '@/firebase-config'
import {
  currentInstallationId,
  getServiceWorkerRegistration,
  persistWebPushSubscription,
  pushSupported,
  registerCurrentDevice,
  registerFirebaseWebToken,
  renewPushBinding,
} from '@/services/notification-installation'

export { currentInstallationId, registerCurrentDevice, renewPushBinding }

function base64UrlToArrayBuffer(value: string): ArrayBuffer {
  const padded = `${value}${'='.repeat((4 - (value.length % 4)) % 4)}`.replace(/-/g, '+').replace(/_/g, '/')
  const decoded = atob(padded)
  const bytes = Uint8Array.from(decoded, (character) => character.charCodeAt(0))
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer
}

/**
 * Explicit notification enablement. Permission is only requested here, never
 * on first visit. VAPID Web Push is the standards-based browser transport and
 * stays the default; Firebase Web Messaging is used when VAPID is not
 * configured but Firebase is, so one installation always has exactly one
 * delivery provider.
 */
export async function enablePushForCurrentProfile(): Promise<'enabled' | 'unavailable' | 'not_configured' | 'denied'> {
  if (!pushSupported()) return 'unavailable'
  const config = await getPushConfiguration()
  const permission = await Notification.requestPermission()
  if (permission !== 'granted') return 'denied'

  if (config.enabled && config.public_key) {
    const registration = await getServiceWorkerRegistration()
    // Reuse an existing subscription; browsers reject a second subscribe with a
    // different key and the subscription may have been rotated while offline.
    const existing = await registration.pushManager.getSubscription()
    const subscription = existing ?? await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: base64UrlToArrayBuffer(config.public_key),
    })
    await persistWebPushSubscription(subscription)
    return 'enabled'
  }

  if (firebaseWebConfig()) {
    try {
      await registerFirebaseWebToken()
      return 'enabled'
    } catch {
      return 'not_configured'
    }
  }

  return 'not_configured'
}

export async function reRegisterRotatedSubscription(): Promise<void> {
  if (!pushSupported()) return
  const registration = await getServiceWorkerRegistration()
  const subscription = await registration.pushManager.getSubscription()
  if (!subscription) return
  await persistWebPushSubscription(subscription)
}

export async function hasActivePushSubscription(): Promise<boolean> {
  if (!pushSupported()) return false
  try {
    const registration = await navigator.serviceWorker.getRegistration('/')
    const subscription = await registration?.pushManager.getSubscription()
    return Boolean(subscription)
  } catch {
    return false
  }
}

/**
 * Revoke this browser's push binding for the signed-in profile. The device
 * identity and provider choice are kept so a later sign-in can re-enable
 * delivery.
 */
export async function revokeCurrentDevice(): Promise<void> {
  await revokeNotificationDevice(currentInstallationId())
}

export function watchPushSubscriptionRotation(): void {
  if (!('serviceWorker' in navigator)) return
  navigator.serviceWorker.addEventListener('message', (event) => {
    if ((event.data as { type?: string } | undefined)?.type !== 'kairo:push-subscription-changed') return
    void reRegisterRotatedSubscription().catch(() => undefined)
  })
}
