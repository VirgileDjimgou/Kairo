import { expect, test, type Page } from '@playwright/test'

function makeMembership(role: string) {
  return {
    tenant_id: 'tenant-demo-1',
    slug: 'demo',
    name: 'Demo Organization',
    roles: [role],
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
    profile_type: 'staff',
  }
}

function makeExecutiveMeResponse(role: string, email: string, displayName: string) {
  return {
    id: `user-${role}-1`,
    email,
    display_name: displayName,
    status: 'active',
    tenant_id: 'tenant-demo-1',
    roles: [role],
    last_login_at: null,
    memberships: [makeMembership(role)],
  }
}

async function mockExecutiveWorkspace(page: Page, role: 'president' | 'vice_president') {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-exec-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    const displayName = role === 'president' ? 'President User' : 'Vice President User'
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeExecutiveMeResponse(role, `${role}@demo.org`, displayName)),
    })
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'doc-1',
          title: 'Bylaws',
          description: 'Official bylaws',
          source_type: 'upload',
          language: 'en',
          access_scope: 'members_only',
          allowed_role_ids: null,
          status: 'ready',
          owner_user_id: null,
          created_at: '2026-07-01T09:00:00Z',
          current_version: null,
        },
        {
          id: 'doc-2',
          title: 'Meeting Minutes',
          description: 'Quarterly minutes',
          source_type: 'upload',
          language: 'en',
          access_scope: 'members_only',
          allowed_role_ids: null,
          status: 'ready',
          owner_user_id: null,
          created_at: '2026-07-01T10:00:00Z',
          current_version: null,
        },
      ]),
    })
  })

  await page.route('http://localhost:8000/api/v1/memberships/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'member-1',
          tenant_id: 'tenant-demo-1',
          user_id: 'user-1',
          member_code: 'M001',
          first_name: 'Alice',
          last_name: 'Example',
          display_name: 'Alice Example',
          email: 'alice@example.org',
          phone: null,
          status: 'active',
          joined_at: '2026-01-10T09:00:00Z',
          created_at: '2026-01-10T09:00:00Z',
          updated_at: '2026-01-10T09:00:00Z',
        },
        {
          id: 'member-2',
          tenant_id: 'tenant-demo-1',
          user_id: 'user-2',
          member_code: 'M002',
          first_name: 'Bob',
          last_name: 'Example',
          display_name: 'Bob Example',
          email: 'bob@example.org',
          phone: null,
          status: 'active',
          joined_at: '2026-02-12T09:00:00Z',
          created_at: '2026-02-12T09:00:00Z',
          updated_at: '2026-02-12T09:00:00Z',
        },
      ]),
    })
  })

  await page.route('http://localhost:8000/api/v1/contributions/summary', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total_count: 4,
        total_expected: '240.00',
        total_paid: '180.00',
        total_balance: '60.00',
      }),
    })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'ann-1',
          tenant_id: 'tenant-demo-1',
          title: 'Board Notice',
          body: 'Meeting on Friday.',
          visibility_scope: 'members_only',
          published_at: '2026-07-01T00:00:00Z',
          expires_at: null,
          created_by: 'user-pres-1',
          created_at: '2026-07-01T00:00:00Z',
          updated_at: '2026-07-01T00:00:00Z',
        },
        {
          id: 'ann-2',
          tenant_id: 'tenant-demo-1',
          title: 'Summer BBQ',
          body: 'Save the date.',
          visibility_scope: 'members_only',
          published_at: '2026-07-02T00:00:00Z',
          expires_at: null,
          created_by: 'user-pres-1',
          created_at: '2026-07-02T00:00:00Z',
          updated_at: '2026-07-02T00:00:00Z',
        },
      ]),
    })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'evt-1',
          tenant_id: 'tenant-demo-1',
          title: 'Annual Meeting',
          description: 'General assembly',
          start_at: '2026-07-15T10:00:00Z',
          end_at: '2026-07-15T12:00:00Z',
          location: 'Main Hall',
          visibility_scope: 'members_only',
          status: 'published',
          metadata_json: {},
          created_by: 'user-pres-1',
          created_at: '2026-07-01T00:00:00Z',
          updated_at: '2026-07-01T00:00:00Z',
        },
        {
          id: 'evt-2',
          tenant_id: 'tenant-demo-1',
          title: 'Board Retreat',
          description: 'Executive planning',
          start_at: '2026-08-01T10:00:00Z',
          end_at: '2026-08-01T12:00:00Z',
          location: 'Offsite',
          visibility_scope: 'role_restricted',
          status: 'published',
          metadata_json: {},
          created_by: 'user-pres-1',
          created_at: '2026-07-01T00:00:00Z',
          updated_at: '2026-07-01T00:00:00Z',
        },
        {
          id: 'evt-3',
          tenant_id: 'tenant-demo-1',
          title: 'Community Day',
          description: 'Open event',
          start_at: '2026-09-01T10:00:00Z',
          end_at: '2026-09-01T12:00:00Z',
          location: 'Park',
          visibility_scope: 'tenant_public',
          status: 'published',
          metadata_json: {},
          created_by: 'user-pres-1',
          created_at: '2026-07-01T00:00:00Z',
          updated_at: '2026-07-01T00:00:00Z',
        },
      ]),
    })
  })

  await page.route(/http:\/\/localhost:8000\/api\/v1\/admin\/audit\/events.*/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'audit-1',
          tenant_id: 'tenant-demo-1',
          actor_user_id: 'user-pres-1',
          module_key: 'events',
          action: 'create',
          entity_type: 'event',
          entity_id: 'evt-1',
          details: {},
          created_at: '2026-07-01T00:00:00Z',
        },
      ]),
    })
  })
}

