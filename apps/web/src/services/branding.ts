import type { TenantBranding } from '@/api/branding.types'
import { KAIRO_BRANDING_DEFAULTS } from '@/api/branding.types'

export function effectiveBranding(branding?: Partial<TenantBranding> | null): TenantBranding {
  return { ...KAIRO_BRANDING_DEFAULTS, ...(branding ?? {}) }
}

/** Accept only site-relative paths or http(s) URLs for a branding asset. */
export function safeBrandingAsset(value: string, fallback: string): string {
  if (!value) return fallback
  if (value.startsWith('/') && !value.startsWith('//')) return value
  try {
    const url = new URL(value)
    return url.protocol === 'https:' || url.protocol === 'http:' ? value : fallback
  } catch {
    return fallback
  }
}

function setMetaContent(name: string, content: string): void {
  let meta = document.querySelector<HTMLMetaElement>(`meta[name="${name}"]`)
  if (!meta) {
    meta = document.createElement('meta')
    meta.setAttribute('name', name)
    document.head.appendChild(meta)
  }
  meta.setAttribute('content', content)
}

function applyFavicon(href: string): void {
  let link = document.querySelector<HTMLLinkElement>('link[rel="icon"]')
  if (!link) {
    link = document.createElement('link')
    link.rel = 'icon'
    document.head.appendChild(link)
  }
  link.href = href
}

/**
 * iOS reads `apple-touch-icon` before the manifest icons for the Home Screen
 * web clip. Injecting it per tenant keeps the installed identity branded on
 * iPhone/iPad; manifest icons remain the fallback for every other platform.
 */
function applyAppleTouchIcon(href: string): void {
  let link = document.querySelector<HTMLLinkElement>('link[rel="apple-touch-icon"]')
  if (!link) {
    link = document.createElement('link')
    link.rel = 'apple-touch-icon'
    document.head.appendChild(link)
  }
  link.href = href
}

/**
 * Publishes the tenant notification name to the Service Worker so a push that
 * arrives without a title is attributed to the association, never the platform.
 */
function syncNotificationIdentity(name: string): void {
  if (typeof navigator === 'undefined' || !('serviceWorker' in navigator)) return
  const message = { type: 'kairo:notification-identity', name }
  navigator.serviceWorker.controller?.postMessage(message)
  void navigator.serviceWorker.ready
    .then((registration) => registration.active?.postMessage(message))
    .catch(() => undefined)
}

/**
 * Applies the effective tenant branding to the shared presentation surfaces:
 * page title, favicon, theme/apple meta tags and the semantic CSS variables
 * consumed by the shell, buttons and layouts. It never touches authorization.
 */
export function applyBranding(branding?: Partial<TenantBranding> | null): TenantBranding {
  const effective = effectiveBranding(branding)
  syncNotificationIdentity(effective.notification_name)
  if (typeof document === 'undefined') return effective

  document.title = effective.display_name
  applyFavicon(safeBrandingAsset(effective.favicon_url, '/favicon.svg'))
  applyAppleTouchIcon(
    safeBrandingAsset(
      effective.icon_512_url || effective.icon_192_url || effective.favicon_url,
      '/pwa-192x192.png',
    ),
  )
  setMetaContent('theme-color', effective.theme_color)
  setMetaContent('apple-mobile-web-app-title', effective.short_name || effective.display_name)

  const root = document.documentElement
  root.style.setProperty('--om-primary', effective.primary_color)
  root.style.setProperty('--om-secondary', effective.secondary_color)
  root.style.setProperty('--om-background', effective.background_color)
  return effective
}
