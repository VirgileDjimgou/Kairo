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

function makeTenantSettings(tenantId: string, name: string, slug: string) {
  return {
    tenant_id: tenantId,
    name,
    slug,
    default_language: 'en',
    branding: { primary_color: '#1f4f8f', logo_url: '' },
    modules: demoMemberships[0].modules,
    operations: {
      last_backup_at: null,
      last_backup_status: 'unknown',
      last_backup_reference: '',
      last_restore_drill_at: null,
      last_restore_drill_status: 'unknown',
      alert_posture: 'unknown',
      alert_contacts_configured: false,
      backup_retention_days: null,
      notes: '',
      backup_is_stale: false,
      restore_drill_is_stale: false,
      alert_is_healthy: false,
      overall_status: 'healthy',
      status_message: 'Healthy',
    },
    updated_at: '2026-01-01T00:00:00Z',
  }
}

test.describe('Tenant switching', () => {
  test('switches the active tenant through the tenant command center and preserves the new workspace', async ({ page }) => {
    let currentTenantId = 'tenant-demo-1'

    await page.addInitScript(() => {
      window.localStorage.setItem('access_token', 'tenant-switch-token')
      window.localStorage.setItem('selected_tenant_id', 'tenant-demo-1')
    })

    page.on('dialog', async (dialog) => {
      await dialog.accept()
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

      if (pathname.endsWith('/settings') && method === 'GET') {
        const membership = demoMemberships.find((item) => pathname.includes(item.tenant_id))
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(
            makeTenantSettings(
              membership?.tenant_id ?? currentTenantId,
              membership?.name ?? 'Acme Community Organization',
              membership?.slug ?? 'demo',
            ),
          ),
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

      if (pathname.endsWith('/documents/') && method === 'GET') {
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

    await page.goto('/admin/tenants', { waitUntil: 'networkidle' })
    await expect(page.getByTestId('tenant-card-demo')).toContainText('Current tenant')

    await page.getByRole('button', { name: 'Switch to riverdale' }).click()

    await expect(page.getByTestId('tenant-card-riverdale')).toContainText('Current tenant', {
      timeout: 15000,
    })
    await expect.poll(async () => page.evaluate(() => window.localStorage.getItem('selected_tenant_id'))).toBe(
      'tenant-riverdale-1',
    )
  })
})
