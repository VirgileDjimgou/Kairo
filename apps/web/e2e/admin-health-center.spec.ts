import { expect, test, type Page } from '@playwright/test'

const adminMeResponse = {
  id: 'user-admin-1',
  email: 'admin@demo.org',
  display_name: 'Admin User',
  status: 'active',
  tenant_id: 'tenant-demo-1',
  roles: ['admin'],
  last_login_at: null,
  memberships: [
    {
      tenant_id: 'tenant-demo-1',
      slug: 'demo',
      name: 'Demo Organization',
      roles: ['admin'],
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
  ],
}

const presidentMeResponse = {
  ...adminMeResponse,
  id: 'user-president-1',
  email: 'president@demo.org',
  display_name: 'President User',
  roles: ['president'],
  memberships: [
    {
      ...adminMeResponse.memberships[0],
      roles: ['president'],
      profile_type: 'staff',
    },
  ],
}

function makeSettings(overrides?: Partial<Record<string, unknown>>) {
  return {
    tenant_id: 'tenant-demo-1',
    name: 'Demo Organization',
    slug: 'demo',
    default_language: 'en',
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
    operations: {
      last_backup_at: '2026-07-05T03:00:00Z',
      last_backup_status: 'completed',
      last_backup_reference: 'kairo-backup-20260705_030000.tar.gz',
      last_restore_drill_at: '2026-07-01T12:00:00Z',
      last_restore_drill_status: 'passed',
      alert_posture: 'healthy',
      alert_contacts_configured: true,
      backup_retention_days: 30,
      notes: 'Latest drill completed with a clean restore.',
      backup_is_stale: false,
      restore_drill_is_stale: false,
      alert_is_healthy: true,
      overall_status: 'healthy',
      status_message: 'Recovery evidence looks current and healthy.',
    },
    updated_at: '2026-07-05T12:00:00Z',
    ...overrides,
  }
}

async function mockHealthCenter(page: Page, settings = makeSettings(), meResponse = adminMeResponse) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-admin-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(meResponse),
    })
  })

  await page.route('http://localhost:8000/health', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        status: 'ok',
        version: '1.0.0',
        env: 'test',
        checks: {
          database: { status: 'ok', latency_ms: 2 },
          redis: { status: 'ok', latency_ms: 4 },
          minio: { status: 'ok', latency_ms: 6 },
          qdrant: { status: 'ok', latency_ms: 8 },
          ollama: { status: 'ok', latency_ms: 12 },
        },
        modules: ['membership', 'contributions', 'policies', 'disciplinary', 'events'],
      }),
    })
  })

  await page.route('http://localhost:8000/api/v1/tenants/tenant-demo-1/settings', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(settings),
    })
  })
}

test.describe('Admin health center', () => {
  test('shows dependency health and current recovery evidence', async ({ page }) => {
    await mockHealthCenter(page)
    await page.goto('/admin/health')

    await expect(page).toHaveURL(/\/admin\/health$/)
    await expect(page.getByRole('heading', { name: 'Recovery evidence and dependency health' })).toBeVisible()
    await expect(page.getByText('System status')).toBeVisible()
    await expect(page.getByText('Database', { exact: true })).toBeVisible()
    await expect(page.getByText('Redis cache', { exact: true })).toBeVisible()
    await expect(page.getByText('Object storage', { exact: true })).toBeVisible()
    await expect(page.getByText('Vector store', { exact: true })).toBeVisible()
    await expect(page.getByText('LLM provider', { exact: true })).toBeVisible()
    await expect(page.getByText('Latest drill completed with a clean restore.')).toBeVisible()
    await expect(page.getByTestId('health-center-warning-count')).toHaveText('0')
  })

  test('surfaces stale or missing recovery evidence warnings', async ({ page }) => {
    await mockHealthCenter(
      page,
      makeSettings({
        operations: {
          last_backup_at: null,
          last_backup_status: 'unknown',
          last_backup_reference: '',
          last_restore_drill_at: null,
          last_restore_drill_status: 'unknown',
          alert_posture: 'critical',
          alert_contacts_configured: false,
          backup_retention_days: null,
          notes: 'Recovery evidence missing for this tenant.',
          backup_is_stale: true,
          restore_drill_is_stale: true,
          alert_is_healthy: false,
          overall_status: 'critical',
          status_message: 'No recovery evidence has been recorded yet.',
        },
      }),
    )
    await page.goto('/admin/health')

    await expect(page).toHaveURL(/\/admin\/health$/)
    await expect(page.getByText('No recovery evidence has been recorded yet.')).toBeVisible()
    await expect(page.getByText('Backup evidence is stale and should be refreshed.')).toBeVisible()
    await expect(page.getByText('Restore drill evidence is stale and should be refreshed.')).toBeVisible()
    await expect(page.getByText('Alert contacts or alert posture need attention.')).toBeVisible()
  })

  test('is reachable for a president session through the read-only dashboard quick action', async ({ page }) => {
    await mockHealthCenter(page, makeSettings(), presidentMeResponse)
    await page.goto('/dashboard')

    await expect(page.getByRole('link', { name: 'Open health center' })).toHaveAttribute('href', '/admin/health')
    await page.getByRole('link', { name: 'Open health center' }).first().click()
    await expect(page).toHaveURL(/\/admin\/health$/)
    await expect(page.getByRole('heading', { name: 'Recovery evidence and dependency health' })).toBeVisible()
  })
})
