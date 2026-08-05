import { getPushConfiguration, registerNotificationDevice, savePushSubscription } from '@/api/notifications.api'

const installationKey = 'kairo_notification_installation_id'

function installationId(): string {
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

export async function registerCurrentDevice(): Promise<void> {
  await registerNotificationDevice({ installation_id: installationId(), platform: navigator.platform })
}

export async function enablePushForCurrentProfile(): Promise<'enabled' | 'unavailable' | 'not_configured' | 'denied'> {
  if (!pushSupported()) return 'unavailable'
  const config = await getPushConfiguration()
  if (!config.enabled || !config.public_key) return 'not_configured'
  const permission = await Notification.requestPermission()
  if (permission !== 'granted') return 'denied'
  const registration = await getServiceWorkerRegistration()
  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: base64UrlToArrayBuffer(config.public_key),
  })
  const keys = subscription.toJSON().keys
  if (!keys?.p256dh || !keys.auth) throw new Error('Push subscription keys are unavailable')
  await savePushSubscription({
    installation_id: installationId(),
    platform: navigator.platform,
    endpoint: subscription.endpoint,
    p256dh: keys.p256dh,
    auth: keys.auth,
  })
  return 'enabled'
}
