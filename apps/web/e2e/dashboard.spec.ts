import { test, expect } from '@playwright/test'

const onboardingChecklistPattern = /First-run checklist|Checklist de premier démarrage|Erststart-Checkliste/
const setupModePattern = /This tenant is still in setup mode|Ce tenant est encore en mode initialisation|Dieser Tenant ist noch im Einrichtungsmodus/
const quickActionsPattern = /Quick actions|Actions rapides|Schnellaktionen/

function welcomeBackPattern(name: string) {
  return new RegExp(`^(Welcome back|Bon retour|Willkommen zurück), ${name}$`)
}

const meResponse = {
  id: 'user-admin-1',
  email: 'admin@demo.org',
  display_name: 'Admin User',
  status: 'active',
  tenant_id: 'tenant-demo-1',
  roles: ['admin'],
  last_login_at: null,
  memberships: [
    {
      tenant_id: 'tenant-demo-1',
      slug: 'demo',
      name: 'Demo Organization',
      roles: ['admin'],
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
      profile_type: 'admin',
    },
  ],
}

const memberMeResponse = {
  ...meResponse,
  id: 'user-member-1',
  email: 'member@demo.org',
  display_name: 'Member User',
  roles: ['member'],
  memberships: [
    {
      tenant_id: 'tenant-demo-1',
      slug: 'demo',
      name: 'Demo Organization',
      roles: ['member'],
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
      profile_type: 'member',
    },
  ],
}

const treasurerMeResponse = {
  ...meResponse,
  id: 'user-treasurer-1',
  email: 'treasurer@demo.org',
  display_name: 'Treasurer User',
  roles: ['treasurer'],
  memberships: [
    {
      tenant_id: 'tenant-demo-1',
      slug: 'demo',
      name: 'Demo Organization',
      roles: ['treasurer'],
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
      profile_type: 'treasurer',
    },
  ],
}

const auditorMeResponse = {
  ...meResponse,
  id: 'user-auditor-1',
  email: 'auditor@demo.org',
  display_name: 'Auditor User',
  roles: ['auditor'],
  memberships: [
    {
      tenant_id: 'tenant-demo-1',
      slug: 'demo',
      name: 'Demo Organization',
      roles: ['auditor'],
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

const censorMeResponse = {
  ...meResponse,
  id: 'user-censor-1',
  email: 'censor@demo.org',
  display_name: 'Censor User',
  roles: ['censor'],
  memberships: [
    {
      tenant_id: 'tenant-demo-1',
      slug: 'demo',
      name: 'Demo Organization',
      roles: ['censor'],
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

const sportsManagerMeResponse = {
  ...meResponse,
  id: 'user-sports-1',
  email: 'sports@demo.org',
  display_name: 'Sports Manager',
  roles: ['sports_manager'],
  memberships: [
    {
      tenant_id: 'tenant-demo-1',
      slug: 'demo',
      name: 'Demo Organization',
      roles: ['sports_manager'],
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

const presidentMeResponse = {
  ...meResponse,
  id: 'user-president-1',
  email: 'president@demo.org',
  display_name: 'President User',
  roles: ['president'],
  memberships: [
    {
      tenant_id: 'tenant-demo-1',
      slug: 'demo',
      name: 'Demo Organization',
      roles: ['president'],
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

const principalAdminMeResponse = {
  ...meResponse,
  id: 'user-principal-1',
  email: 'principal@demo.org',
  display_name: 'Principal Admin User',
  roles: ['principal_admin'],
  memberships: [
    {
      tenant_id: 'tenant-demo-1',
      slug: 'demo',
      name: 'Demo Organization',
      roles: ['principal_admin'],
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
      profile_type: 'admin',
    },
  ],
}

async function mockAuthenticatedDashboard(page: import('@playwright/test').Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-demo-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(meResponse),
    })
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/memberships/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })
}

async function mockMemberDashboard(page: import('@playwright/test').Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-member-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(memberMeResponse),
    })
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/memberships/me/statement', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        profile: {
          id: 'profile-member-1',
          tenant_id: 'tenant-demo-1',
          user_id: 'user-member-1',
          member_code: 'M-100',
          first_name: 'Member',
          last_name: 'User',
          display_name: 'Member User',
          email: 'member@demo.org',
          phone: null,
          status: 'active',
          joined_at: '2026-01-01T00:00:00Z',
          created_at: '2026-01-01T00:00:00Z',
          updated_at: '2026-01-01T00:00:00Z',
        },
        summary: {
          profile: {
            id: 'profile-member-1',
            tenant_id: 'tenant-demo-1',
            user_id: 'user-member-1',
            member_code: 'M-100',
            first_name: 'Member',
            last_name: 'User',
            display_name: 'Member User',
            email: 'member@demo.org',
            phone: null,
            status: 'active',
            joined_at: '2026-01-01T00:00:00Z',
            created_at: '2026-01-01T00:00:00Z',
            updated_at: '2026-01-01T00:00:00Z',
          },
          total_expected: '120.00',
          total_paid: '45.00',
          total_balance: '75.00',
          contribution_count: 1,
        },
        contributions: [],
      }),
    })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })
}

