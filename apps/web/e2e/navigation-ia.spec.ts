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

function makeMe(role: string, capabilities?: string[]) {
  return {
    id: 'user-nav-1',
    email: 'nav@demo.org',
    display_name: 'Nav Demo',
    preferred_language: 'en',
    status: 'active',
    tenant_id: 'tenant-demo-1',
    roles: [role],
    ...(capabilities ? { capabilities } : {}),
    last_login_at: null,
    memberships: [
      {
        tenant_id: 'tenant-demo-1',
        slug: 'demo',
        name: 'Demo Organization',
        roles: [role],
        ...(capabilities ? { capabilities } : {}),
        branding: { primary_color: '#1f4f8f', logo_url: '' },
        modules: moduleToggles,
        profile_type: role === 'member' ? 'member' : 'staff',
      },
    ],
  }
}

async function mockNavigation(page: Page, role: string, capabilities?: string[]) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-nav-token')
    window.localStorage.setItem('preferred_locale', 'en')
  })

  await page.route('**/api/v1/**', async (route) => {
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'No navigation mock for this request' }),
    })
  })

  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeMe(role, capabilities)),
    })
  })

  for (const path of ['**/api/v1/memberships/', '**/api/v1/documents/', '**/api/v1/announcements/active', '**/api/v1/events/public']) {
    await page.route(path, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
  }
}

test.describe('Navigation and information architecture', () => {
  test('more is a real navigation catalog grouped by domain', async ({ page }) => {
    await mockNavigation(page, 'treasurer')
    await page.goto('/dashboard')
    await page.getByRole('button', { name: 'More' }).click()
    await expect(page).toHaveURL(/\/more$/)

    await expect(page.getByRole('heading', { name: 'All destinations' })).toBeVisible()
    const catalog = page.getByRole('main')
    await expect(catalog.getByText('Management', { exact: true })).toBeVisible()
    await expect(catalog.getByText('Governance', { exact: true })).toBeVisible()
    await expect(catalog.getByText('Community', { exact: true })).toBeVisible()
    await expect(catalog.getByText('Account', { exact: true })).toBeVisible()

    // The catalog links to authorised workspaces, it never forwards silently.
    await expect(catalog.getByRole('link', { name: /Finance workspace/ }).first()).toBeVisible()
    await expect(catalog.getByRole('link', { name: 'My profile' }).first()).toBeVisible()
    await expect(catalog.getByRole('link', { name: 'Account security' }).first()).toBeVisible()
  })

  test('office bottom navigation holds high-value destinations', async ({ page }) => {
    await mockNavigation(page, 'treasurer')
    await page.goto('/dashboard')

    const bottomNav = page.locator('nav.bottom-nav')
    for (const label of ['Home', 'Tasks', 'Search', 'Notifications', 'More']) {
      await expect(bottomNav.getByRole('button', { name: label })).toBeVisible()
    }
    // Profile and Security must not permanently occupy primary slots.
    await expect(bottomNav.getByRole('button', { name: 'Profile' })).toHaveCount(0)
    await expect(bottomNav.getByRole('button', { name: 'Security' })).toHaveCount(0)
  })

  test('profile and security live in the account surface', async ({ page }) => {
    await mockNavigation(page, 'treasurer')
    await page.goto('/dashboard')

    await page.getByRole('button', { name: 'Account' }).click()
    const menu = page.locator('.dropdown-menu')
    await expect(menu.getByRole('link', { name: 'My profile' })).toBeVisible()
    await expect(menu.getByRole('link', { name: 'Account security' })).toBeVisible()
  })

  test('more survives 320px width without destructive overflow', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 640 })
    await mockNavigation(page, 'treasurer')

    for (const target of ['/more', '/tasks']) {
      await page.goto(target)
      const overflow = await page.evaluate(
        () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
      )
      expect(overflow).toBeLessThanOrEqual(1)
    }
  })

  test('bottom navigation is keyboard operable', async ({ page }) => {
    await mockNavigation(page, 'treasurer')
    await page.goto('/dashboard')

    const more = page.locator('nav.bottom-nav').getByRole('button', { name: 'More' })
    await more.focus()
    await page.keyboard.press('Enter')
    await expect(page).toHaveURL(/\/more$/)

    const tasks = page.locator('nav.bottom-nav').getByRole('button', { name: 'Tasks' })
    await page.goto('/more')
    await tasks.focus()
    await page.keyboard.press('Enter')
    await expect(page).toHaveURL(/\/tasks$/)
  })

  test('member navigation stays compact and account-scoped', async ({ page }) => {
    await mockNavigation(page, 'member')
    await page.goto('/dashboard')

    const bottomNav = page.locator('nav.bottom-nav')
    for (const label of ['Home', 'Chat', 'Notifications', 'More']) {
      await expect(bottomNav.getByRole('button', { name: label })).toBeVisible()
    }
    await expect(bottomNav.getByRole('button', { name: 'Tasks' })).toHaveCount(0)
    await expect(bottomNav.getByRole('button', { name: 'Search' })).toHaveCount(0)

    await bottomNav.getByRole('button', { name: 'More' }).click()
    await expect(page).toHaveURL(/\/more$/)
    await expect(page.getByRole('main').getByText('Account', { exact: true })).toBeVisible()
  })

  test('navigation follows API capabilities, not role labels', async ({ page }) => {
    await mockNavigation(page, 'member', [
      'membership:self_read',
      'membership:tenant_read',
      'finance:self_read',
      'finance:tenant_read',
      'finance:write',
      'documents:read',
      'policies:read',
      'disciplinary:self_read',
      'events:read',
      'announcements:read',
      'chat:use',
    ])
    await page.goto('/dashboard')

    await expect(page.locator('a[href="/finance"]').first()).toBeVisible()
    await expect(page.getByTestId('dashboard-workspace-focus')).toBeVisible()
  })
})
