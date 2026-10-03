import { expect, test, type Page } from '@playwright/test'

const resolvedTenant = {
  tenant_id: 'tenant-combis-1',
  slug: 'combis',
  name: 'Combis Sport Verein',
  default_language: 'fr',
  branding: {
    display_name: 'COMBIS App',
    short_name: 'COMBIS',
    primary_color: '#0a5c2e',
    theme_color: '#0a5c2e',
  },
  manifest_url: '/api/v1/tenants/public/combis/manifest',
}

async function installRoutes(page: Page, resolution: Record<string, unknown> | null): Promise<void> {
  await page.route('**/api/v1/**', async (route) => {
    const request = route.request()
    const pathname = new URL(request.url()).pathname
    const method = request.method()

    if (pathname.endsWith('/tenants/public/resolve') && method === 'GET') {
      if (!resolution) {
        await route.fulfill({
          status: 404,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'No tenant is mapped to this host' }),
        })
        return
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(resolution),
      })
      return
    }
    if (pathname.endsWith('/auth/login') && method === 'POST') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'host-tenant-token',
          token_type: 'bearer',
          expires_in: 3600,
          tenant_id: 'tenant-combis-1',
          user_id: 'user-member-host-1',
          password_change_required: false,
        }),
      })
      return
    }
    if (pathname.endsWith('/auth/me') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'user-member-host-1',
          email: 'member@combis.example',
          display_name: 'Awa Ngono',
          preferred_language: 'fr',
          status: 'active',
          tenant_id: 'tenant-combis-1',
          roles: ['member'],
          last_login_at: null,
          memberships: [
            {
              tenant_id: 'tenant-combis-1',
              slug: 'combis',
              name: 'Combis Sport Verein',
              roles: ['member'],
              branding: resolvedTenant.branding,
              modules: {
                membership: true,
                contributions: true,
                policies: true,
                disciplinary: true,
                events: true,
                announcements: true,
                chat: true,
                notifications: true,
              },
              profile_type: 'member',
            },
          ],
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
    if (pathname.endsWith('/notifications/devices') && method === 'POST') {
      await route.fulfill({ status: 204, body: '' })
      return
    }
    if (pathname.endsWith('/attention') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [] }),
      })
      return
    }
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: `No host-tenant mock for ${method} ${pathname}` }),
    })
  })
}

test('a mapped host applies tenant branding and manifest before sign-in', async ({ page }) => {
  await installRoutes(page, resolvedTenant)
  await page.goto('/login')

  await expect(page).toHaveTitle('COMBIS App')
  const href = await page.locator('link[rel="manifest"]').getAttribute('href')
  expect(href).toContain('/api/v1/tenants/public/combis/manifest')
  const primary = await page.evaluate(() =>
    getComputedStyle(document.documentElement).getPropertyValue('--om-primary').trim(),
  )
  expect(primary).toBe('#0a5c2e')
})

test('an unmapped host keeps the safe platform defaults', async ({ page }) => {
  await installRoutes(page, null)
  await page.goto('/login')

  await expect(page).toHaveTitle('Kairo')
  const href = await page.locator('link[rel="manifest"]').getAttribute('href')
  expect(href).toContain('/manifest.webmanifest')
})

test('host resolution seeds the login tenant context', async ({ page }) => {
  await installRoutes(page, resolvedTenant)
  await page.goto('/login')

  const loginRequest = page.waitForRequest(
    (request) => request.url().includes('/auth/login') && request.method() === 'POST',
  )
  await page.locator('#email:visible').fill('member@combis.example')
  await page.locator('#password:visible').fill('HostTenantPass1!')
  await page.locator('button[type="submit"]:visible').click()

  const body = (await loginRequest).postDataJSON() as { tenant_slug?: string }
  expect(body.tenant_slug).toBe('combis')
})
