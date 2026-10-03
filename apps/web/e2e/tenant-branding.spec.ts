import { expect, test, type Page } from '@playwright/test'

const modules = {
  membership: true,
  contributions: true,
  policies: true,
  disciplinary: true,
  events: true,
  announcements: true,
  chat: true,
  notifications: true,
}

function membershipWithBranding(branding: Record<string, string>) {
  return {
    tenant_id: 'tenant-combis-1',
    slug: 'combis',
    name: 'Combis Sport Verein',
    roles: ['member'],
    branding,
    modules,
    profile_type: 'member',
  }
}

async function installRoutes(page: Page, branding: Record<string, string>): Promise<void> {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'tenant-branding-token')
    window.localStorage.setItem('selected_tenant_id', 'tenant-combis-1')
  })
  await page.route('**/api/v1/**', async (route) => {
    const request = route.request()
    const pathname = new URL(request.url()).pathname
    const method = request.method()

    if (pathname.endsWith('/auth/me') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'user-member-branding-1',
          email: 'member@combis.example',
          display_name: 'Awa Ngono',
          preferred_language: 'fr',
          status: 'active',
          tenant_id: 'tenant-combis-1',
          roles: ['member'],
          last_login_at: null,
          memberships: [membershipWithBranding(branding)],
        }),
      })
      return
    }
    if (pathname.endsWith('/notifications/inbox') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], unread_count: 0 }),
      })
      return
    }
    if (pathname.endsWith('/notifications/preferences') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          push_enabled: true,
          finance_enabled: true,
          discipline_enabled: true,
          announcements_enabled: true,
          events_enabled: true,
        }),
      })
      return
    }
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: `No branding mock for ${method} ${pathname}` }),
    })
  })
}

test('tenant branding drives title, favicon, theme color, logo and primary color', async ({ page }) => {
  await installRoutes(page, {
    display_name: 'COMBIS App',
    short_name: 'COMBIS',
    notification_name: 'COMBIS',
    primary_color: '#0a5c2e',
    secondary_color: '#c93146',
    background_color: '#f4f7f2',
    theme_color: '#0a5c2e',
    favicon_url: '/favicon.svg',
    logo_url: '/pwa-192x192.png',
  })

  await page.goto('/more')
  await expect(page).toHaveURL(/\/more$/)
  await expect(page).toHaveTitle('COMBIS App')

  const favicon = await page.locator('link[rel="icon"]').getAttribute('href')
  expect(favicon).toContain('/favicon.svg')

  const themeColor = await page.locator('meta[name="theme-color"]').getAttribute('content')
  expect(themeColor).toBe('#0a5c2e')

  const primary = await page.evaluate(() =>
    getComputedStyle(document.documentElement).getPropertyValue('--om-primary').trim(),
  )
  expect(primary).toBe('#0a5c2e')

  const logo = page.locator('.app-top-bar__mark img')
  await expect(logo).toHaveAttribute('src', /pwa-192x192\.png/)
})

test('safe Kairo defaults apply when a tenant has no branding', async ({ page }) => {
  await installRoutes(page, { primary_color: '#1f4f8f', logo_url: '' })

  await page.goto('/more')
  await expect(page).toHaveTitle('Kairo')
  const primary = await page.evaluate(() =>
    getComputedStyle(document.documentElement).getPropertyValue('--om-primary').trim(),
  )
  expect(primary).toBe('#1f4f8f')
})

test('unsafe branding asset values fall back to the safe default', async ({ page }) => {
  await installRoutes(page, {
    display_name: 'COMBIS App',
    favicon_url: 'javascript:alert(1)',
    logo_url: 'data:text/html,<script>alert(1)</script>',
  })

  await page.goto('/more')
  await expect(page).toHaveTitle('COMBIS App')

  const favicon = await page.locator('link[rel="icon"]').getAttribute('href')
  expect(favicon).toContain('/favicon.svg')
  await expect(page.locator('.app-top-bar__mark img')).toHaveCount(0)
})
