import { test, expect, type Page } from '@playwright/test'

type ModuleToggles = {
  membership: boolean
  contributions: boolean
  policies: boolean
  disciplinary: boolean
  events: boolean
  announcements: boolean
  chat: boolean
  notifications: boolean
}

function makeMeResponse(modules: ModuleToggles) {
  return {
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
        modules,
        profile_type: 'admin',
      },
    ],
  }
}

async function mockAdminOverview(page: Page, modules: ModuleToggles) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-admin-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeMeResponse(modules)),
    })
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'doc-1',
          title: 'Welcome Guide',
          description: 'First admin handbook',
          source_type: 'upload',
          language: 'en',
          access_scope: 'tenant_public',
          allowed_role_ids: null,
          status: 'ready',
          owner_user_id: null,
          created_at: '2026-06-29T08:00:00Z',
          current_version: null,
        },
      ]),
    })
  })

  await page.route('http://localhost:8000/api/v1/admin/audit/events**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'audit-1',
          tenant_id: 'tenant-demo-1',
          actor_user_id: 'user-admin-1',
          module_key: 'documents',
          action: 'create',
          entity_type: 'document',
          entity_id: 'doc-1',
          details: { title: 'Welcome Guide' },
          created_at: '2026-06-29T09:00:00Z',
        },
      ]),
    })
  })

  await page.route('http://localhost:8000/api/v1/admin/ingestion-jobs/health', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        queued_count: 1,
        processing_count: 0,
        failed_count: 0,
        completed_count: 3,
        retried_count: 1,
        recent_failures: [],
      }),
    })
  })

  await page.route('http://localhost:8000/api/v1/memberships/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(
        modules.membership
          ? [
              {
                id: 'member-1',
                tenant_id: 'tenant-demo-1',
                user_id: null,
                member_code: 'M-001',
                first_name: 'Alice',
                last_name: 'Jones',
                display_name: 'Alice Jones',
                email: 'alice@example.org',
                phone: null,
                status: 'active',
                joined_at: '2026-06-01T00:00:00Z',
                created_at: '2026-06-01T00:00:00Z',
                updated_at: '2026-06-01T00:00:00Z',
              },
            ]
          : []
      ),
    })
  })

  await page.route('http://localhost:8000/api/v1/contributions/summary**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total_count: 2,
        total_expected: '200.00',
        total_paid: '125.00',
        total_balance: '75.00',
      }),
    })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(
        modules.announcements
          ? [
              {
                id: 'ann-1',
                tenant_id: 'tenant-demo-1',
                title: 'Launch note',
                body: 'Welcome',
                visibility_scope: 'tenant_public',
                published_at: '2026-06-29T10:00:00Z',
                expires_at: null,
                created_by: null,
                created_at: '2026-06-29T10:00:00Z',
                updated_at: '2026-06-29T10:00:00Z',
              },
            ]
          : []
      ),
    })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(
        modules.events
          ? [
              {
                id: 'evt-1',
                tenant_id: 'tenant-demo-1',
                title: 'Board meeting',
                description: null,
                start_at: '2026-07-01T10:00:00Z',
                end_at: null,
                location: null,
                visibility_scope: 'tenant_public',
                status: 'published',
                created_by: null,
                created_at: '2026-06-29T10:00:00Z',
                updated_at: '2026-06-29T10:00:00Z',
              },
            ]
          : []
      ),
    })
  })

  await page.route('http://localhost:8000/api/v1/notifications/channels', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          channel: 'email',
          display_name: 'Email',
          description: 'SMTP channel',
          configured: true,
          simulation_only: true,
          target_hint: 'ops@example.org',
        },
        {
          channel: 'telegram',
          display_name: 'Telegram',
          description: 'Bot placeholder',
          configured: false,
          simulation_only: true,
          target_hint: '@channel',
        },
      ]),
    })
  })
}

test.describe('Admin overview', () => {
  test('renders a real operations hub for admins', async ({ page }) => {
    await mockAdminOverview(page, {
      membership: true,
      contributions: true,
      policies: true,
      disciplinary: true,
      events: true,
      announcements: true,
      chat: true,
      notifications: true,
    })

    await page.goto('/admin')

    await expect(page).toHaveURL(/\/admin$/)
    await expect(page.getByText('Admin operations hub')).toBeVisible()
    await expect(page.getByTestId('admin-overview-metrics')).toContainText('Documents')
    await expect(page.getByTestId('admin-overview-metrics')).toContainText('Open balance')
    await expect(page.getByText('Operational watchlist')).toBeVisible()
    await expect(page.getByText('Launch readiness')).toBeVisible()
    await expect(page.getByTestId('admin-overview-quick-actions')).toContainText('Tenant settings')
    await expect(page.getByText('Ingestion health')).toBeVisible()
  })

  test('hides disabled module widgets and quick actions', async ({ page }) => {
    await mockAdminOverview(page, {
      membership: false,
      contributions: false,
      policies: true,
      disciplinary: true,
      events: false,
      announcements: false,
      chat: true,
      notifications: false,
    })

    await page.goto('/admin')

    await expect(page.getByTestId('admin-overview-metrics')).not.toContainText('Members')
    await expect(page.getByTestId('admin-overview-metrics')).not.toContainText('Open balance')
    await expect(page.getByTestId('admin-overview-metrics')).not.toContainText('Announcements')
    await expect(page.getByTestId('admin-overview-metrics')).not.toContainText('Upcoming events')
    await expect(page.getByTestId('admin-overview-quick-actions')).not.toContainText('Channels')
    await expect(page.getByTestId('admin-overview-quick-actions')).not.toContainText('Members')
  })
})
