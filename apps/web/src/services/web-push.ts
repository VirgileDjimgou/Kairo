import {
  getPushConfiguration,
  registerNotificationDevice,
  revokeNotificationDevice,
  savePushSubscription,
} from '@/api/notifications.api'

const installationKey = 'kairo_notification_installation_id'

export function currentInstallationId(): string {
  const existing = localStorage.getItem(installationKey)
  if (existing) return existing
  const created = crypto.randomUUID()
  localStorage.setItem(installationKey, created)
  return created
}

function base64UrlToArrayBuffer(value: string): ArrayBuffer {
  const padded = `${value}${'='.repeat((4 - (value.length % 4)) % 4)}`.replace(/-/g, '+').replace(/_/g, '/')
  const decoded = atob(padded)
  const bytes = Uint8Array.from(decoded, (character) => character.charCodeAt(0))
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer
}

export function pushSupported(): boolean {
  return 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window
}

async function getServiceWorkerRegistration(): Promise<ServiceWorkerRegistration> {
  const registration = await navigator.serviceWorker.getRegistration('/')
    ?? await navigator.serviceWorker.register('/sw.js', { scope: '/' })

  if (registration.active) return registration
  return navigator.serviceWorker.ready
}

async function persistSubscription(subscription: PushSubscription): Promise<void> {
  const keys = subscription.toJSON().keys
  if (!keys?.p256dh || !keys.auth) throw new Error('Push subscription keys are unavailable')
  await savePushSubscription({
    installation_id: currentInstallationId(),
    platform: navigator.platform,
    endpoint: subscription.endpoint,
    p256dh: keys.p256dh,
    auth: keys.auth,
  })
}

export async function registerCurrentDevice(): Promise<void> {
  await registerNotificationDevice({ installation_id: currentInstallationId(), platform: navigator.platform })
}

export async function enablePushForCurrentProfile(): Promise<'enabled' | 'unavailable' | 'not_configured' | 'denied'> {
  if (!pushSupported()) return 'unavailable'
  const config = await getPushConfiguration()
  if (!config.enabled || !config.public_key) return 'not_configured'
  const permission = await Notification.requestPermission()
  if (permission !== 'granted') return 'denied'
  const registration = await getServiceWorkerRegistration()
  // Reuse an existing subscription; browsers reject a second subscribe with a
  // different key and the subscription may have been rotated while offline.
  const existing = await registration.pushManager.getSubscription()
  const subscription = existing ?? await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: base64UrlToArrayBuffer(config.public_key),
  })
  await persistSubscription(subscription)
  return 'enabled'
}

export async function reRegisterRotatedSubscription(): Promise<void> {
  if (!pushSupported()) return
  const registration = await getServiceWorkerRegistration()
  const subscription = await registration.pushManager.getSubscription()
  if (!subscription) return
  await persistSubscription(subscription)
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
 * identity is kept so a later sign-in can re-enable delivery.
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
