import { expect, test, type Page } from '@playwright/test'

function makeMeResponse() {
  return {
    id: 'user-member-1',
    email: 'member@demo.org',
    display_name: 'Member User',
    status: 'active',
    tenant_id: 'tenant-demo-1',
    roles: ['member'],
    last_login_at: null,
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
}

async function mockAccountSecurity(page: Page) {
  let mfaStatus = { enabled: false, enrolled: false }
  let sessions = [
    {
      id: 'session-current-1',
      current: true,
      current_tenant_id: 'tenant-demo-1',
      created_at: '2026-06-29T08:00:00Z',
      last_seen_at: '2026-06-29T10:00:00Z',
      created_ip: '127.0.0.1',
      last_seen_ip: '127.0.0.1',
      created_user_agent: 'Chrome current',
      last_seen_user_agent: 'Chrome current',
    },
    {
      id: 'session-other-1',
      current: false,
      current_tenant_id: 'tenant-demo-1',
      created_at: '2026-06-28T07:00:00Z',
      last_seen_at: '2026-06-29T09:00:00Z',
      created_ip: '10.0.0.5',
      last_seen_ip: '10.0.0.5',
      created_user_agent: 'Firefox laptop',
      last_seen_user_agent: 'Firefox laptop',
    },
  ]
  const securityEvents = [
    {
      id: 'event-1',
      action: 'login_succeeded',
      actor_user_id: 'user-member-1',
      entity_type: 'session',
      entity_id: 'session-current-1',
      details: { mfa_completed: false },
      created_at: '2026-06-29T10:00:00Z',
    },
    {
      id: 'event-2',
      action: 'session_revoked',
      actor_user_id: 'user-member-1',
      entity_type: 'session',
      entity_id: 'session-old-1',
      details: { reason: 'manual_revoke_others' },
      created_at: '2026-06-29T09:30:00Z',
    },
  ]

  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-member-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeMeResponse()),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/mfa/status', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mfaStatus),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/mfa/enroll', async (route) => {
    mfaStatus = { enabled: false, enrolled: true }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        secret: 'JBSWY3DPEHPK3PXP',
        uri: 'otpauth://totp/Kairo:member@demo.org?secret=JBSWY3DPEHPK3PXP',
        qr_code_url: '',
      }),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/mfa/verify', async (route) => {
    mfaStatus = { enabled: true, enrolled: true }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        enabled: true,
        message: 'MFA has been enabled',
      }),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/mfa', async (route) => {
    mfaStatus = { enabled: false, enrolled: false }
    await route.fulfill({ status: 204, body: '' })
  })

  await page.route('http://localhost:8000/api/v1/auth/forgot-password', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        message: 'If the email exists, a reset token has been generated',
        reset_token: 'dev-reset-token-12345',
      }),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/sessions', async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(sessions),
      })
      return
    }

    sessions = sessions.filter((session) => session.id !== 'session-other-1')
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        message: 'The selected session has been revoked.',
        revoked_session_count: 1,
      }),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/sessions/revoke-others', async (route) => {
    sessions = sessions.filter((session) => session.current)
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        message: 'Other active sessions have been revoked.',
        revoked_session_count: 1,
      }),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/sessions/revoke-all', async (route) => {
    sessions = []
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        message: 'All active sessions have been revoked.',
        revoked_session_count: 2,
      }),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/security-events', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(securityEvents),
    })
  })
}

test.describe('Account security', () => {
  test('allows a signed-in user to enable MFA and trigger password recovery', async ({ page }) => {
    await mockAccountSecurity(page)
    await page.goto('/account/security')

    await expect(page).toHaveURL(/\/account\/security$/)
    await expect(page.getByRole('heading', { name: 'Account security' })).toBeVisible()
    await expect(page.getByTestId('account-security-summary')).toContainText('Not enabled')

    await page.getByRole('button', { name: 'Set up MFA' }).click()
    await expect(page.getByText('Manual key:')).toBeVisible()
    await page.getByLabel('Verification code').fill('123456')
    await page.getByRole('button', { name: 'Enable MFA' }).click()
    await expect(page.getByTestId('account-security-summary')).toContainText('Enabled')

    await page.getByRole('button', { name: 'Email reset link' }).click()
    await expect(page.getByText('Development reset token')).toBeVisible()
    await expect(page.getByText('dev-reset-token-12345')).toBeVisible()
  })

  test('allows a signed-in user to disable MFA after it is enabled', async ({ page }) => {
    await mockAccountSecurity(page)
    await page.goto('/account/security')

    await page.getByRole('button', { name: 'Set up MFA' }).click()
    await page.getByLabel('Verification code').fill('123456')
    await page.getByRole('button', { name: 'Enable MFA' }).click()
    await page.getByRole('button', { name: 'Disable MFA' }).click()

    await expect(page.getByTestId('account-security-summary')).toContainText('Not enabled')
  })

  test('shows session inventory and allows revoking other sessions', async ({ page }) => {
    await mockAccountSecurity(page)
    await page.goto('/account/security')

    await expect(page.getByTestId('account-security-sessions')).toContainText('Current session')
    await expect(page.getByTestId('account-security-sessions')).toContainText('Firefox laptop')
    await expect(page.getByTestId('account-security-events')).toContainText('Successful sign-in')

    await page.getByRole('button', { name: 'Revoke other sessions' }).click()

    await expect(page.getByTestId('account-security-summary')).toContainText('1')
    await expect(page.getByTestId('account-security-sessions')).not.toContainText('Firefox laptop')
  })
})
