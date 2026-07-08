import { expect, test, type Page } from '@playwright/test'

type Locale = 'fr' | 'en' | 'de'

function makeMembership(locale: Locale, role: string) {
  return {
    tenant_id: 'tenant-demo-1',
    slug: 'demo',
    name: 'Combis Sport Verein',
    default_language: locale,
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
    profile_type: role === 'member' ? 'member' : 'staff',
  }
}

function makeMe(locale: Locale, role: string) {
  return {
    id: `user-${role}-1`,
    email: `${role}@demo.org`,
    display_name: role === 'member' ? 'Aude Ndam' : role === 'secretary_general' ? 'Sophie Mvondo' : 'Lukas Fischer',
    preferred_language: locale,
    status: 'active',
    tenant_id: 'tenant-demo-1',
    roles: [role],
    last_login_at: null,
    memberships: [makeMembership(locale, role)],
  }
}

function statementResponse(locale: Locale) {
  return {
    profile: {
      id: 'profile-1',
      tenant_id: 'tenant-demo-1',
      user_id: 'user-member-1',
      member_code: 'MEM-1001',
      first_name: locale === 'de' ? 'Anna' : locale === 'en' ? 'Ava' : 'Awa',
      last_name: locale === 'de' ? 'Meyer' : locale === 'en' ? 'Brown' : 'Ngono',
      display_name: locale === 'de' ? 'Anna Meyer' : locale === 'en' ? 'Ava Brown' : 'Awa Ngono',
      email: 'member@demo.org',
      phone: '+49 000 000',
      status: 'active',
      joined_at: '2025-01-10T10:00:00Z',
      created_at: '2025-01-10T10:00:00Z',
      updated_at: '2025-06-01T10:00:00Z',
    },
    summary: {
      profile: {
        id: 'profile-1',
        tenant_id: 'tenant-demo-1',
        user_id: 'user-member-1',
        member_code: 'MEM-1001',
        first_name: locale === 'de' ? 'Anna' : locale === 'en' ? 'Ava' : 'Awa',
        last_name: locale === 'de' ? 'Meyer' : locale === 'en' ? 'Brown' : 'Ngono',
        display_name: locale === 'de' ? 'Anna Meyer' : locale === 'en' ? 'Ava Brown' : 'Awa Ngono',
        email: 'member@demo.org',
        phone: '+49 000 000',
        status: 'active',
        joined_at: '2025-01-10T10:00:00Z',
        created_at: '2025-01-10T10:00:00Z',
        updated_at: '2025-06-01T10:00:00Z',
      },
      total_expected: '120.00',
      total_paid: '90.00',
      total_balance: '30.00',
      contribution_count: 2,
    },
    contributions: [
      {
        id: 'contrib-1',
        tenant_id: 'tenant-demo-1',
        membership_profile_id: 'profile-1',
        year: 2025,
        expected_amount: '60.00',
        paid_amount: '30.00',
        balance: '30.00',
        currency: 'EUR',
        status: 'partial',
        due_date: '2025-12-31T00:00:00Z',
      },
    ],
  }
}

async function seedLocale(page: Page, locale: Locale, role: string) {
  await page.addInitScript(({ nextLocale }) => {
    window.localStorage.setItem('preferred_locale', nextLocale)
    window.localStorage.setItem('access_token', 'playwright-access-token')
  }, { nextLocale: locale })

  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeMe(locale, role)),
    })
  })
}

test.describe('locale coverage', () => {
  test('member profile renders in the selected language', async ({ page }) => {
    await seedLocale(page, 'fr', 'member')
    await page.route('**/api/v1/memberships/me/statement', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(statementResponse('fr')),
      })
    })

    await page.goto('/members/profile')
    await expect(page.getByRole('heading', { name: 'Mon profil et mon relevé de cotisations' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Télécharger mon relevé' })).toBeVisible()
    await expect(page.getByText("Cet espace n'expose jamais les données financières d'un autre membre.")).toBeVisible()
  })

  test('secretary workspace renders in English when requested', async ({ page }) => {
    await seedLocale(page, 'en', 'secretary_general')

    await page.goto('/secretary')
    await expect(page.getByRole('heading', { name: 'Official records and communication workspace' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Open documents' })).toBeVisible()
    await expect(page.getByText('Manage the documents, policies, and announcements that shape the formal life of the organization without entering finance or disciplinary operations.')).toBeVisible()
  })

  test('sports workspace renders in German when requested', async ({ page }) => {
    await seedLocale(page, 'de', 'sports_manager')
    await page.route('**/api/v1/sports/events', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      })
    })

    await page.goto('/sports')
    await expect(page.getByRole('heading', { name: 'Sportbereich' })).toBeVisible()
    await expect(page.getByRole('button', { name: 'Aktualisieren' })).toBeVisible()
    await expect(page.getByText('Noch keine Sportereignisse')).toBeVisible()
  })
})
