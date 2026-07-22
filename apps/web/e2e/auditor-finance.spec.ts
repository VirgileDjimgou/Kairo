import { expect, test, type Page } from '@playwright/test'

function makeAuditorMeResponse() {
  return {
    id: 'user-auditor-1',
    email: 'auditor@demo.org',
    display_name: 'Auditor Demo',
    preferred_language: 'en',
    status: 'active',
    tenant_id: 'tenant-demo-1',
    roles: ['auditor'],
    last_login_at: null,
    memberships: [
      {
        tenant_id: 'tenant-demo-1',
        slug: 'demo',
        name: 'Demo Organization',
        roles: ['auditor'],
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
      },
    ],
  }
}

async function mockAuditorFinance(page: Page) {
  const financeRequests: string[] = []

  const members = [
    {
      id: 'member-1',
      tenant_id: 'tenant-demo-1',
      user_id: 'user-member-1',
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
      user_id: 'user-member-2',
      member_code: 'M002',
      first_name: 'Bob',
      last_name: 'Example',
      display_name: 'Bob Example',
      email: 'bob@example.org',
      phone: null,
      status: 'active',
      joined_at: '2026-02-15T09:00:00Z',
      created_at: '2026-02-15T09:00:00Z',
      updated_at: '2026-02-15T09:00:00Z',
    },
  ]

  const contributions = [
    {
      id: 'contrib-1',
      tenant_id: 'tenant-demo-1',
      membership_profile_id: 'member-1',
      year: 2026,
      expected_amount: '120.00',
      paid_amount: '40.00',
      balance: '80.00',
      currency: 'EUR',
      status: 'partial',
      due_date: null,
      created_at: '2026-03-01T10:00:00Z',
      updated_at: '2026-03-15T10:00:00Z',
    },
    {
      id: 'contrib-2',
      tenant_id: 'tenant-demo-1',
      membership_profile_id: 'member-2',
      year: 2026,
      expected_amount: '90.00',
      paid_amount: '90.00',
      balance: '0.00',
      currency: 'EUR',
      status: 'paid',
      due_date: null,
      created_at: '2026-03-10T10:00:00Z',
      updated_at: '2026-03-20T10:00:00Z',
    },
  ]

  const payments = [
    {
      id: 'payment-1',
      tenant_id: 'tenant-demo-1',
      contribution_record_id: 'contrib-1',
      amount: '40.00',
      currency: 'EUR',
      paid_at: '2026-03-15T10:00:00Z',
      payment_method: 'bank_transfer',
      reference: 'INV-001',
      recorded_by: 'user-treasurer-1',
      created_at: '2026-03-15T10:00:00Z',
    },
    {
      id: 'payment-2',
      tenant_id: 'tenant-demo-1',
      contribution_record_id: 'contrib-2',
      amount: '90.00',
      currency: 'EUR',
      paid_at: '2026-03-20T10:00:00Z',
      payment_method: 'cash',
      reference: null,
      recorded_by: 'user-treasurer-1',
      created_at: '2026-03-20T10:00:00Z',
    },
  ]

  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-auditor-token')
  })

  page.on('request', (request) => {
    const url = new URL(request.url())
    if (url.origin === 'http://localhost:8000' && url.pathname.startsWith('/api/v1/contributions')) {
      financeRequests.push(url.pathname)
    }
  })

  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeAuditorMeResponse()),
    })
  })

  await page.route('**/api/v1/memberships/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(members),
    })
  })

  await page.route('**/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('**/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('**/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('**/api/v1/contributions/summary?**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        total_count: 2,
        total_expected: '210.00',
        total_paid: '130.00',
        total_balance: '80.00',
      }),
    })
  })

  await page.route('**/api/v1/contributions/payments', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(payments),
    })
  })

  await page.route('**/api/v1/contributions/report/export', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'text/csv',
      body: 'contribution_id,membership_profile_id,year\ncontrib-1,member-1,2026\n',
    })
  })

  await page.route('**/api/v1/contributions/?**', async (route) => {
    if (route.request().method() !== 'GET') {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Finance write capability required' }),
      })
      return
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(contributions),
    })
  })

  return { financeRequests }
}

test.describe('Auditor finance workspace', () => {
  test('auditor sees read-only finance oversight without mutation controls', async ({ page }) => {
    await mockAuditorFinance(page)
    await page.goto('/finance-audit')

    await expect(page).toHaveURL(/\/finance-audit$/)
    await expect(page.getByTestId('auditor-finance-overview')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Read-only finance oversight' })).toBeVisible()
    await expect(page.getByText('210.00 EUR')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Export finance report' })).toBeVisible()
    await expect(page.getByText('Alice Example (M001)')).toBeVisible()
    await expect(page.getByText('40.00 EUR · bank transfer')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Record payment' })).toHaveCount(0)
    await expect(page.getByRole('button', { name: 'Create contribution' })).toHaveCount(0)
  })

  test('auditor cannot enter the treasurer finance workspace or load contribution data', async ({ page }) => {
    const { financeRequests } = await mockAuditorFinance(page)

    await page.goto('/finance')

    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByRole('heading', { name: 'Welcome back, Auditor Demo' })).toBeVisible()
    expect(financeRequests).toEqual([])
  })
})
