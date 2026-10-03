import { ref } from 'vue'

const INSTALL_DISMISSED_KEY = 'kairo_install_prompt_dismissed'
const INSTALLED_KEY = 'kairo_app_installed'

interface BeforeInstallPromptEvent extends Event {
  prompt: () => Promise<void>
  userChoice?: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

const installEvent = ref<BeforeInstallPromptEvent | null>(null)
const installed = ref(false)
let initialized = false

export function isStandalone(): boolean {
  return (
    window.matchMedia('(display-mode: standalone)').matches
    || (navigator as Navigator & { standalone?: boolean }).standalone === true
  )
}

export function isInstalled(): boolean {
  return installed.value || isStandalone() || localStorage.getItem(INSTALLED_KEY) === '1'
}

export function installPromptDismissed(): boolean {
  return localStorage.getItem(INSTALL_DISMISSED_KEY) === '1'
}

export function installPromptAvailable(): boolean {
  return installEvent.value !== null && !isInstalled() && !installPromptDismissed()
}

export function dismissInstallPrompt(): void {
  localStorage.setItem(INSTALL_DISMISSED_KEY, '1')
  installEvent.value = null
}

/**
 * Captures the browser install prompt and completion events. It never requests
 * notification permission: installation and notifications are separate,
 * explicit user decisions.
 */
export function initializeInstallPrompt(): void {
  if (initialized) return
  initialized = true
  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault()
    installEvent.value = event as BeforeInstallPromptEvent
  })
  window.addEventListener('appinstalled', () => {
    installed.value = true
    localStorage.setItem(INSTALLED_KEY, '1')
    installEvent.value = null
    window.dispatchEvent(new CustomEvent('kairo:app-installed'))
  })
}

export async function promptInstall(): Promise<'accepted' | 'dismissed' | 'unavailable'> {
  const event = installEvent.value
  if (!event) return 'unavailable'
  await event.prompt()
  const choice = await event.userChoice?.catch(() => undefined)
  installEvent.value = null
  return choice?.outcome ?? 'accepted'
}

export function tenantManifestUrl(slug: string): string {
  return `/api/v1/tenants/public/${encodeURIComponent(slug)}/manifest`
}

/**
 * Swaps the manifest link to the tenant-aware manifest once a tenant context
 * exists. Before sign-in the static platform manifest remains active.
 */
export function applyTenantManifest(slug: string | null | undefined): void {
  const href = slug ? tenantManifestUrl(slug) : '/manifest.webmanifest'
  let link = document.querySelector<HTMLLinkElement>('link[rel="manifest"]')
  if (!link) {
    link = document.createElement('link')
    link.rel = 'manifest'
    document.head.appendChild(link)
  }
  link.href = href
}

/** Browser-specific guidance when no install prompt is available. */
export function installGuidanceKey(): string {
  const userAgent = navigator.userAgent
  if (/iPhone|iPad|iPod/.test(userAgent)) return 'install.guidanceIos'
  if (/Firefox\//.test(userAgent)) return 'install.guidanceFirefox'
  return 'install.guidanceGeneric'
}
