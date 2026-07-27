import { test, expect, type Page } from '@playwright/test'

const VIEWPORTS = [
  { width: 320, height: 568, name: '320' },
  { width: 360, height: 800, name: '360' },
  { width: 375, height: 812, name: '375' },
  { width: 390, height: 844, name: '390' },
  { width: 412, height: 915, name: '412' },
  { width: 430, height: 932, name: '430' },
  { width: 768, height: 1024, name: '768' },
  { width: 1280, height: 720, name: '1280' },
  { width: 1440, height: 900, name: '1440' },
]

const ROUTES = [
  { path: '/dashboard', name: 'dashboard' },
  { path: '/members/profile', name: 'profile' },
  { path: '/account/security', name: 'security' },
  { path: '/events', name: 'events' },
  { path: '/announcements', name: 'announcements' },
  { path: '/policies', name: 'policies' },
  { path: '/admin', name: 'admin-overview' },
  { path: '/admin/members', name: 'admin-members' },
  { path: '/admin/contributions', name: 'admin-contributions' },
  { path: '/admin/events', name: 'admin-events' },
  { path: '/admin/announcements', name: 'admin-announcements' },
  { path: '/admin/audit', name: 'admin-audit' },
  { path: '/admin/settings', name: 'admin-settings' },
]

async function loginAndNavigate(page: Page, route: string) {
  await page.goto('https://app.combissportverein.org/', { waitUntil: 'networkidle' })
  const emailInput = page.locator('input[type="email"]')
  if (await emailInput.isVisible()) {
    await emailInput.fill('admin@demo.org')
    await page.locator('input[type="password"]').fill('Admin123!')
    await page.locator('button[type="submit"]').click()
    await page.waitForURL('**/dashboard', { timeout: 15000 })
    await page.waitForTimeout(500)
  }
  await page.goto(`https://app.combissportverein.org${route}`, { waitUntil: 'networkidle' })
  await page.waitForTimeout(300)
}

for (const vp of VIEWPORTS) {
  for (const route of ROUTES) {
    test(`overflow-check @${vp.name}px - ${route.name}`, async ({ page }) => {
      await page.context().setViewportSize({ width: vp.width, height: vp.height })
      await loginAndNavigate(page, route.path)

      const overflow = await page.evaluate(() => {
        const docEl = document.documentElement
        const body = document.body
        return {
          scrollWidth: Math.max(docEl.scrollWidth, body.scrollWidth),
          clientWidth: docEl.clientWidth,
          bodyScrollWidth: body.scrollWidth,
          bodyClientWidth: body.clientWidth,
        }
      })

      const overflowPx = overflow.scrollWidth - overflow.clientWidth
      test.info().annotations.push({
        type: 'overflow',
        description: `scrollW=${overflow.scrollWidth} clientW=${overflow.clientWidth} diff=${overflowPx}`,
      })

      // Tolerance: 1px for sub-pixel rounding
      expect(overflowPx, `Horizontal overflow at ${vp.width}px on ${route.path}: ${overflowPx}px`).toBeLessThanOrEqual(1)
    })
  }
}