import { expect, test } from '@playwright/test'

/**
 * These tests run against the production build served by `vite preview`
 * (playwright.pwa.config.ts). They verify the acceptance-critical Service
 * Worker properties that the dev server cannot exercise: a single canonical
 * worker for the origin and a working offline fallback.
 */

test('exactly one canonical service worker controls the application origin', async ({ page }) => {
  await page.goto('/login')
  await page.waitForFunction(() => Boolean(navigator.serviceWorker.controller))
  await expect
    .poll(async () => page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).length))
    .toBe(1)

  const registrations = await page.evaluate(async () => {
    const list = await navigator.serviceWorker.getRegistrations()
    return list.map((registration) => ({
      scope: registration.scope,
      script: registration.active?.scriptURL ?? null,
    }))
  })

  expect(registrations[0]?.script).toContain('/sw.js')
  expect(new URL(registrations[0]!.scope).pathname).toBe('/')
})

test('the web manifest is installable and linked from the shell', async ({ page }) => {
  await page.goto('/login')
  const manifestHref = await page.locator('link[rel="manifest"]').getAttribute('href')
  expect(manifestHref).toBeTruthy()

  const manifest = await page.evaluate(async (href) => {
    const response = await fetch(href!)
    return response.json()
  }, manifestHref)

  expect(manifest.display).toBe('standalone')
  expect(manifest.start_url).toBe('/dashboard')
  expect(manifest.icons.length).toBeGreaterThanOrEqual(2)
  expect(manifest.icons.some((icon: { purpose?: string }) => icon.purpose === 'maskable')).toBe(true)
})

test('offline navigation falls back to the cached application shell', async ({ page, context }) => {
  await page.goto('/login')
  await page.waitForFunction(() => Boolean(navigator.serviceWorker.controller))

  // Reload once while controlled so the navigation route caches the shell.
  await page.reload()
  await page.waitForFunction(async () => {
    const cache = await caches.open('kairo-pages')
    return (await cache.keys()).length > 0
  })

  await context.setOffline(true)
  try {
    await page.reload()
    await expect(page.getByRole('heading', { name: 'Accéder à votre espace' })).toBeVisible()
  } finally {
    await context.setOffline(false)
  }
})
