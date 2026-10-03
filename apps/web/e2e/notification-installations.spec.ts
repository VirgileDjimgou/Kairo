import { expect, test, type Page } from '@playwright/test'

type CapturedRequest = {
  method: string
  pathname: string
  authorization: string | null
  payload: unknown
}

const modules = {
  membership: true,
  contributions: true,
  policies: true,
  disciplinary: true,
  events: true,
  announcements: true,
  chat: true,
  notifications: true,
}

function makeMembership(tenantId: string, slug: string, name: string, role: string) {
  return {
    tenant_id: tenantId,
    slug,
    name,
    roles: [role],
    branding: { primary_color: '#1f4f8f', logo_url: '' },
    modules,
    profile_type: role === 'member' ? 'member' : 'admin',
  }
}

function makeUser(role: string, memberships: ReturnType<typeof makeMembership>[], tenantId: string) {
  return {
    id: `user-${role}-1`,
    email: `${role}@demo.org`,
    display_name: role === 'member' ? 'Awa Ngono' : 'Priya Principal',
    preferred_language: 'fr',
    status: 'active',
    tenant_id: tenantId,
    roles: [role],
    last_login_at: null,
    memberships,
  }
}

async function installBaseRoutes(
  page: Page,
  role: string,
  memberships: ReturnType<typeof makeMembership>[],
  captured: CapturedRequest[],
): Promise<void> {
  await page.route('**/api/v1/**', async (route) => {
    const request = route.request()
    const pathname = new URL(request.url()).pathname
    const method = request.method()
    const authorization = request.headers()['authorization'] ?? null
    let payload: unknown = null
    try {
      payload = request.postDataJSON()
    } catch {
      payload = null
    }
    captured.push({ method, pathname, authorization, payload })

    if (pathname.endsWith('/auth/me') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(makeUser(role, memberships, memberships[0]!.tenant_id)),
      })
      return
    }
    if (pathname.endsWith('/notifications/inbox') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], unread_count: 0 }),
      })
      return
    }
    if (pathname.endsWith('/notifications/preferences') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          push_enabled: true,
          finance_enabled: true,
          discipline_enabled: true,
          announcements_enabled: true,
          events_enabled: true,
        }),
      })
      return
    }
    if (pathname.endsWith('/notifications/push/configuration') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ enabled: false, reason: 'disabled' }),
      })
      return
    }
    if (pathname.endsWith('/notifications/devices') && method === 'POST') {
      await route.fulfill({ status: 204, body: '' })
      return
    }
    if (pathname.includes('/notifications/devices/') && pathname.endsWith('/revoke')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          revoked_profiles: 1,
          disabled_web_subscriptions: 1,
          disabled_fcm_tokens: 0,
        }),
      })
      return
    }
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: `No installation mock for ${method} ${pathname}` }),
    })
  })
}

test('installation registration sends normalized browser metadata and keeps a stable identity', async ({ page }) => {
  const captured: CapturedRequest[] = []
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'installations-member-token')
  })
  await installBaseRoutes(page, 'member', [makeMembership('tenant-demo-1', 'demo', 'Demo', 'member')], captured)

  await page.goto('/more')
  await expect.poll(() => captured.filter((entry) => entry.pathname.endsWith('/notifications/devices')).length).toBeGreaterThan(0)

  const registration = captured.find((entry) => entry.pathname.endsWith('/notifications/devices'))
  const payload = registration?.payload as {
    installation_id: string
    platform: string
    browser: string
    device_metadata: Record<string, string>
  }
  expect(payload.installation_id).toMatch(/^[0-9a-f-]{36}$/)
  expect(payload.platform.length).toBeGreaterThan(0)
  expect(payload.browser.length).toBeGreaterThan(0)
  expect(payload.device_metadata.display_mode).toBe('browser')
  expect(payload.device_metadata.language.length).toBeGreaterThan(0)

  const storedId = await page.evaluate(() => window.localStorage.getItem('kairo_notification_installation_id'))
  expect(storedId).toBe(payload.installation_id)
})

test('notification permission is not requested on first visit', async ({ page }) => {
  const captured: CapturedRequest[] = []
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'installations-permission-token')
    const state = { requests: 0 }
    ;(window as Window & { __kairoPermissionState?: typeof state }).__kairoPermissionState = state
    const original = Notification.requestPermission.bind(Notification)
    Notification.requestPermission = (...args: Parameters<typeof Notification.requestPermission>) => {
      state.requests += 1
      return original(...args)
    }
  })
  await installBaseRoutes(page, 'member', [makeMembership('tenant-demo-1', 'demo', 'Demo', 'member')], captured)

  await page.goto('/more')
  await expect(page).toHaveURL(/\/more$/)

  const requests = await page.evaluate(
    () => (window as Window & { __kairoPermissionState?: { requests: number } }).__kairoPermissionState?.requests ?? -1,
  )
  expect(requests).toBe(0)
  const pushConfigurationCalls = captured.filter((entry) => entry.pathname.endsWith('/notifications/push/configuration'))
  expect(pushConfigurationCalls).toHaveLength(0)
})

