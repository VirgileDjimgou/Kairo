import { expect, test, type Page } from '@playwright/test'

const quickActionsPattern = /Quick actions|Actions rapides|Schnellaktionen/

const secretaryMeResponse = {
  id: 'user-secretary-1',
  email: 'secretary@demo.org',
  display_name: 'Secretary General',
  status: 'active',
  tenant_id: 'tenant-demo-1',
  roles: ['secretary_general'],
  last_login_at: null,
  memberships: [
    {
      tenant_id: 'tenant-demo-1',
      slug: 'demo',
      name: 'Demo Organization',
      roles: ['secretary_general'],
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

const secretaryLimitedModulesResponse = {
  ...secretaryMeResponse,
  memberships: [
    {
      ...secretaryMeResponse.memberships[0],
      modules: {
        ...secretaryMeResponse.memberships[0].modules,
        policies: false,
        announcements: false,
      },
    },
  ],
}

async function mockSecretaryWorkspace(page: Page, response = secretaryMeResponse) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-secretary-token')
  })

  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(response),
    })
  })

  await page.route('**/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('**/api/v1/memberships/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('**/api/v1/policies/categories', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ categories: ['governance', 'communications'] }),
    })
  })

  await page.route('**/api/v1/policies/', async (route) => {
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

  await page.route('**/api/v1/announcements/', async (route) => {
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

  await page.route('**/api/v1/documents/ingestion-jobs/**', async (route) => {
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'not found' }),
    })
  })
}

test.describe('Secretary workspace', () => {
  test('secretary general sees a dedicated workspace and scoped navigation', async ({ page }) => {
    await mockSecretaryWorkspace(page)
    await page.goto('/secretary')

    await expect(page).toHaveURL(/\/secretary$/)
    await expect(page.getByTestId('secretary-overview')).toBeVisible()
    await expect(page.getByRole('heading', { name: /Official records and communication workspace|Espace des documents et de la communication officielle|Offizielle Dokumente und Kommunikationszentrale/ })).toBeVisible()
    await expect(page.locator('a[href="/secretary/documents"]').first()).toBeVisible()
    await expect(page.locator('a[href="/secretary/announcements"]').first()).toBeVisible()
    await expect(page.locator('a[href="/dashboard"]').first()).toBeVisible()
    await expect(page.getByTestId('secretary-boundaries')).toContainText(/Contribution mutation and finance operations|Mouvements de cotisations et opérations financières|Beitrags- und Finanzvorgaenge/)
  })

  test('secretary general cannot enter the finance workspace route', async ({ page }) => {
    await mockSecretaryWorkspace(page)
    await page.goto('/finance')

    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByText(quickActionsPattern)).toBeVisible()
    await expect(page.getByTestId('dashboard-workspace-focus').locator('a[href="/secretary"]').first()).toBeVisible()
    await expect(page.locator('a[href="/secretary"]').first()).toBeVisible()
    await expect(page.locator('a[href="/finance"]')).toHaveCount(0)
  })

  test('secretary workspace stays discoverable when policy and announcement modules are disabled', async ({ page }) => {
    await mockSecretaryWorkspace(page, secretaryLimitedModulesResponse)
    await page.goto('/dashboard')

    await expect(page.getByTestId('dashboard-workspace-focus').locator('a[href="/secretary"]').first()).toBeVisible()
    await expect(page.locator('a[href="/secretary"]').first()).toBeVisible()
    await expect(page.locator('a[href="/secretary/policies"]')).toHaveCount(0)
    await expect(page.locator('a[href="/secretary/announcements"]')).toHaveCount(0)

    await page.goto('/secretary')
    await expect(page).toHaveURL(/\/secretary$/)
    await expect(page.getByTestId('secretary-overview')).toBeVisible()
  })
})
