import { test, expect } from '@playwright/test'

const meResponse = {
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

async function mockAuthenticatedDashboard(page: import('@playwright/test').Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-demo-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(meResponse),
    })
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/memberships/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })
}

test.describe('Dashboard onboarding', () => {
  test('shows the first-run checklist for a tenant still in setup mode', async ({ page }) => {
    await mockAuthenticatedDashboard(page)
    await page.goto('/dashboard')

    await expect(page).toHaveURL(/dashboard/)
    await expect(page.getByTestId('tenant-onboarding')).toBeVisible()
    await expect(page.getByText('First-run checklist')).toBeVisible()
    await expect(page.getByText('This tenant is still in setup mode')).toBeVisible()
    await expect(page.getByText('Upload the first document')).toBeVisible()
    await expect(page.getByText('Add or import members')).toBeVisible()
    await expect(page.getByText('Quick actions')).toBeVisible()
    await expect(page.getByTestId('tenant-onboarding-progress')).toContainText('0%')
  })
})
