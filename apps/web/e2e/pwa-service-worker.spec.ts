import { expect, test, type Page } from '@playwright/test'

const memberMe = {
  id: 'user-member-pwa-1',
  email: 'member@demo.org',
  display_name: 'Awa Ngono',
  preferred_language: 'fr',
  status: 'active',
  tenant_id: 'tenant-demo-1',
  roles: ['member'],
  last_login_at: null,
  memberships: [
    {
      tenant_id: 'tenant-demo-1',
      slug: 'demo',
      name: 'Demo Organization',
      roles: ['member'],
      branding: { primary_color: '#1f4f8f', logo_url: '' },
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
      profile_type: 'member',
    },
  ],
}

async function installAuthenticatedMember(page: Page): Promise<void> {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-pwa-service-worker-token')
  })
  await page.route('**/api/v1/**', async (route) => {
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'No PWA mock for this request' }),
    })
  })
  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(memberMe),
    })
  })
  await page.route('**/api/v1/notifications/inbox', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ items: [], unread_count: 0 }),
    })
  })
}

async function dispatchNavigate(page: Page, target: string): Promise<void> {
  await page.evaluate((value) => {
    navigator.serviceWorker.dispatchEvent(
      new MessageEvent('message', { data: { type: 'kairo:navigate', target: value } }),
    )
  }, target)
}

test('a notification click navigates an authenticated client to the exact target route', async ({ page }) => {
  await installAuthenticatedMember(page)
  await page.goto('/more')
  await expect(page).toHaveURL(/\/more$/)

  await dispatchNavigate(page, '/notifications')

  await expect(page).toHaveURL(/\/notifications$/)
  await expect(page.getByRole('heading', { level: 1, name: /Boîte de réception|Inbox/ })).toBeVisible()
})

test('unsafe notification targets are ignored instead of navigating externally', async ({ page }) => {
  await installAuthenticatedMember(page)
  await page.goto('/more')
  await expect(page).toHaveURL(/\/more$/)

  await dispatchNavigate(page, 'https://evil.example/collect')
  await dispatchNavigate(page, '//evil.example/collect')
  await dispatchNavigate(page, 'javascript:alert(1)')
  await dispatchNavigate(page, '')

  await expect(page).toHaveURL(/\/more$/)
})

test('an unauthenticated notification target survives the login redirect', async ({ page }) => {
  await page.goto('/login')
  await expect(page).toHaveURL(/\/login$/)

  await dispatchNavigate(page, '/notifications')

  await expect(page).toHaveURL((url) => url.pathname === '/login' && url.searchParams.get('redirect') === '/notifications')
})
