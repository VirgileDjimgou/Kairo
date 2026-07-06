import { expect, test, type Page } from '@playwright/test'

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

async function mockSecretaryWorkspace(page: Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-secretary-token')
  })

  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(secretaryMeResponse),
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
    await expect(page.getByText('Official records and communication workspace')).toBeVisible()
    await expect(page.getByRole('link', { name: 'Open documents' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Open announcements' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Back to portal' })).toBeVisible()
    await expect(page.getByTestId('secretary-boundaries')).toContainText('Contribution mutation and finance operations')
  })

  test('secretary general cannot enter the finance workspace route', async ({ page }) => {
    await mockSecretaryWorkspace(page)
    await page.goto('/finance')

    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByText('Quick actions')).toBeVisible()
    await expect(page.getByTestId('dashboard-workspace-focus').getByRole('link', { name: 'Open secretary workspace' })).toHaveAttribute('href', '/secretary')
    await expect(page.getByRole('link', { name: /Open secretary workspace/ })).toHaveCount(2)
    await expect(page.getByRole('link', { name: 'Go to finance workspace' })).toHaveCount(0)
  })
})
