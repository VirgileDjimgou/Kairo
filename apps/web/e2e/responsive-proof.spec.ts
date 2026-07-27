import { expect, test, type Page } from '@playwright/test'
import path from 'node:path'

const proofRoot = path.resolve('artifacts/responsive-proof/2026-07-27')

const member = {
  id: 'member-1',
  member_code: 'IMP-0041',
  first_name: 'Mireille',
  last_name: 'Salomon',
  display_name: 'Mireille Salomon',
  email: 'mireille.salomon@example.org',
  phone: '+49 123 456 789',
  status: 'active',
  joined_at: '2025-01-15T10:00:00Z',
}

function profile(role: string) {
  return {
    id: `user-${role}`,
    email: `${role}@demo.org`,
    display_name: role.replaceAll('_', ' '),
    roles: [role],
    locale: 'fr',
    preferred_language: 'fr',
    status: 'active',
    last_login_at: null,
    tenant_id: 'tenant-demo-1',
    memberships: [{
      tenant_id: 'tenant-demo-1',
      slug: 'demo',
      name: 'Combis Sport Verein',
      roles: [role],
      branding: { primary_color: '#1a3f6b', logo_url: '' },
      modules: {
        membership: true, contributions: true, policies: true, disciplinary: true,
        events: true, announcements: true, chat: true, notifications: true,
      },
      profile_type: role === 'member' ? 'member' : 'staff',
    }],
  }
}

async function mockApplication(page: Page, role: string) {
  await page.addInitScript(() => {
    localStorage.setItem('access_token', 'responsive-proof-token')
    localStorage.setItem('tenant_id', 'tenant-demo-1')
  })

  await page.route('**/api/v1/**', async (route) => {
    const url = new URL(route.request().url())
    const endpoint = url.pathname.replace('/api/v1', '')
    let body: unknown = []

    if (endpoint === '/auth/me') body = profile(role)
    else if (endpoint === '/memberships/' || endpoint === '/memberships') body = [member]
    else if (endpoint === '/memberships/me') body = member
    else if (endpoint === '/memberships/me/statement') body = {
      profile: member,
      summary: { profile: member, total_expected: '150.00', total_paid: '20.00', total_balance: '130.00', contribution_count: 1 },
      contributions: [],
    }
    else if (endpoint === '/memberships/me/balance') body = { membership_profile_id: member.id, expected_amount: '150.00', paid_amount: '20.00', balance: '130.00' }
    else if (endpoint === '/memberships/me/contributions') body = []
    else if (endpoint === '/auth/sessions' || endpoint === '/auth/security-events') body = []
    else if (endpoint === '/auth/mfa/status') body = { enabled: false, verified: false }
    else if (endpoint === '/chat/conversations') body = []
    else if (endpoint === '/chat/domain-policy') body = { allowed_domains: ['governance'], denied_domains: [] }
    else if (endpoint === '/admin/audit/events') body = [{
      id: 'audit-1', action: 'login_succeeded', entity_type: 'session',
      entity_id: 'e51bc77b-30f1-4778-9157-d7d832908f9e',
      actor_user_id: '4bb6509b-0000-4000-8000-000000000001',
      module_key: 'identity', created_at: '2026-07-27T21:59:36Z',
      details: { tenant_id: 'e8c4ea64-9c4d-4ef1-ba09-4740cb01d66c', mfa_completed: '[redacted]' },
    }]
    else if (endpoint === '/contributions/summary') body = { total_count: 1, total_expected: '150.00', total_paid: '20.00', total_balance: '130.00' }
    else if (endpoint === '/contributions/payments') body = []
    else if (endpoint === '/contributions/' || endpoint === '/contributions') body = [{
      id: 'contribution-1', tenant_id: 'tenant-demo-1', membership_profile_id: member.id,
      year: 2026, expected_amount: '150.00', paid_amount: '20.00', balance: '130.00',
      status: 'pending', due_date: '2026-12-31', created_at: '2026-01-01T10:00:00Z',
    }]
    else if (endpoint === '/policies/' || endpoint === '/policies') body = []
    else if (endpoint === '/disciplinary/' || endpoint === '/disciplinary') body = [{
      id: 'disciplinary-1', membership_profile_id: member.id,
      membership_display_name: member.display_name, title: 'Cotisation en retard',
      description: 'Suivi administratif du dossier et rappel envoyé au membre.',
      policy_record_id: null, policy_title: 'Règlement financier',
      amount: '20.00', currency: 'EUR', status: 'open',
      recorded_at: '2026-07-26T10:00:00Z',
    }]
    else if (endpoint === '/events/' || endpoint === '/events') body = [{
      id: 'event-1', title: 'Summer BBQ 2026', description: 'Rencontre annuelle du club',
      start_at: '2026-08-28T18:00:00Z', end_at: '2026-08-28T22:00:00Z',
      location: 'Riverside Pavilion', visibility_scope: 'members_only', status: 'published',
    }]
    else if (endpoint === '/announcements/' || endpoint === '/announcements') body = [{
      id: 'announcement-1', title: 'Bienvenue pour la saison 2026',
      body: 'Toutes les informations importantes sont maintenant disponibles dans votre espace.',
      published_at: '2026-07-19T10:00:00Z', expires_at: '2026-08-19T10:00:00Z',
      visibility_scope: 'members_only', status: 'published',
    }]
    else if (endpoint.startsWith('/auth/invitations/')) body = [{
      id: 'invite-1', email: 'nouveau.membre@example.org', role_code: 'member',
      status: 'pending', expires_at: '2026-08-01T10:00:00Z',
    }]
    else if (endpoint.startsWith('/auth/admin/managed-users/')) body = [{
      user_id: 'managed-user-1', display_name: 'Carine Christian',
      email: 'carine.christian@example.org', profile_type: 'member',
      roles: ['member', 'sports_manager'], membership_status: 'active',
      active_session_count: 1, last_security_event_at: '2026-07-27T18:30:00Z',
      last_security_event_action: 'login_succeeded',
    }]

    await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(body) })
  })
}

