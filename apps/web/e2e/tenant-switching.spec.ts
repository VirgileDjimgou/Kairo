import { test, expect } from '@playwright/test'

const demoMemberships = [
  {
    tenant_id: 'tenant-demo-1',
    slug: 'demo',
    name: 'Acme Community Organization',
    roles: ['principal_admin'],
    branding: {
      primary_color: '#1f4f8f',
      logo_url: '',
    },
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
    profile_type: 'admin',
  },
  {
    tenant_id: 'tenant-riverdale-1',
    slug: 'riverdale',
    name: 'Riverdale Sports Union',
    roles: ['principal_admin'],
    branding: {
      primary_color: '#2f6f55',
      logo_url: '',
    },
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
    profile_type: 'admin',
  },
]

function makeUser(tenantId: string) {
  return {
    id: 'user-principal-1',
    email: 'principal@demo.org',
    display_name: 'Priya Principal',
    preferred_language: 'en',
    status: 'active',
    tenant_id: tenantId,
    roles: ['principal_admin'],
    last_login_at: null,
    memberships: demoMemberships,
  }
}

test.describe('Tenant switching', () => {
  test('switches the active tenant through the header selector and preserves the new workspace', async ({ page }) => {
    let currentTenantId = 'tenant-demo-1'

    await page.addInitScript(() => {
      window.localStorage.setItem('access_token', 'tenant-switch-token')
      window.localStorage.setItem('selected_tenant_id', 'tenant-demo-1')
    })

    await page.route('http://localhost:8000/api/v1/**', async (route) => {
      const request = route.request()
      const pathname = new URL(request.url()).pathname
      const method = request.method()

      if (pathname.endsWith('/auth/me') && method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(makeUser(currentTenantId)),
        })
        return
      }

      if (pathname.endsWith('/auth/switch-tenant') && method === 'POST') {
        const payload = request.postDataJSON()
        currentTenantId = payload.tenant_id

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            access_token: `token-${payload.tenant_id}`,
            token_type: 'bearer',
            expires_in: 3600,
            tenant_id: payload.tenant_id,
            user_id: 'user-principal-1',
            memberships: demoMemberships,
          }),
        })
        return
      }

      if (pathname.endsWith('/memberships/me/statement') && method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            profile: null,
            summary: {
              total_count: 0,
              total_expected: '0.00',
              total_paid: '0.00',
              total_balance: '0.00',
              contribution_count: 0,
            },
            contributions: [],
          }),
        })
        return
      }

      if (pathname.endsWith('/announcements/active') && method === 'GET') {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
        return
      }

      if (pathname.endsWith('/events/public') && method === 'GET') {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
        return
      }

      if (pathname.endsWith('/documents') && method === 'GET') {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
        return
      }

      if (pathname.endsWith('/contributions/') && method === 'GET') {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
        return
      }

      if (pathname.endsWith('/policies/') && method === 'GET') {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
        return
      }

      if (pathname.endsWith('/memberships/') && method === 'GET') {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
        return
      }

      if (pathname.endsWith('/notifications/channels') && method === 'GET') {
        await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
        return
      }

      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ detail: `No mock for ${method} ${pathname}` }),
      })
    })

    await page.goto('/dashboard', { waitUntil: 'networkidle' })
    await expect(page.locator('.tenant-switcher .dropdown-toggle')).toContainText('Acme Community Organization')

    await page.locator('.tenant-switcher .dropdown-toggle').click()
    await page.locator('.tenant-switcher .dropdown-menu .dropdown-item').filter({ hasText: 'Riverdale Sports Union' }).click()

    await expect(page.locator('.tenant-switcher .dropdown-toggle')).toContainText('Riverdale Sports Union', {
      timeout: 15000,
    })
    await expect(page.getByRole('heading', { name: /Welcome back, Priya Principal/ })).toBeVisible({
      timeout: 15000,
    })
    await expect.poll(async () => page.evaluate(() => window.localStorage.getItem('selected_tenant_id'))).toBe(
      'tenant-riverdale-1',
    )
  })
})
