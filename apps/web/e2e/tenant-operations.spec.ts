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
    status: 'active',
    tenant_id: tenantId,
    roles: ['principal_admin'],
    last_login_at: null,
    memberships: demoMemberships,
  }
}

function makeSettings(tenantName: string, status: 'healthy' | 'warning' | 'critical') {
  return {
    tenant_id: tenantName === 'Acme Community Organization' ? 'tenant-demo-1' : 'tenant-riverdale-1',
    name: tenantName,
    slug: tenantName === 'Acme Community Organization' ? 'demo' : 'riverdale',
    default_language: 'en',
    branding: {
      primary_color: tenantName === 'Acme Community Organization' ? '#1f4f8f' : '#2f6f55',
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
    operations: {
      last_backup_at: '2026-07-02T03:00:00Z',
      last_backup_status: status === 'critical' ? 'failed' : 'completed',
      last_backup_reference: 'kairo-backup-20260702_030000.tar.gz',
      last_restore_drill_at: '2026-06-28T12:00:00Z',
      last_restore_drill_status: status === 'critical' ? 'failed' : 'passed',
      alert_posture: status,
      alert_contacts_configured: status !== 'critical',
      backup_retention_days: 30,
      notes: `${tenantName} recovery note.`,
      backup_is_stale: false,
      restore_drill_is_stale: false,
      alert_is_healthy: status === 'healthy',
      overall_status: status,
      status_message:
        status === 'healthy'
          ? 'Recovery evidence looks current and healthy.'
          : status === 'warning'
            ? 'Recovery evidence needs refresh.'
            : 'Recovery posture is critical and needs attention.',
    },
    updated_at: '2026-07-04T12:00:00Z',
  }
}

test.describe('Tenant operations command center', () => {
  test('shows membership inventory and switches tenant context explicitly', async ({ page }) => {
    let currentTenantId = 'tenant-demo-1'

    await page.addInitScript(() => {
      window.localStorage.setItem('access_token', 'tenant-ops-token')
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

      if (pathname.match(/\/tenants\/[^/]+\/settings$/) && method === 'GET') {
        const tenantId = pathname.split('/')[4]
        const tenantName = tenantId === 'tenant-demo-1' ? 'Acme Community Organization' : 'Riverdale Sports Union'
        const status = tenantId === 'tenant-demo-1' ? 'healthy' : 'warning'

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(makeSettings(tenantName, status)),
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

      await route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ detail: `No mock for ${method} ${pathname}` }),
      })
    })

    await page.goto('/admin/tenants', { waitUntil: 'networkidle' })

    await expect(page.getByTestId('tenant-ops-label')).toHaveText('Multi-tenant operations')
    await expect(page.getByTestId('tenant-ops-title')).toHaveText('Command center')
    await expect(page.getByTestId('tenant-card-demo')).toContainText('Current tenant')
    await expect(page.getByTestId('tenant-card-riverdale')).toContainText('Available tenant')
    await expect(page.getByText('Safe preparation notes')).toBeVisible()
    await expect(page.getByTestId('tenant-ops-success')).toHaveCount(0)

    page.on('dialog', async (dialog) => {
      expect(dialog.message()).toContain('Switch from Acme Community Organization to Riverdale Sports Union')
      await dialog.accept()
    })

    await page.getByRole('button', { name: 'Switch to riverdale' }).click()

    await expect(page.getByTestId('tenant-ops-success')).toContainText(
      'Switched to Riverdale Sports Union',
    )
    await expect(page.getByTestId('tenant-card-riverdale')).toContainText('Current tenant')
    await expect(page.getByTestId('tenant-card-demo')).toContainText('Available tenant')
    await expect.poll(async () => page.evaluate(() => window.localStorage.getItem('selected_tenant_id'))).toBe(
      'tenant-riverdale-1',
    )
  })
})
