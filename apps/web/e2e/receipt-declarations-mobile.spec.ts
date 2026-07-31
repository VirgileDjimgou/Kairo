import { expect, test, type Page } from '@playwright/test'

const proofDirectory = 'artifacts/role-workflow-proof/2026-07-28'
const modules = { membership: true, contributions: true, policies: true, disciplinary: true, events: true, announcements: true, chat: true, notifications: true }

function declaration(status: 'submitted' | 'validated' = 'submitted') {
  return { id: 'receipt-1', tenant_id: 'tenant-alpha', membership_profile_id: 'member-1', declarant_user_id: 'office-user', declarant_role_code: 'vice_president', amount: '20.00', currency: 'EUR', received_at: '2026-07-28T10:00:00Z', payment_method: 'cash', reference: null, note: 'Contribution remise en espèces.', evidence_json: null, status, processed_amount: status === 'validated' ? '20.00' : null, processing_note: null, contribution_record_id: status === 'validated' ? 'contribution-1' : null, payment_id: status === 'validated' ? 'payment-1' : null, created_at: '2026-07-28T10:00:00Z', updated_at: '2026-07-28T10:00:00Z', submitted_at: '2026-07-28T10:01:00Z', processed_at: null }
}

async function mockReceiptApi(page: Page, role: string) {
  await page.addInitScript(() => { localStorage.setItem('access_token', 'test-token'); localStorage.setItem('selected_tenant_id', 'tenant-alpha') })
  await page.route('http://localhost:8000/api/v1/**', async (route) => {
    const request = route.request(); const pathname = new URL(request.url()).pathname
    const respond = (body: unknown) => route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })
    if (pathname === '/api/v1/auth/me') return respond({ id: 'office-user', email: 'office@example.org', display_name: 'Office User', preferred_language: 'fr', status: 'active', tenant_id: 'tenant-alpha', roles: [role], last_login_at: null, memberships: [{ tenant_id: 'tenant-alpha', slug: 'alpha', name: 'Association Alpha', default_language: 'fr', roles: [role], branding: { primary_color: '#1f4f8f', logo_url: '' }, modules, profile_type: 'member' }] })
    if (pathname === '/api/v1/contributions/receipt-declarations/member-options') return respond([{
      id: 'member-1', display_name: 'Membre Démonstration', member_code: 'MEM-001', first_name: 'Membre', last_name: 'Démonstration',
      email: 'membre@example.org', phone: '+49 123 456789', membership_type: 'individual', status: 'active', joined_at: '2026-01-01T00:00:00Z',
    }])
    if (pathname === '/api/v1/contributions/receipt-declarations/mine') return respond([declaration()])
    if (pathname === '/api/v1/contributions/receipt-declarations') return respond([declaration()])
    if (pathname === '/api/v1/contributions/') return respond([{ id: 'contribution-1', tenant_id: 'tenant-alpha', membership_profile_id: 'member-1', year: 2026, expected_amount: '60.00', paid_amount: '0.00', balance: '60.00', currency: 'EUR', status: 'pending', due_date: null, created_at: '2026-01-01T00:00:00Z', updated_at: '2026-01-01T00:00:00Z' }])
    return route.fulfill({ status: 404, contentType: 'application/json', body: JSON.stringify({ detail: `Unexpected request: ${pathname}` }) })
  })
}

test.describe('Receipt declarations mobile proof', () => {
  test.use({ viewport: { width: 390, height: 844 }, isMobile: true })

  test('shows the bureau declaration screen without horizontal overflow', async ({ page, browserName }) => {
    await mockReceiptApi(page, 'vice_president')
    await page.goto('/receipts')
    await expect(page.getByRole('heading', { name: 'Déclarer un encaissement reçu' })).toBeVisible()
    await expect(page.getByPlaceholder('Montant')).toBeVisible()
    await expect(page.getByRole('option', { name: 'Membre Démonstration · MEM-001' })).toHaveCount(1)
    expect(await page.locator('.receipt-declarations').evaluate((element) => element.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
    await page.screenshot({ path: `${proofDirectory}/${browserName}-bureau-declaration.png`, fullPage: true })
  })

  test('opens a read-only member profile before selecting a receipt recipient', async ({ page, browserName }) => {
    await mockReceiptApi(page, 'vice_president')
    await page.goto('/receipts')
    await page.getByPlaceholder('Rechercher un membre…').fill('Démon')
    await page.getByRole('button', { name: 'Voir les informations du membre' }).click()
    await expect(page.getByRole('heading', { name: 'Informations du membre' })).toBeVisible()
    await expect(page.getByText('membre@example.org')).toBeVisible()
    await expect(page.getByText('Ces informations sont consultables en lecture seule.')).toBeVisible()
    expect(await page.locator('.receipt-member-modal').evaluate((element) => element.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
    await page.screenshot({ path: `${proofDirectory}/${browserName}-member-readonly-profile.png`, fullPage: true })
    await page.getByRole('button', { name: 'Sélectionner ce membre' }).click()
    await expect(page.locator('form .alert-primary')).toContainText('Membre Démonstration (MEM-001)')
  })

  test('selects a member directly from the full list without searching', async ({ page }) => {
    await mockReceiptApi(page, 'vice_president')
    await page.goto('/receipts')
    await page.getByRole('combobox', { name: 'Choisir dans la liste complète' }).selectOption('member-1')
    await expect(page.locator('form .alert-primary')).toContainText('Membre Démonstration (MEM-001)')
  })

  test('highlights an incomplete receipt declaration and displays a validation notification', async ({ page }) => {
    await mockReceiptApi(page, 'vice_president')
    await page.goto('/receipts')
    await page.getByRole('button', { name: 'Soumettre la déclaration' }).click()

    await expect(page.getByText('Corrigez les champs signalés en rouge avant de continuer.')).toBeVisible()
    await expect(page.getByRole('combobox', { name: 'Choisir dans la liste complète' })).toHaveClass(/is-invalid/)
    await expect(page.getByPlaceholder('Montant')).toHaveClass(/is-invalid/)
  })

  test('shows the treasurer validation queue without horizontal overflow', async ({ page, browserName }) => {
    await mockReceiptApi(page, 'treasurer')
    await page.goto('/receipts')
    await expect(page.getByRole('heading', { name: 'Encaissements à valider' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Valider' })).toBeVisible()
    expect(await page.locator('.receipt-declarations').evaluate((element) => element.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
    await page.screenshot({ path: `${proofDirectory}/${browserName}-treasurer-queue.png`, fullPage: true })
  })
})
