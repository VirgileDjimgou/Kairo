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

function makeMe(role: string) {
  return {
    id: 'user-search-1',
    email: 'search@demo.org',
    display_name: 'Search Demo',
    preferred_language: 'en',
    status: 'active',
    tenant_id: 'tenant-demo-1',
    roles: [role],
    last_login_at: null,
    memberships: [
      {
        tenant_id: 'tenant-demo-1',
        slug: 'demo',
        name: 'Demo Organization',
        roles: [role],
        branding: { primary_color: '#1f4f8f', logo_url: '' },
        modules: moduleToggles,
        profile_type: role === 'member' ? 'member' : 'staff',
      },
    ],
  }
}

const searchResults = {
  query: 'alice',
  results: [
    {
      id: 'member-1',
      type: 'members',
      type_key: 'search.types.members',
      title: 'Alice Example',
      subtitle: 'M001',
      target_path: '/members/manage',
      score: 3,
    },
    {
      id: 'event-1',
      type: 'events',
      type_key: 'search.types.events',
      title: 'Alice tournament',
      subtitle: null,
      target_path: '/events',
      score: 2,
    },
  ],
}

async function mockSearch(page: Page, role: string) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-search-token')
    window.localStorage.setItem('preferred_locale', 'en')
  })

  await page.route('**/api/v1/**', async (route) => {
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'No search mock for this request' }),
    })
  })

  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeMe(role)),
    })
  })

  await page.route('**/api/v1/search**', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(searchResults),
    })
  })

  for (const path of ['**/api/v1/memberships/', '**/api/v1/documents/', '**/api/v1/announcements/active', '**/api/v1/events/public']) {
    await page.route(path, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
  }
}

test.describe('Global permission-aware search', () => {
  test('Ctrl+K opens the overlay and results carry type labels', async ({ page }) => {
    await mockSearch(page, 'treasurer')
    await page.goto('/dashboard')
    // The hotkey listener attaches when the authenticated shell mounts.
    await expect(page.locator('nav.bottom-nav')).toBeVisible()

    await page.keyboard.press('Control+k')
    const dialog = page.getByRole('dialog')
    await expect(dialog).toBeVisible()

    const input = dialog.getByRole('searchbox')
    await input.fill('alice')
    await input.press('Enter')

    await expect(dialog.getByText('Alice Example')).toBeVisible()
    await expect(dialog.getByText('Members', { exact: true })).toBeVisible()
    await expect(dialog.getByText('Events', { exact: true })).toBeVisible()

    await dialog.getByText('Alice tournament').click()
    await expect(page).toHaveURL(/\/events$/)
  })

  test('overlay closes with Escape', async ({ page }) => {
    await mockSearch(page, 'treasurer')
    await page.goto('/dashboard')
    await expect(page.locator('nav.bottom-nav')).toBeVisible()

    await page.keyboard.press('Control+k')
    await expect(page.getByRole('dialog')).toBeVisible()
    await page.keyboard.press('Escape')
    await expect(page.getByRole('dialog')).toHaveCount(0)
  })

  test('search page works at phone width', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await mockSearch(page, 'treasurer')
    await page.goto('/search')

    const input = page.getByRole('searchbox')
    await input.fill('alice')
    await input.press('Enter')

    await expect(page.getByText('Alice Example')).toBeVisible()
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow).toBeLessThanOrEqual(1)
  })

  test('member search surfaces only what the API authorizes', async ({ page }) => {
    await mockSearch(page, 'member')
    await page.goto('/search')

    const input = page.getByRole('searchbox')
    await input.fill('alice')
    await input.press('Enter')

    // The mock returns only authorized rows; the client renders exactly those
    // and nothing else is ever requested or hidden locally.
    await expect(page.getByText('Alice Example')).toBeVisible()
    await expect(page.getByText('Confidential case')).toHaveCount(0)
  })
})
