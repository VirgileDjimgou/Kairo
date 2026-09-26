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
    id: 'user-att-1',
    email: 'att@demo.org',
    display_name: 'Attention Demo',
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

const treasurerAttention = {
  items: [
    {
      id: 'attention.overdueHandovers',
      priority: 'urgent',
      category: 'finance',
      title_key: 'attention.overdueHandovers',
      count: 2,
      target_path: '/finance',
    },
    {
      id: 'attention.pendingReceipts',
      priority: 'attention',
      category: 'finance',
      title_key: 'attention.pendingReceipts',
      count: 3,
      target_path: '/finance',
    },
  ],
}

const memberAttention = {
  items: [
    {
      id: 'attention.myBalance',
      priority: 'attention',
      category: 'account',
      title_key: 'attention.myBalance',
      count: 1,
      target_path: '/members/profile',
    },
    {
      id: 'attention.unreadNotifications',
      priority: 'informational',
      category: 'account',
      title_key: 'attention.unreadNotifications',
      count: 4,
      target_path: '/notifications',
    },
  ],
}

async function mockAttention(page: Page, role: string, attention: object) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-attention-token')
    window.localStorage.setItem('preferred_locale', 'en')
  })

  await page.route('**/api/v1/**', async (route) => {
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'No attention mock for this request' }),
    })
  })

  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeMe(role)),
    })
  })

  await page.route('**/api/v1/attention', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(attention),
    })
  })

  for (const path of ['**/api/v1/memberships/', '**/api/v1/documents/', '**/api/v1/announcements/active', '**/api/v1/events/public']) {
    await page.route(path, async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
    })
  }
}

test.describe('Role-aware action center', () => {
  test('dashboard answers what needs my attention with actionable cards', async ({ page }) => {
    await mockAttention(page, 'treasurer', treasurerAttention)
    await page.goto('/dashboard')

    const center = page.getByTestId('attention-center')
    await expect(center.getByRole('heading', { name: 'What needs my attention now?' })).toBeVisible()
    await expect(center.getByTestId('attention-item-attention.overdueHandovers')).toContainText('Cash handovers overdue')
    await expect(center.getByTestId('attention-item-attention.overdueHandovers')).toContainText('2')
    await expect(center.getByTestId('attention-item-attention.overdueHandovers')).toContainText('Urgent')
    await expect(center.getByTestId('attention-item-attention.pendingReceipts')).toContainText('3')

    await center.getByTestId('attention-item-attention.pendingReceipts').click()
    await expect(page).toHaveURL(/\/finance$/)
  })

  test('member attention stays personal', async ({ page }) => {
    await mockAttention(page, 'member', memberAttention)
    await page.goto('/dashboard')

    const center = page.getByTestId('attention-center')
    await expect(center.getByTestId('attention-item-attention.myBalance')).toBeVisible()
    await expect(center.getByTestId('attention-item-attention.unreadNotifications')).toContainText('4')
    await expect(center.getByTestId('attention-item-attention.pendingReceipts')).toHaveCount(0)
    await expect(center.getByTestId('attention-item-attention.outstandingBalances')).toHaveCount(0)
    await expect(center.getByTestId('attention-item-attention.overdueHandovers')).toHaveCount(0)
  })

  test('empty attention state is meaningful', async ({ page }) => {
    await mockAttention(page, 'treasurer', { items: [] })
    await page.goto('/tasks')

    const center = page.getByTestId('attention-center')
    await expect(center.getByText('Nothing needs your attention right now.')).toBeVisible()
    await expect(center.getByRole('link')).toHaveCount(0)
  })

  test('action center renders on the tasks destination too', async ({ page }) => {
    await mockAttention(page, 'treasurer', treasurerAttention)
    await page.goto('/tasks')

    await expect(page.getByTestId('attention-center').getByTestId('attention-item-attention.pendingReceipts')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'My tasks' })).toBeVisible()
  })
})
