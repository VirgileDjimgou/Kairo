import { expect, test, type Page } from '@playwright/test'

function makeMeResponse(role: string, displayName: string) {
  return {
    id: `user-${role}-1`,
    email: `${role}@demo.org`,
    display_name: displayName,
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

async function mockChatPage(page: Page, role: string, displayName: string) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-chat-token')
  })

  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeMeResponse(role, displayName)),
    })
  })

  await page.route('**/api/v1/chat/query', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        answer: 'Grounded answer from authorized sources.',
        citations: [],
        source_types: ['structured:publication_context'],
        confidence: 0.95,
        refused: false,
        refusal_reason: null,
      }),
    })
  })
}

test.describe('Role-aware chat expansion', () => {
  test('secretary general sees publication-focused prompts and source badges', async ({ page }) => {
    await mockChatPage(page, 'secretary_general', 'Secretary General')
    await page.goto('/chat')

    await expect(page.getByRole('heading', { name: 'Grounded organizational assistant' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Show the official publication context.' })).toBeVisible()
    await page.getByRole('button', { name: 'Show the official publication context.' }).click()
    await expect(page.locator('textarea')).toHaveValue('Show the official publication context.')
    await page.getByRole('button', { name: 'Ask question' }).click()

    await expect(page.getByText('Structured publication context')).toBeVisible()
    await expect(page.getByText('Grounded answer from authorized sources.')).toBeVisible()
  })

  test('sports manager sees sports schedule prompts', async ({ page }) => {
    await mockChatPage(page, 'sports_manager', 'Sports Manager')
    await page.goto('/chat')

    await expect(page.getByRole('button', { name: 'Show the sports schedule.' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'What is the next sports event?' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Which training sessions are upcoming?' })).toBeVisible()
  })
})