async function mockTreasurerDashboard(page: import('@playwright/test').Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-treasurer-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(treasurerMeResponse),
    })
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })
}

async function mockCensorDashboard(page: import('@playwright/test').Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-censor-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(censorMeResponse),
    })
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })
}

async function mockAuditorDashboard(page: import('@playwright/test').Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-auditor-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(auditorMeResponse),
    })
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })
}

async function mockSportsDashboard(page: import('@playwright/test').Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-sports-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(sportsManagerMeResponse),
    })
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })
}

async function mockPresidentDashboard(page: import('@playwright/test').Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-president-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(presidentMeResponse),
    })
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/memberships/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })
}

async function mockPrincipalAdminDashboard(page: import('@playwright/test').Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-principal-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(principalAdminMeResponse),
    })
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/memberships/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })
}

test.describe('Dashboard onboarding', () => {
  test('shows the first-run checklist for a tenant still in setup mode', async ({ page }) => {
    await mockAuthenticatedDashboard(page)
    await page.goto('/dashboard')

    await expect(page).toHaveURL(/dashboard/)
    await expect(page.getByTestId('tenant-onboarding')).toBeVisible()
    await expect(page.getByText(onboardingChecklistPattern)).toBeVisible()
    await expect(page.getByText(setupModePattern)).toBeVisible()
    await expect(page.locator('a[href="/admin/documents"]').first()).toBeVisible()
    await expect(page.locator('a[href="/admin/members"]').first()).toBeVisible()
    await expect(page.getByText(quickActionsPattern)).toBeVisible()
    await expect(page.getByTestId('tenant-onboarding-progress')).toContainText('0%')
  })

  test('shows role-aware quick actions for a treasurer session', async ({ page }) => {
    await mockTreasurerDashboard(page)
    await page.goto('/dashboard')

    await expect(page.getByRole('heading', { name: welcomeBackPattern('Treasurer User') })).toBeVisible()
    await expect(page.getByTestId('dashboard-workspace-focus')).toBeVisible()
    await expect(page.getByRole('heading', { name: /Balances, contribution records, and payments|Soldes, cotisations et paiements|Salden, Beitragsakten und Zahlungen/ })).toBeVisible()
    await expect(page.getByTestId('dashboard-workspace-focus').locator('a[href="/finance"]').first()).toBeVisible()
    await expect(page.getByText(quickActionsPattern)).toBeVisible()
    await expect(page.locator('a[href="/finance"]').first()).toBeVisible()
    await expect(page.getByRole('link', { name: /Open finance audit|Ouvrir l'audit financier|Finanzaudit öffnen/ })).toHaveCount(0)
    await expect(page.locator('a[href="/admin/settings"]')).toHaveCount(0)
    await expect(page.locator('a[href="/admin/documents"]')).toHaveCount(0)
    await expect(page.locator('a[href="/admin/members"]')).toHaveCount(0)
    await expect(page.getByText(/Use the finance workspace to review balances, payment activity, and the member records needed for treasury follow-up.|Utilisez l'espace finances pour suivre les soldes, les paiements et les dossiers membres utiles au trésorier.|Nutzen Sie den Finanzbereich, um Salden, Zahlungen und die fuer die Nachverfolgung noetigen Mitgliederdaten zu pruefen./)).toBeVisible()
  })

  test('keeps the auditor dashboard aligned with read-only routes', async ({ page }) => {
    await mockAuditorDashboard(page)
    await page.goto('/dashboard')

    await expect(page.getByRole('heading', { name: welcomeBackPattern('Auditor User') })).toBeVisible()
    await expect(page.getByTestId('dashboard-workspace-focus').locator('a[href="/finance-audit"]').first()).toBeVisible()
    await expect(page.getByRole('link', { name: /Review finance workspace|Revoir l'espace finances|Finanzbereich prüfen/ })).toHaveCount(0)
    await expect(page.getByRole('link', { name: /Review member directory|Consulter l'annuaire membre|Mitgliederverzeichnis prüfen/ })).toHaveCount(0)
    await expect(page.locator('a[href="/policies"]').first()).toBeVisible()
    await expect(page.locator('a[href="/admin/health"]').first()).toBeVisible()
    await expect(page.locator('a[href="/finance"]')).toHaveCount(0)
  })

  test('shows the disciplinary workspace quick action for censor sessions', async ({ page }) => {
    await mockCensorDashboard(page)
    await page.goto('/dashboard')

    await expect(page.getByRole('heading', { name: welcomeBackPattern('Censor User') })).toBeVisible()
    await expect(page.getByText(quickActionsPattern)).toBeVisible()
    await expect(page.getByTestId('dashboard-workspace-focus').locator('a[href="/censor"]').first()).toBeVisible()
    await expect(page.locator('a[href="/censor"]').first()).toBeVisible()
  })

  test('shows the sports workspace quick action for sports managers', async ({ page }) => {
    await mockSportsDashboard(page)
    await page.goto('/dashboard')

    await expect(page.getByRole('heading', { name: welcomeBackPattern('Sports Manager') })).toBeVisible()
    await expect(page.getByTestId('dashboard-workspace-focus').locator('a[href="/sports"]').first()).toBeVisible()
    await expect(page.locator('a[href="/sports"]').first()).toBeVisible()
  })

  test('shows the governance cockpit quick action for president sessions', async ({ page }) => {
    await mockPresidentDashboard(page)
    await page.goto('/dashboard')

    await expect(page.getByRole('heading', { name: welcomeBackPattern('President User') })).toBeVisible()
    await expect(page.getByTestId('dashboard-workspace-focus').locator('a[href="/governance"]').first()).toBeVisible()
    await expect(page.locator('a[href="/governance"]').first()).toBeVisible()
  })

  test('shows the principal admin control plane quick action for principal admins', async ({ page }) => {
    await mockPrincipalAdminDashboard(page)
    await page.goto('/dashboard')

    await expect(page.getByRole('heading', { name: welcomeBackPattern('Principal Admin User') })).toBeVisible()
    await expect(page.getByTestId('dashboard-workspace-focus')).toBeVisible()
    await expect(page.getByRole('heading', { name: /Tenant operations, settings, and sensitive review|Opérations du tenant, réglages et supervision sensible|Tenant-Betrieb, Einstellungen und sensible Kontrolle/ })).toBeVisible()
    await expect(page.getByTestId('dashboard-workspace-focus').locator('a[href="/admin/settings"]').first()).toBeVisible()
    await expect(page.locator('a[href="/admin/settings"]').first()).toBeVisible()
    await expect(page.locator('a[href="/admin/onboarding"]').first()).toBeVisible()
    await expect(page.locator('a[href="/admin/tenants"]').first()).toBeVisible()
  })

  test('keeps the member sidebar compact and personal', async ({ page }) => {
    await mockMemberDashboard(page)
    await page.goto('/dashboard')

    const sidebar = page.locator('aside.sidebar')
    await expect(page.getByRole('heading', { name: welcomeBackPattern('Member User') })).toBeVisible()
    await expect(sidebar.locator('a[href="/members/profile"]')).toBeVisible()
    await expect(sidebar.locator('a[href="/account/security"]')).toBeVisible()
    await expect(sidebar.locator('a[href="/chat"]')).toBeVisible()
    await expect(sidebar.locator('a[href="/events"]')).toBeVisible()
    await expect(sidebar.locator('a[href="/announcements"]')).toBeVisible()
    await expect(sidebar.locator('a[href="/finance"]')).toHaveCount(0)
    await expect(sidebar.locator('a[href="/admin/settings"]')).toHaveCount(0)
    await expect(sidebar.locator('a[href="/governance"]')).toHaveCount(0)
  })
})
