/// <reference types="vite/client" />
/// <reference types="vite-plugin-pwa/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_NAME: string
  /** "false" disables the public portfolio demo entry point. */
  readonly VITE_DEMO_MODE?: string
  /** Tenant slug used by one-click demo sessions. */
  readonly VITE_DEMO_TENANT_SLUG?: string
  /** JSON array overriding the demo account catalogue. */
  readonly VITE_DEMO_ACCOUNTS?: string
  /** Base64-encoded JSON array overriding the demo account catalogue. */
  readonly VITE_DEMO_ACCOUNTS_B64?: string
  /** Firebase Web SDK configuration for FCM background messages (public client identifiers). */
  readonly VITE_FIREBASE_API_KEY?: string
  readonly VITE_FIREBASE_PROJECT_ID?: string
  readonly VITE_FIREBASE_MESSAGING_SENDER_ID?: string
  readonly VITE_FIREBASE_APP_ID?: string
  readonly VITE_FIREBASE_AUTH_DOMAIN?: string
  readonly VITE_FIREBASE_STORAGE_BUCKET?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
