import { expect, test, type Page } from '@playwright/test'

function makeMeResponse() {
  return {
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
}

async function mockAdminAccess(page: Page) {
  let invitations = [
    {
      id: 'invite-pending-1',
      email: 'pending@example.org',
      role_code: 'member',
      status: 'pending',
      expires_at: '2026-07-10T10:00:00Z',
      created_at: '2026-06-29T10:00:00Z',
    },
    {
      id: 'invite-accepted-1',
      email: 'accepted@example.org',
      role_code: 'admin',
      status: 'accepted',
      expires_at: '2026-07-02T10:00:00Z',
      created_at: '2026-06-28T08:00:00Z',
    },
  ]

  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-admin-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeMeResponse()),
    })
  })

  await page.route('http://localhost:8000/api/v1/tenants/tenant-demo-1/roles', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'role-admin',
          tenant_id: 'tenant-demo-1',
          code: 'admin',
          name: 'Administrator',
          description: 'Full access',
          is_system_role: true,
        },
        {
          id: 'role-member',
          tenant_id: 'tenant-demo-1',
          code: 'member',
          name: 'Member',
          description: 'Standard member',
          is_system_role: false,
        },
      ]),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/invitations/tenant-demo-1', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(invitations),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/invite', async (route) => {
    const payload = route.request().postDataJSON() as { email: string; role_code: string; tenant_id: string }
    await route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({
        invitation_id: 'invite-new-1',
        email: payload.email,
        role_code: payload.role_code,
        status: 'pending',
        expires_at: '2026-07-12T09:00:00Z',
        invite_token: 'raw-invite-token-12345',
      }),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/invitations/invite-pending-1', async (route) => {
    invitations = invitations.map((invitation) =>
      invitation.id === 'invite-pending-1'
        ? { ...invitation, status: 'cancelled' }
        : invitation
    )
    await route.fulfill({ status: 204, body: '' })
  })
}

test.describe('Admin access operations', () => {
  test('renders invitation operations and creates a new invite', async ({ page }) => {
    await mockAdminAccess(page)
    await page.goto('/admin/access')

    await expect(page).toHaveURL(/\/admin\/access$/)
    await expect(page.getByText('Access operations')).toBeVisible()
    await expect(page.getByTestId('admin-access-summary')).toContainText('Pending')
    await expect(page.getByRole('cell', { name: 'pending@example.org' })).toBeVisible()

    await page.getByLabel('Email').fill('newuser@example.org')
    await page.getByLabel('Role').selectOption('member')
    await page.getByRole('button', { name: 'Send invitation' }).click()

    await expect(page.getByText('Share the acceptance link securely')).toBeVisible()
    await expect(page.getByText('/accept-invite?token=raw-invite-token-12345')).toBeVisible()
    await expect(page.getByTestId('admin-access-guidance')).toContainText('Password reset and MFA already exist')
  })

  test('allows cancelling a pending invitation', async ({ page }) => {
    await mockAdminAccess(page)
    await page.goto('/admin/access')

    await page.getByRole('button', { name: 'Cancel' }).click()
    await expect(page.getByRole('row', { name: /pending@example\.org/i })).toContainText('cancelled')
    await expect(page.getByRole('cell', { name: 'accepted@example.org' })).toBeVisible()
  })
})
