import { expect, test, type Page } from '@playwright/test'

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

async function installRoutes(page: Page): Promise<void> {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'tenant-installation-token')
    window.localStorage.setItem('selected_tenant_id', 'tenant-combis-1')
  })
  await page.route('**/api/v1/**', async (route) => {
    const request = route.request()
    const pathname = new URL(request.url()).pathname
    const method = request.method()

    if (pathname.endsWith('/auth/me') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'user-member-install-1',
          email: 'member@combis.example',
          display_name: 'Awa Ngono',
          preferred_language: 'fr',
          status: 'active',
          tenant_id: 'tenant-combis-1',
          roles: ['member'],
          last_login_at: null,
          memberships: [
            {
              tenant_id: 'tenant-combis-1',
              slug: 'combis',
              name: 'Combis Sport Verein',
              roles: ['member'],
              branding: {
                display_name: 'COMBIS App',
                short_name: 'COMBIS',
                primary_color: '#0a5c2e',
                theme_color: '#0a5c2e',
              },
              modules,
              profile_type: 'member',
            },
          ],
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
    if (pathname.endsWith('/notifications/devices') && method === 'POST') {
      await route.fulfill({ status: 204, body: '' })
      return
    }
    if (pathname.endsWith('/attention') && method === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ items: [] }),
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

async function dispatchInstallPrompt(page: Page): Promise<void> {
  await page.evaluate(() => {
    const event = new Event('beforeinstallprompt')
    const synthetic = event as Event & {
      prompt: () => Promise<void>
      userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
    }
    ;(window as Window & { __kairoInstallPrompted?: boolean }).__kairoInstallPrompted = false
    synthetic.prompt = () => {
      ;(window as Window & { __kairoInstallPrompted?: boolean }).__kairoInstallPrompted = true
      return Promise.resolve()
    }
    synthetic.userChoice = Promise.resolve({ outcome: 'accepted' as const })
    window.dispatchEvent(synthetic)
  })
}

test('the manifest link follows the signed-in tenant', async ({ page }) => {
  await installRoutes(page)
  await page.goto('/more')
  await expect(page).toHaveURL(/\/more$/)

  const href = await page.locator('link[rel="manifest"]').getAttribute('href')
  expect(href).toContain('/api/v1/tenants/public/combis/manifest')
})

test('installation is offered through an explicit prompt and hides after install', async ({ page }) => {
  await installRoutes(page)
  await page.goto('/more')

  await dispatchInstallPrompt(page)
  const installButton = page.getByRole('button', { name: 'Installer' })
  await expect(installButton).toBeVisible()

  await installButton.click()
  expect(await page.evaluate(() => (window as Window & { __kairoInstallPrompted?: boolean }).__kairoInstallPrompted)).toBe(true)

  await page.evaluate(() => window.dispatchEvent(new Event('appinstalled')))
  await expect(installButton).toHaveCount(0)
  await expect(page.locator('.Vue-Toastification__toast')).toBeVisible()
})

test('dismissing the install prompt persists for the installation', async ({ page }) => {
  await installRoutes(page)
  await page.goto('/more')
  await dispatchInstallPrompt(page)

  await page.getByRole('button', { name: 'Plus tard' }).click()
  await expect(page.getByRole('button', { name: 'Installer' })).toHaveCount(0)

  await page.reload()
  await dispatchInstallPrompt(page)
  await expect(page.getByRole('button', { name: 'Installer' })).toHaveCount(0)
})

test('installation never requests notification permission', async ({ page }) => {
  await installRoutes(page)
  await page.addInitScript(() => {
    const state = { requests: 0 }
    ;(window as Window & { __kairoPermissionState?: typeof state }).__kairoPermissionState = state
    const original = Notification.requestPermission.bind(Notification)
    Notification.requestPermission = (...args: Parameters<typeof Notification.requestPermission>) => {
      state.requests += 1
      return original(...args)
    }
  })
  await page.goto('/more')
  await dispatchInstallPrompt(page)
  await page.getByRole('button', { name: 'Installer' }).click()

  const requests = await page.evaluate(
    () => (window as Window & { __kairoPermissionState?: { requests: number } }).__kairoPermissionState?.requests ?? -1,
  )
  expect(requests).toBe(0)
})

test('the install prompt renders safely at phone width', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await installRoutes(page)
  await page.goto('/more')
  await dispatchInstallPrompt(page)

  await expect(page.getByRole('button', { name: 'Installer' })).toBeVisible()
  const hasHorizontalOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth + 1,
  )
  expect(hasHorizontalOverflow).toBe(false)
})
