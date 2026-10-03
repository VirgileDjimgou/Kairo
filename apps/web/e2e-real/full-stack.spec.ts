import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'

/**
 * Real-stack browser gate (Roadmap V2 Sprint 128).
 *
 * Runs against the production-like stack started by
 * docker-compose.release-gate.yml with seeded COMBIS data. No API is mocked:
 * every assertion exercises Vue -> nginx -> FastAPI -> PostgreSQL.
 */

const WCAG_22_AA_TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']
const TREASURER = { email: 'combis-treasurer@gate.kairo.app', password: 'GateTreasurer1!' }

async function login(page: Page, email: string, password: string): Promise<void> {
  await page.goto('/login')
  await page.locator('#email:visible').fill(email)
  await page.locator('#password:visible').fill(password)
  await page.locator('button[type="submit"]:visible').click()
  await expect(page).toHaveURL(/\/dashboard$/, { timeout: 30_000 })
}

test('real stack: branding, tenant manifest, service worker and accessibility', async ({ page }) => {
  await login(page, TREASURER.email, TREASURER.password)

  await expect(page).toHaveTitle('COMBIS App')
  const manifestHref = await page.locator('link[rel="manifest"]').getAttribute('href')
  expect(manifestHref).toContain('/api/v1/tenants/public/combis/manifest')

  const manifest = await page.evaluate(async (href) => {
    const response = await fetch(href!)
    return response.json()
  }, manifestHref)
  expect(manifest.name).toBe('COMBIS App')
  expect(manifest.icons.length).toBeGreaterThanOrEqual(2)

  await page.waitForFunction(async () => {
    const registration = await navigator.serviceWorker.getRegistration('/')
    return Boolean(registration?.active)
  })
  const registrations = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).length)
  expect(registrations).toBe(1)

  const lang = await page.evaluate(() => document.documentElement.lang)
  expect(['fr', 'en', 'de']).toContain(lang)

  const results = await new AxeBuilder({ page }).withTags(WCAG_22_AA_TAGS).analyze()
  if (results.violations.length > 0) {
    console.log('AXE_VIOLATIONS ' + JSON.stringify(results.violations.map((violation) => ({
      id: violation.id,
      targets: violation.nodes.map((node) => ({ target: node.target, html: node.html })),
    }))))
  }
  expect(results.violations.map((violation) => `${violation.id} (${violation.nodes.length})`)).toEqual([])
})

test('real stack: notification click reaches the exact authorized target', async ({ page }) => {
  await login(page, TREASURER.email, TREASURER.password)

  await page.getByRole('banner').getByRole('button', { name: 'Notifications' }).click()
  const item = page.locator('.notification-bell__item').first()
  await expect(item).toBeVisible()
  await item.click()

  await expect(page).toHaveURL(/\/finance$/, { timeout: 15_000 })
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
})

test('real stack: android viewport, offline shell and sign-out', async ({ page, context }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await login(page, TREASURER.email, TREASURER.password)

  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth + 1,
  )
  expect(overflow).toBe(false)

  // Offline: the canonical service worker serves the cached shell. The first
  // controlled navigation must happen before going offline, otherwise the
  // navigation route has no cached document to fall back to.
  await page.waitForFunction(() => Boolean(navigator.serviceWorker.controller))
  await page.reload()
  await page.waitForFunction(async () => {
    const cache = await caches.open('kairo-pages')
    return (await cache.keys()).some((request) => new URL(request.url).pathname === '/dashboard')
  })
  // Allow any auto-update reload to settle before testing offline behavior.
  await page.waitForTimeout(6000)
  await page.waitForFunction(() => Boolean(navigator.serviceWorker.controller))
  await context.setOffline(true)
  try {
    await page.reload()
    await expect(page.locator('main#kairo-main-content')).toBeVisible()
  } finally {
    await context.setOffline(false)
  }

  // Sign out returns to the public login surface.
  await page.locator('.app-top-bar__account').click()
  await page.getByRole('button', { name: 'Se déconnecter' }).click()
  await expect(page).toHaveURL(/\/login$/, { timeout: 15_000 })
})
