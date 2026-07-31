import { expect, test, type Page } from '@playwright/test'

const modules = { membership: true, contributions: true, policies: true, disciplinary: true, events: true, announcements: true, chat: true, notifications: true }

async function mockPresidentSession(page: Page) {
  await page.addInitScript(() => localStorage.setItem('access_token', 'president-token'))
  await page.route('http://localhost:8000/api/v1/**', async (route) => {
    const pathname = new URL(route.request().url()).pathname
    if (pathname === '/api/v1/auth/me') return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({
      id: 'president-1', email: 'president@example.org', display_name: 'Président', preferred_language: 'fr', status: 'active', tenant_id: 'tenant-alpha', roles: ['president'], last_login_at: null,
      memberships: [{ tenant_id: 'tenant-alpha', slug: 'alpha', name: 'Association Alpha', default_language: 'fr', roles: ['president'], branding: { primary_color: '#1f4f8f', logo_url: '' }, modules, profile_type: 'staff' }],
    }) })
    if (pathname === '/api/v1/admin/audit/operation-journal') return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([
      { id: 'event-1', tenant_id: 'tenant-alpha', actor_user_id: 'president-1', actor: { display_name: 'Marie Durand', email: 'president@example.org', roles: ['president'] }, module_key: 'membership', action: 'create', entity_type: 'membership_profile', entity_id: 'member-1', details: { member_code: 'DURAND-COMBIS-42' }, created_at: '2026-07-29T10:00:00Z' },
      { id: 'event-2', tenant_id: 'tenant-alpha', actor_user_id: 'treasurer-1', actor: { display_name: 'Paul Martin', email: 'treasurer@example.org', roles: ['treasurer'] }, module_key: 'operations', action: 'operation_failed', entity_type: 'client_request', entity_id: null, details: { method: 'POST', path: '/api/v1/contributions/', status_code: 422 }, created_at: '2026-07-29T10:01:00Z' },
    ]) })
    return route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: `Unexpected request: ${pathname}` }) })
  })
}

test('shows the president operational journal with successful and failed operations', async ({ page, browserName }) => {
  await mockPresidentSession(page)
  await page.goto('/operation-journal')
  await expect(page.getByRole('heading', { name: 'Journal des opérations' })).toBeVisible()
  await expect(page.getByText('Opération non réalisée')).toBeVisible()
  await expect(page.getByText('Paul Martin')).toBeVisible()
  await expect(page.getByText('Trésorier')).toBeVisible()
  await expect(page.getByText('certaines informations doivent être corrigées')).toBeVisible()
  await page.screenshot({ path: `artifacts/role-workflow-proof/2026-07-29/${browserName}-operation-journal-president.png`, fullPage: true })
})
