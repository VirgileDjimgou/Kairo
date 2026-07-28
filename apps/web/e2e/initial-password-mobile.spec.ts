import { expect, test } from '@playwright/test'

const modules = { membership: true, contributions: true, policies: true, disciplinary: true, events: true, announcements: true, chat: true, notifications: true }

test.describe('Initial member password mobile flow', () => {
  test.use({ viewport: { width: 390, height: 844 }, isMobile: true })

  test('requires and completes a personal password before member access', async ({ page, browserName }) => {
    let passwordChanged = false
    await page.addInitScript(() => localStorage.setItem('access_token', 'temporary-member-token'))
    await page.route('http://localhost:8000/api/v1/**', async (route) => {
      const pathname = new URL(route.request().url()).pathname
      if (pathname === '/api/v1/auth/me') {
        return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({
          id: 'member-1', email: 'member-internal@member.kairo.local', display_name: 'Marie Sans Email', preferred_language: 'fr', status: 'active', tenant_id: 'tenant-alpha', roles: ['member'], last_login_at: null,
          password_change_required: !passwordChanged,
          memberships: [{ tenant_id: 'tenant-alpha', slug: 'alpha', name: 'Association Alpha', default_language: 'fr', roles: ['member'], branding: { primary_color: '#1f4f8f', logo_url: '' }, modules, profile_type: 'member' }],
        }) })
      }
      if (pathname === '/api/v1/auth/change-initial-password') {
        passwordChanged = true
        return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ message: 'Password has been updated' }) })
      }
      if (pathname === '/api/v1/memberships/me') return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({}) })
      return route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: `Unexpected request: ${pathname}` }) })
    })

    await page.goto('/initial-password')
    await expect(page.getByRole('heading', { name: 'Choisissez votre mot de passe personnel' })).toBeVisible()
    await expect(page.getByText('Aucun e-mail ni SMS n’est nécessaire.')).toBeVisible()
    await page.screenshot({ path: `artifacts/role-workflow-proof/2026-07-28/${browserName}-initial-password-mobile.png`, fullPage: true })
    expect(await page.locator('.initial-password-card').evaluate((element) => element.scrollWidth <= document.documentElement.clientWidth)).toBe(true)

    await page.getByLabel('Nouveau mot de passe', { exact: true }).fill('PersonalPass123!')
    await page.getByLabel('Confirmer le nouveau mot de passe', { exact: true }).fill('PersonalPass123!')
    await page.getByRole('button', { name: 'Enregistrer mon mot de passe' }).click()
    await expect(page).toHaveURL(/dashboard/)
  })
})
