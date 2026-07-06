import { test, expect, type Page } from '@playwright/test'

function makeAdminMeResponse() {
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
}

async function mockAdminOnboarding(page: Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-admin-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeAdminMeResponse()),
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

test.describe('Admin onboarding wizard', () => {
  test('shows the first-run setup path, seed commands, and guided launch links', async ({ page }) => {
    await mockAdminOnboarding(page)

    await page.goto('/admin/onboarding')

    await expect(page).toHaveURL(/\/admin\/onboarding$/)
    await expect(page.getByTestId('admin-onboarding-kicker')).toHaveText('First-run setup')
    await expect(page.getByTestId('admin-onboarding-title')).toHaveText('Onboarding wizard')
    await expect(page.getByTestId('admin-onboarding-checklist')).toContainText('Launch checklist')
    await expect(page.getByTestId('admin-onboarding-progress')).toHaveText('0%')
    await expect(page.getByTestId('admin-onboarding-next-step')).toContainText('Confirm tenant branding')
    await expect(page.getByTestId('admin-onboarding-seed-bash')).toContainText('./seed/seed-multi-tenant.sh')
    await expect(page.getByTestId('admin-onboarding-seed-powershell')).toContainText('.\\seed\\seed-multi-tenant.ps1')
    await expect(page.getByTestId('admin-onboarding-links')).toContainText('Tenant settings')
    await expect(page.getByTestId('admin-onboarding-links')).toContainText('Tenant operations')
    await expect(page.locator('aside.admin-sidebar').getByRole('link', { name: 'Onboarding wizard' })).toBeVisible()
    await expect(page.getByTestId('admin-onboarding-health-button')).toHaveAttribute('href', '/admin/health')
  })
})