async function open(page: Page, role: string, route: string) {
  await mockApplication(page, role)
  await page.goto(route, { waitUntil: 'networkidle' })
  await expect(page.locator('.app-shell')).toBeVisible()
  await expect(page.locator('.bottom-nav-item')).toHaveCount(5)
}

async function capture(page: Page, folder: string, file: string) {
  await page.screenshot({ path: path.join(proofRoot, folder, file), fullPage: true })
}

test.describe('responsive visual proof', () => {
  const android = [
    [320, 568], [360, 800], [390, 844], [412, 915], [430, 932],
  ]
  const ios = [
    [375, 812], [390, 844], [393, 852], [430, 932],
  ]

  for (const [width, height] of android) {
    test(`android ${width}x${height} members cards`, async ({ page }, testInfo) => {
      test.skip(testInfo.project.name !== 'chromium')
      await page.setViewportSize({ width, height })
      await open(page, 'principal_admin', '/admin/members')
      await expect(page.locator('.mobile-data-card')).toBeVisible()
      await expect(page.locator('.desktop-data-table')).toBeHidden()
      await capture(page, `01-android/${width}x${height}`, `android__${width}x${height}__principal-admin__members__full__PENDING.png`)
    })
  }

  for (const [width, height] of ios) {
    test(`ios ${width}x${height} finance audit cards`, async ({ page }, testInfo) => {
      test.skip(testInfo.project.name !== 'webkit')
      await page.setViewportSize({ width, height })
      await open(page, 'auditor', '/finance-audit')
      await expect(page.locator('.mobile-data-card')).toBeVisible()
      await expect(page.locator('.desktop-data-table')).toBeHidden()
      await capture(page, `02-ios/${width}x${height}`, `ios__${width}x${height}__auditor__finance-audit__full__PENDING.png`)
    })
  }

  const representative = [
    ['principal_admin', '/admin/members', 'members'],
    ['principal_admin', '/admin/access', 'access'],
    ['principal_admin', '/admin/events', 'events'],
    ['principal_admin', '/admin/announcements', 'announcements'],
    ['principal_admin', '/admin/disciplinary', 'discipline'],
    ['principal_admin', '/admin/contributions', 'contributions'],
    ['principal_admin', '/admin/audit', 'audit'],
    ['principal_admin', '/admin', 'admin-overview'],
    ['auditor', '/finance-audit', 'finance-audit'],
    ['censor', '/censor', 'censor'],
    ['member', '/members/profile', 'profile'],
    ['member', '/account/security', 'security'],
    ['member', '/chat', 'chat'],
  ] as const

  const desktop = [
    [1280, 720], [1440, 900], [1920, 1080],
  ]

  for (const [width, height] of desktop) {
    test(`desktop ${width}x${height} members table`, async ({ page }, testInfo) => {
      test.skip(testInfo.project.name !== 'chromium')
      await page.setViewportSize({ width, height })
      await open(page, 'principal_admin', '/admin/members')
      await expect(page.locator('.desktop-data-table')).toBeVisible()
      await expect(page.locator('.mobile-data-list')).toBeHidden()
      await capture(page, `03-desktop-regression/${width}x${height}`, `desktop__${width}x${height}__principal-admin__members__full__PENDING.png`)
    })
  }

  for (const [role, route, slug] of representative) {
    test(`android representative ${slug}`, async ({ page }, testInfo) => {
      test.skip(testInfo.project.name !== 'chromium')
      await page.setViewportSize({ width: 390, height: 844 })
      await open(page, role, route)
      await capture(page, '01-android/390x844', `android__390x844__${role.replaceAll('_', '-')}__${slug}__full__PENDING.png`)
    })
  }
})