test('explicit enablement reports a missing provider without subscribing', async ({ page, context }) => {
  const captured: CapturedRequest[] = []
  await context.grantPermissions(['notifications'])
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'installations-enable-token')
  })
  await installBaseRoutes(page, 'member', [makeMembership('tenant-demo-1', 'demo', 'Demo', 'member')], captured)

  await page.goto('/more')
  await page.getByRole('banner').getByRole('button', { name: 'Notifications' }).click()
  await page.getByRole('button', { name: 'Activer les notifications sur cet appareil' }).click()

  await expect(page.locator('.Vue-Toastification__toast')).toBeVisible()
  const subscriptionCalls = captured.filter(
    (entry) => entry.pathname.endsWith('/notifications/push-subscriptions') || entry.pathname.endsWith('/notifications/mobile-push-tokens'),
  )
  expect(subscriptionCalls).toHaveLength(0)
})

test('tenant switching revokes the previous tenant binding before switching', async ({ page }) => {
  const captured: CapturedRequest[] = []
  const memberships = [
    makeMembership('tenant-demo-1', 'demo', 'Acme Community Organization', 'principal_admin'),
    makeMembership('tenant-riverdale-1', 'riverdale', 'Riverdale Sports Union', 'principal_admin'),
  ]
  let currentTenantId = 'tenant-demo-1'

  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'tenant-switch-old-token')
    window.localStorage.setItem('selected_tenant_id', 'tenant-demo-1')
  })
  page.on('dialog', async (dialog) => {
    await dialog.accept()
  })

  await page.route('**/api/v1/**', async (route) => {
    const request = route.request()
    const pathname = new URL(request.url()).pathname
    const method = request.method()
    let payload: unknown = null
    try {
      payload = request.postDataJSON()
    } catch {
      payload = null
    }
    captured.push({
      method,
      pathname,
      authorization: request.headers()['authorization'] ?? null,
      payload,
    })

    if (pathname.endsWith('/auth/me') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(makeUser('principal_admin', memberships, currentTenantId)),
      })
      return
    }
    if (pathname.endsWith('/auth/switch-tenant') && method === 'POST') {
      currentTenantId = (payload as { tenant_id: string }).tenant_id
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'tenant-switch-new-token',
          token_type: 'bearer',
          expires_in: 3600,
          tenant_id: currentTenantId,
          user_id: 'user-principal_admin-1',
          memberships,
        }),
      })
      return
    }
    if (pathname.endsWith('/notifications/devices') && method === 'POST') {
      await route.fulfill({ status: 204, body: '' })
      return
    }
    if (pathname.includes('/notifications/devices/') && pathname.endsWith('/revoke')) {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          revoked_profiles: 1,
          disabled_web_subscriptions: 1,
          disabled_fcm_tokens: 0,
        }),
      })
      return
    }
    if (pathname.endsWith('/notifications/inbox') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [], unread_count: 0 }),
      })
      return
    }
    if (pathname.endsWith('/notifications/push/configuration') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ enabled: false, reason: 'disabled' }),
      })
      return
    }
    if (pathname.endsWith('/settings') && method === 'GET') {
      const membership = memberships.find((item) => pathname.includes(item.tenant_id)) ?? memberships[0]!
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          tenant_id: membership.tenant_id,
          name: membership.name,
          slug: membership.slug,
          default_language: 'fr',
          branding: { primary_color: '#1f4f8f', logo_url: '' },
          modules,
          operations: {
            last_backup_at: null,
            last_backup_status: 'unknown',
            last_backup_reference: '',
            last_restore_drill_at: null,
            last_restore_drill_status: 'unknown',
            alert_posture: 'unknown',
            alert_contacts_configured: false,
            backup_retention_days: null,
            notes: '',
            backup_is_stale: false,
            restore_drill_is_stale: false,
            alert_is_healthy: false,
            overall_status: 'healthy',
            status_message: 'Healthy',
          },
          updated_at: '2026-01-01T00:00:00Z',
        }),
      })
      return
    }
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: `No installation mock for ${method} ${pathname}` }),
    })
  })

  await page.goto('/admin/tenants')
  await expect(page.getByTestId('tenant-card-demo')).toContainText('Current tenant')
  await page.getByRole('button', { name: 'Switch to riverdale' }).click()
  await expect(page.getByTestId('tenant-card-riverdale')).toContainText('Current tenant', { timeout: 15000 })

  const revokeIndex = captured.findIndex((entry) => entry.pathname.endsWith('/revoke'))
  const switchIndex = captured.findIndex((entry) => entry.pathname.endsWith('/auth/switch-tenant'))
  expect(revokeIndex).toBeGreaterThanOrEqual(0)
  expect(switchIndex).toBeGreaterThan(revokeIndex)
  expect(captured[revokeIndex]?.authorization).toBe('Bearer tenant-switch-old-token')
})
