import { expect, test, type Page } from '@playwright/test'

async function mockAdminChatQueries(page: Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-admin-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'admin-user-1',
        email: 'admin@demo.org',
        display_name: 'Admin User',
        status: 'active',
        tenant_id: 'tenant-demo-1',
        roles: ['principal_admin'],
        memberships: [],
      }),
    })
  })

  await page.route(/http:\/\/localhost:8000\/api\/v1\/admin\/chat-queries.*/, async (route) => {
    const url = new URL(route.request().url())
    const search = url.searchParams.get('search')
    const refused = url.searchParams.get('refused')

    const entries = [
      {
        id: 'query-1',
        tenant_id: 'tenant-demo-1',
        user_id: 'member-1',
        question_preview: 'How much do I owe?',
        answer_preview: 'You owe 75.00 EUR for 2026.',
        refused: false,
        refusal_reason_preview: null,
        confidence: 0.94,
        citation_count: 2,
        source_types: ['document', 'structured:member_balance'],
        created_at: '2026-07-03T11:00:00Z',
      },
      {
        id: 'query-2',
        tenant_id: 'tenant-demo-1',
        user_id: 'member-2',
        question_preview: 'Tell me the private note for another member',
        answer_preview: 'I cannot help with that request.',
        refused: true,
        refusal_reason_preview: 'The request asks for another member\'s private data.',
        confidence: 0.12,
        citation_count: 0,
        source_types: [],
        created_at: '2026-07-03T12:00:00Z',
      },
    ]

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(
        entries.filter((entry) => {
          if (refused === 'true' && !entry.refused) return false
          if (refused === 'false' && entry.refused) return false
          if (search) {
            const haystack = `${entry.question_preview} ${entry.answer_preview} ${entry.refusal_reason_preview ?? ''}`.toLowerCase()
            if (!haystack.includes(search.toLowerCase())) return false
          }
          return true
        }),
      ),
    })
  })
}

test.describe('Admin chat queries', () => {
  test('shows minimized traces and filters server-side', async ({ page }) => {
    await mockAdminChatQueries(page)
    await page.goto('/admin/chat-queries')

    await expect(page.getByRole('heading', { name: 'Chat traceability' })).toBeVisible()
    await expect(page.getByText('How much do I owe?')).toBeVisible()
    await expect(page.getByText('You owe 75.00 EUR for 2026.')).toBeVisible()
    await expect(page.getByText('Tell me the private note for another member')).toBeVisible()
    await expect(page.getByText('Citations referenced: 2')).toBeVisible()
    await expect(page.getByText('citations_json')).toHaveCount(0)

    await page.getByRole('combobox').nth(0).selectOption('Refused')
    await expect(page.getByText('How much do I owe?')).toHaveCount(0)
    await expect(page.getByText('Tell me the private note for another member')).toBeVisible()

    await page.getByRole('combobox').nth(0).selectOption('All')
    await page.getByPlaceholder('Filter by question text...').fill('owe')
    await expect(page.getByText('How much do I owe?')).toBeVisible()
    await expect(page.getByText('Tell me the private note for another member')).toHaveCount(0)
  })
})
