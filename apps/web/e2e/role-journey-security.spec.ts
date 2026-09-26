import { expect, test, type Page } from '@playwright/test'

const moduleToggles = {
  membership: true,
  contributions: true,
  policies: true,
  disciplinary: true,
  events: true,
  announcements: true,
  chat: true,
  notifications: true,
}

function membership(tenantId: string, name: string) {
  return {
    tenant_id: tenantId,
    slug: tenantId,
    name,
    default_language: 'en',
    roles: ['member'],
    branding: { primary_color: '#1f4f8f', logo_url: '' },
    modules: moduleToggles,
    profile_type: 'member',
  }
}

function memberStatement(tenantId: string, displayName: string, memberCode: string) {
  const profile = {
    id: `profile-${tenantId}`,
    tenant_id: tenantId,
    user_id: 'user-member-1',
    member_code: memberCode,
    first_name: displayName.split(' ')[0],
    last_name: 'Member',
    display_name: displayName,
    email: 'member@example.org',
    phone: null,
    status: 'active',
    joined_at: '2026-01-10T09:00:00Z',
    created_at: '2026-01-10T09:00:00Z',
    updated_at: '2026-01-10T09:00:00Z',
  }

  return {
    profile,
    summary: {
      profile,
      total_expected: '120.00',
      total_paid: '45.00',
      total_balance: '75.00',
      contribution_count: 1,
    },
    contributions: [
      {
        id: `contribution-${tenantId}`,
        tenant_id: tenantId,
        membership_profile_id: profile.id,
        year: 2026,
        expected_amount: '120.00',
        paid_amount: '45.00',
        balance: '75.00',
        currency: 'EUR',
        status: 'partial',
        due_date: null,
        created_at: '2026-01-10T09:00:00Z',
        updated_at: '2026-01-10T09:00:00Z',
      },
    ],
  }
}

async function mockMemberJourney(page: Page, options: { multipleTenants?: boolean; selectedTenantId?: string } = {}) {
  const memberships = options.multipleTenants
    ? [
        membership('tenant-alpha', 'Alpha Association'),
        membership('tenant-river', 'River Association'),
      ]
    : [membership('tenant-alpha', 'Alpha Association')]
  const initialTenantId = options.selectedTenantId ?? 'tenant-alpha'
  let currentTenantId = initialTenantId
  const unsafeRequests: string[] = []
  const statementTokens: string[] = []

  // Personal self-service reads stay inside the member's own records.
  const personalSelfServicePaths = new Set([
    '/api/v1/contributions/receipt-declarations/me',
  ])
  // Global failure telemetry is append-only diagnostics open to any authenticated
  // user; the backend owns that policy, not the member's navigation boundary.
  const globalDiagnosticPaths = new Set([
    '/api/v1/admin/audit/operation-journal/failures',
  ])

  await page.addInitScript(({ tenantId }) => {
    if (!window.localStorage.getItem('access_token')) {
      window.localStorage.setItem('access_token', `member-token-${tenantId}`)
    }
    if (!window.localStorage.getItem('selected_tenant_id')) {
      window.localStorage.setItem('selected_tenant_id', tenantId)
    }
  }, { tenantId: initialTenantId })

  page.on('request', (request) => {
    const url = new URL(request.url())
    if (url.origin !== 'http://localhost:8000') return
    if (personalSelfServicePaths.has(url.pathname) || globalDiagnosticPaths.has(url.pathname)) return
    if (
      url.pathname === '/api/v1/memberships/' ||
      url.pathname.startsWith('/api/v1/contributions') ||
      url.pathname.startsWith('/api/v1/admin')
    ) {
      unsafeRequests.push(url.pathname)
    }
  })

  await page.route('http://localhost:8000/api/v1/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    const { pathname } = url

    if (pathname === '/api/v1/auth/me' && request.method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'user-member-1',
          email: 'member@example.org',
          display_name: 'Member User',
          preferred_language: 'en',
          status: 'active',
          tenant_id: currentTenantId,
          roles: ['member'],
          last_login_at: null,
          memberships,
        }),
      })
      return
    }

    if (pathname === '/api/v1/auth/switch-tenant' && request.method() === 'POST') {
      const payload = request.postDataJSON() as { tenant_id: string }
      currentTenantId = payload.tenant_id
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: `member-token-${currentTenantId}`,
          token_type: 'bearer',
          expires_in: 3600,
          tenant_id: currentTenantId,
          user_id: 'user-member-1',
          memberships,
        }),
      })
      return
    }

    if (pathname === '/api/v1/memberships/me/statement' && request.method() === 'GET') {
      statementTokens.push(request.headers().authorization ?? '')
      const isRiverTenant = currentTenantId === 'tenant-river'
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          memberStatement(
            currentTenantId,
            isRiverTenant ? 'River Member' : 'Alpha Member',
            isRiverTenant ? 'R-100' : 'A-100',
          ),
        ),
      })
      return
    }

    if (pathname === '/api/v1/contributions/receipt-declarations/me' && request.method() === 'GET') {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
      return
    }

    if (
      (pathname === '/api/v1/documents/' ||
        pathname === '/api/v1/announcements/active' ||
        pathname === '/api/v1/events/public') &&
      request.method() === 'GET'
    ) {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
      return
    }

    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: `Unexpected request: ${request.method()} ${pathname}` }),
    })
  })

  return { statementTokens, unsafeRequests }
}

test.describe('Member role journey security', () => {
  test('shows only the member personal statement and never requests tenant finance data', async ({ page }) => {
    const { unsafeRequests } = await mockMemberJourney(page)

    await page.goto('/members/profile')

    await expect(page.getByRole('heading', { name: 'My profile and contribution statement' })).toBeVisible()
    await expect(page.getByText('Alpha Member')).toBeVisible()
    await expect(page.getByText("This area never exposes another member's financial data.")).toBeVisible()
    await expect(page.locator('aside a[href="/finance"]')).toHaveCount(0)
    await expect(page.locator('aside a[href="/admin/members"]')).toHaveCount(0)
    expect(unsafeRequests).toEqual([])
  })

  test('redirects a member away from finance and administration routes before protected views load', async ({ page }) => {
    const { unsafeRequests } = await mockMemberJourney(page)

    await page.goto('/finance')
    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByRole('heading', { name: 'Welcome back, Member User' })).toBeVisible()

    await page.goto('/admin/members')
    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByRole('heading', { name: 'Welcome back, Member User' })).toBeVisible()
    expect(unsafeRequests).toEqual([])
  })

  test('uses the active tenant token for the personal statement and never requests tenant finance data', async ({ page }) => {
    // The inline shell tenant switcher was intentionally removed in the responsive
    // navigation overhaul; a multi-tenant member selects the tenant at sign-in and
    // every personal statement must carry the token issued for that tenant.
    const { statementTokens, unsafeRequests } = await mockMemberJourney(page, {
      multipleTenants: true,
      selectedTenantId: 'tenant-river',
    })

    await page.goto('/members/profile')
    await expect(page.getByText('River Member')).toBeVisible()
    expect(statementTokens.at(-1)).toBe('Bearer member-token-tenant-river')
    expect(unsafeRequests).toEqual([])
  })
})
