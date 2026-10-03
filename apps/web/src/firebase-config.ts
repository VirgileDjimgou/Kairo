import type { FirebaseOptions } from 'firebase/app'

/**
 * Firebase Web SDK configuration for the canonical Kairo Service Worker.
 *
 * Firebase Web configuration values are public client identifiers, not secrets.
 * They are injected at build time through `VITE_FIREBASE_*` variables. When any
 * required value is missing, FCM background handling stays disabled and the
 * worker keeps serving standards-based Web Push (VAPID) only.
 */
export function firebaseWebConfig(): FirebaseOptions | null {
  const env = import.meta.env
  const apiKey = env.VITE_FIREBASE_API_KEY?.trim()
  const projectId = env.VITE_FIREBASE_PROJECT_ID?.trim()
  const messagingSenderId = env.VITE_FIREBASE_MESSAGING_SENDER_ID?.trim()
  const appId = env.VITE_FIREBASE_APP_ID?.trim()
  if (!apiKey || !projectId || !messagingSenderId || !appId) return null

  const authDomain = env.VITE_FIREBASE_AUTH_DOMAIN?.trim()
  const storageBucket = env.VITE_FIREBASE_STORAGE_BUCKET?.trim()
  return {
    apiKey,
    projectId,
    messagingSenderId,
    appId,
    ...(authDomain ? { authDomain } : {}),
    ...(storageBucket ? { storageBucket } : {}),
  }
}

/**
 * Optional Firebase Web Push certificate key used by `getToken`. When absent,
 * the browser uses the project's default Web Push certificate.
 */
export function firebaseVapidKey(): string | null {
  const value = import.meta.env.VITE_FIREBASE_VAPID_KEY?.trim()
  return value || null
}