async function mockDeniedExecutiveWorkspace(page: Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-denied-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'user-treasurer-1',
        email: 'treasurer@demo.org',
        display_name: 'Treasurer User',
        status: 'active',
        tenant_id: 'tenant-demo-1',
        roles: ['treasurer'],
        last_login_at: null,
        memberships: [makeMembership('treasurer')],
      }),
    })
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
  })
}

test.describe('Governance cockpit', () => {
  test('president sees the executive cockpit with finance and audit shortcuts', async ({ page }) => {
    await mockExecutiveWorkspace(page, 'president')
    await page.goto('/governance')

    await expect(page).toHaveURL(/\/governance$/)
    await expect(page.getByRole('heading', { name: 'President governance cockpit' })).toBeVisible()
    await expect(page.getByTestId('governance-cockpit-subtitle')).toContainText('strategic governance')
    await expect(page.getByText('Open finance audit')).toBeVisible()
    await expect(page.getByText('Review audit trail')).toBeVisible()
    await expect(page.getByText('Contribution balance')).toBeVisible()
    await expect(page.getByTestId('governance-finance-snapshot')).toContainText('60.00 EUR')
    await expect(page.getByTestId('governance-finance-link')).toBeVisible()
  })

  test('vice president sees a narrower cockpit without audit shortcuts', async ({ page }) => {
    await mockExecutiveWorkspace(page, 'vice_president')
    await page.goto('/governance')

    await expect(page).toHaveURL(/\/governance$/)
    await expect(page.getByRole('heading', { name: 'Vice president governance cockpit' })).toBeVisible()
    await expect(page.getByTestId('governance-cockpit-subtitle')).toContainText('clear visibility')
    await expect(page.getByText('Open finance audit')).toHaveCount(0)
    await expect(page.getByText('Review audit trail')).toHaveCount(0)
    await expect(page.getByText('Audit hidden')).toBeVisible()
  })

  test('treasurer is redirected away from the executive cockpit', async ({ page }) => {
    await mockDeniedExecutiveWorkspace(page)
    await page.goto('/governance')

    await expect(page.getByRole('heading', { name: 'Welcome back, Treasurer User' })).toBeVisible()
    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByRole('link', { name: 'Governance Cockpit' })).toHaveCount(0)
  })
})
