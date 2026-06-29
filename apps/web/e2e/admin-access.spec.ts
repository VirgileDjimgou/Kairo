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
  let managedUsers = [
    {
      user_id: 'user-member-1',
      email: 'member@example.org',
      display_name: 'Member Example',
      profile_type: 'member',
      membership_status: 'active',
      user_status: 'active',
      roles: ['member'],
      last_login_at: '2026-06-29T08:30:00Z',
      active_session_count: 2,
      last_security_event_action: 'login_succeeded',
      last_security_event_at: '2026-06-29T08:30:00Z',
    },
    {
      user_id: 'user-suspended-1',
      email: 'suspended@example.org',
      display_name: 'Suspended Example',
      profile_type: 'member',
      membership_status: 'suspended',
      user_status: 'active',
      roles: ['member'],
      last_login_at: '2026-06-28T11:00:00Z',
      active_session_count: 0,
      last_security_event_action: 'tenant_user_suspended',
      last_security_event_at: '2026-06-28T11:05:00Z',
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
        delivery_status: 'simulated',
        delivery_message: 'Email provider is running in simulation mode.',
        delivery_simulation_only: true,
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

  await page.route('http://localhost:8000/api/v1/auth/admin/managed-users/tenant-demo-1', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(managedUsers),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/admin/managed-users/user-member-1/suspend', async (route) => {
    managedUsers = managedUsers.map((user) =>
      user.user_id === 'user-member-1'
        ? { ...user, membership_status: 'suspended', active_session_count: 0, last_security_event_action: 'tenant_user_suspended' }
        : user
    )
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ message: 'Suspended', membership_status: 'suspended', revoked_session_count: 2 }),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/admin/managed-users/user-suspended-1/reactivate', async (route) => {
    managedUsers = managedUsers.map((user) =>
      user.user_id === 'user-suspended-1'
        ? { ...user, membership_status: 'active', last_security_event_action: 'tenant_user_reactivated' }
        : user
    )
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ message: 'Reactivated', membership_status: 'active', revoked_session_count: 0 }),
    })
  })

  await page.route('http://localhost:8000/api/v1/auth/admin/managed-users/user-member-1/revoke-sessions', async (route) => {
    managedUsers = managedUsers.map((user) =>
      user.user_id === 'user-member-1'
        ? { ...user, active_session_count: 0, last_security_event_action: 'tenant_user_sessions_revoked' }
        : user
    )
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ message: 'Sessions revoked', membership_status: 'active', revoked_session_count: 2 }),
    })
  })
}

test.describe('Admin access operations', () => {
  test('renders invitation operations and creates a new invite', async ({ page }) => {
    await mockAdminAccess(page)
    await page.goto('/admin/access')

    await expect(page).toHaveURL(/\/admin\/access$/)
    await expect(page.getByText('Access and lifecycle operations')).toBeVisible()
    await expect(page.getByTestId('admin-access-summary')).toContainText('Pending')
    await expect(page.getByRole('cell', { name: 'pending@example.org' })).toBeVisible()
    await expect(page.getByTestId('admin-user-lifecycle')).toContainText('Member Example')

    await page.getByLabel('Email').fill('newuser@example.org')
    await page.getByLabel('Role').selectOption('member')
    await page.getByRole('button', { name: 'Send invitation' }).click()

    await expect(page.getByText('Delivery outcome')).toBeVisible()
    await expect(page.getByText('simulated')).toBeVisible()
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

  test('supports lifecycle actions for managed users', async ({ page }) => {
    await mockAdminAccess(page)
    await page.goto('/admin/access')

    await page.getByRole('button', { name: 'Suspend' }).first().click()
    await expect(page.getByRole('row', { name: /Member Example/i })).toContainText('suspended')

    await page.getByRole('button', { name: 'Reactivate' }).first().click()
    await expect(page.getByRole('row', { name: /Suspended Example/i })).toContainText('active')

    await page.getByRole('button', { name: 'Revoke sessions' }).first().click()
    await expect(page.getByRole('row', { name: /Member Example/i })).toContainText('0')
  })
})
