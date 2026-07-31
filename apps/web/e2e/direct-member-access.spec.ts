import { expect, test, type Page } from '@playwright/test'

const modules = { membership: true, contributions: true, policies: true, disciplinary: true, events: true, announcements: true, chat: true, notifications: true }

async function mockSecretarySession(page: Page, members: unknown[] = []) {
  const memberRows = [...members] as Record<string, unknown>[]
  await page.addInitScript(() => localStorage.setItem('access_token', 'secretary-token'))
  await page.route('http://localhost:8000/api/v1/**', async (route) => {
    const pathname = new URL(route.request().url()).pathname
    if (pathname === '/api/v1/auth/me') {
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({
        id: 'secretary-1', email: 'secretary@example.org', display_name: 'Secrétaire générale', preferred_language: 'fr', status: 'active', tenant_id: 'tenant-alpha', roles: ['secretary_general'], last_login_at: null,
        memberships: [{ tenant_id: 'tenant-alpha', slug: 'alpha', name: 'Association Alpha', default_language: 'fr', roles: ['secretary_general'], branding: { primary_color: '#1f4f8f', logo_url: '' }, modules, profile_type: 'staff' }],
      }) })
    }
    if (pathname === '/api/v1/memberships/' && route.request().method() === 'GET') {
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(memberRows) })
    }
    if (pathname === '/api/v1/memberships/member-1' && route.request().method() === 'PATCH') {
      memberRows[0] = { ...memberRows[0], status: 'suspended' }
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(memberRows[0]),
      })
    }
    return route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: `Unexpected request: ${pathname}` }) })
  })
}

test('shows the default provisional password in the secretary member form', async ({ page, browserName }) => {
  await mockSecretarySession(page)
  await page.goto('/members/manage')

  const addMemberButton = page.getByRole('button', { name: 'Ajouter un membre' })
  await expect(addMemberButton).toHaveCount(1)
  await addMemberButton.click()

  const directAccessSwitch = page.getByLabel('Créer un accès immédiat au membre', { exact: true })
  await expect(directAccessSwitch).toHaveCount(1)
  await directAccessSwitch.check()

  const countrySelect = page.getByTestId('member-phone-country')
  await expect(countrySelect).toHaveCount(1)
  await expect(countrySelect).toHaveValue('DE')
  await countrySelect.selectOption('FR')
  await expect(page.getByText('Le code membre est généré automatiquement à partir du nom, du suffixe COMBIS et d’un numéro unique.')).toBeVisible()
  await page.getByLabel('Prénom', { exact: true }).fill('Marie')
  await page.getByLabel('Nom de famille', { exact: true }).fill('Durand')
  await page.getByLabel("Nom d'affichage", { exact: true }).fill('Marie Durand')
  await page.getByLabel('E-mail', { exact: true }).fill('marie@example.org')
  await page.getByLabel('Numéro de téléphone', { exact: true }).fill('612345678')

  const temporaryPassword = page.getByTestId('direct-temporary-password')
  await expect(temporaryPassword).toHaveValue('CombisPass#')
  await expect(page.getByTestId('direct-temporary-password-help')).toContainText('Prérempli avec CombisPass#')
  await page.getByTestId('direct-temporary-password-visibility').click()
  await expect(temporaryPassword).toHaveAttribute('type', 'text')
  await page.getByRole('button', { name: 'Vérifier les informations' }).click()
  await expect(page.getByText('Vérifiez attentivement ces informations avant la création définitive du membre.')).toBeVisible()
  await expect(page.getByText('+33612345678', { exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Confirmer et créer le membre' })).toBeVisible()
  await page.screenshot({ path: `artifacts/role-workflow-proof/2026-07-28/${browserName}-direct-member-access-default-password.png`, fullPage: true })
})

test('highlights invalid member fields and displays a validation notification', async ({ page }) => {
  await mockSecretarySession(page)
  await page.goto('/members/manage')
  await page.getByRole('button', { name: 'Ajouter un membre' }).click()
  await page.getByRole('button', { name: 'Vérifier les informations' }).click()

  await expect(page.getByText('Corrigez les champs signalés en rouge avant de continuer.')).toBeVisible()
  await expect(page.getByLabel('Prénom', { exact: true })).toHaveClass(/is-invalid/)
  await expect(page.getByLabel('Nom de famille', { exact: true })).toHaveClass(/is-invalid/)
  await expect(page.getByLabel("Nom d'affichage", { exact: true })).toHaveClass(/is-invalid/)
})

test('secretary can pause a member with legible stacked mobile actions', async ({ page, browserName }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await mockSecretarySession(page, [{
    id: 'member-1', tenant_id: 'tenant-alpha', user_id: null, member_code: 'IMP-0041',
    first_name: 'Mireille', last_name: 'Salomon', display_name: 'Mireille Salomon',
    email: 'mireille@example.org', phone: '+49123456789', status: 'active', membership_type: 'individual',
    joined_at: '2026-01-10T09:00:00Z', created_at: '2026-01-10T09:00:00Z', updated_at: '2026-01-10T09:00:00Z',
  }])
  await page.goto('/members/manage')

  const edit = page.getByRole('button', { name: 'Modifier le membre' })
  const pause = page.getByRole('button', { name: 'Mettre en pause' })
  const remove = page.getByRole('button', { name: 'Supprimer le membre' })
  await expect(edit).toBeVisible()
  await expect(pause).toBeVisible()
  await expect(remove).toBeVisible()
  await expect(pause).toHaveCSS('white-space', 'normal')

  const editBox = await edit.boundingBox()
  const pauseBox = await pause.boundingBox()
  const removeBox = await remove.boundingBox()
  expect(pauseBox?.y).toBeGreaterThan(editBox?.y ?? 0)
  expect(removeBox?.y).toBeGreaterThan(pauseBox?.y ?? 0)

  await pause.click()
  await expect(page.getByRole('button', { name: 'Réactiver le membre' })).toBeVisible()
  await page.screenshot({ path: `artifacts/role-workflow-proof/2026-07-29/${browserName}-member-pause-mobile.png`, fullPage: true })
})
