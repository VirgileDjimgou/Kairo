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
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
