import { test, expect } from '@playwright/test'

function makeMemberships() {
  return [
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
    {
      tenant_id: 'tenant-ops-2',
      slug: 'ops',
      name: 'Ops Organization',
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
  ]
}

test.describe('Login flow', () => {
  test('login page renders correctly', async ({ page }) => {
    await page.goto('/login')
    await expect(page.getByTestId('commercial-hero-title')).toBeVisible()
    await expect(page.getByTestId('commercial-hero')).toContainText('Private AI for organizations')
    await expect(page.locator('input[type="email"]')).toBeVisible()
    await expect(page.locator('input[type="password"]')).toBeVisible()
    await expect(page.locator('button[type="submit"]')).toBeVisible()
    await expect(page.locator('#signin-card')).toBeVisible()
    await expect(page.locator('#highlights .highlight-card')).toHaveCount(3)
  })

  test('login form shows validation on empty submit', async ({ page }) => {
    await page.goto('/login')
    await page.locator('button[type="submit"]').click()
    await expect(page.getByText('Email is required')).toBeVisible()
    await expect(page.locator('#email')).toHaveClass(/is-invalid/)
  })

  test('login with invalid credentials shows error', async ({ page }) => {
    await page.route('http://localhost:8000/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid email or password' }),
      })
    })

    await page.goto('/login')
    await page.locator('input[type="email"]').fill('nonexistent@test.com')
    await page.locator('input[type="password"]').fill('wrongpassword')
    await page.locator('button[type="submit"]').click()
    await expect(page.locator('.alert-danger')).toBeVisible({ timeout: 10000 })
  })

  test('login shows a clear suspended-access message', async ({ page }) => {
    await page.route('http://localhost:8000/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 403,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'You are not an active member of this organization' }),
      })
    })

    await page.goto('/login')
    await page.locator('input[type="email"]').fill('member@test.com')
    await page.locator('input[type="password"]').fill('StrongPass123!')
    await page.locator('button[type="submit"]').click()
    await expect(page.getByText('You do not currently have active access to an organization.')).toBeVisible()
  })

  test('mfa flow keeps multi-tenant users on the organization picker', async ({ page }) => {
    await page.route('http://localhost:8000/api/v1/auth/login', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          mfa_required: true,
          mfa_token: 'mfa-token-123',
          expires_in: 300,
        }),
      })
    })

    await page.route('http://localhost:8000/api/v1/auth/mfa/complete', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'access-token-123',
          token_type: 'bearer',
          expires_in: 1800,
          tenant_id: 'tenant-demo-1',
          user_id: 'user-1',
        }),
      })
    })

    await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'user-1',
          email: 'member@test.com',
          display_name: 'Member User',
          status: 'active',
          tenant_id: 'tenant-demo-1',
          roles: ['member'],
          last_login_at: null,
          memberships: makeMemberships(),
        }),
      })
    })

    await page.goto('/login')
    await page.locator('input[type="email"]').fill('member@test.com')
    await page.locator('input[type="password"]').fill('StrongPass123!')
    await page.locator('button[type="submit"]').click()
    await expect(page.getByRole('heading', { name: 'Two-factor authentication' })).toBeVisible()

    await page.locator('#mfa-code').fill('123456')
    await page.getByRole('button', { name: 'Verify' }).click()

    await expect(page.getByRole('heading', { name: 'Choose organization' })).toBeVisible()
    await expect(page.getByRole('button', { name: /Demo Organization/ })).toBeVisible()
    await expect(page.getByRole('button', { name: /Ops Organization/ })).toBeVisible()
  })

  test('forgot password link is accessible', async ({ page }) => {
    await page.goto('/login')
    const forgotLink = page.locator('a[href*="forgot"], a:has-text("Forgot")')
    if (await forgotLink.isVisible()) {
      await forgotLink.click()
      await expect(page).toHaveURL(/forgot-password/)
    }
  })
})

test.describe('Unauthenticated access', () => {
  test('protected route redirects to login', async ({ page }) => {
    await page.goto('/dashboard')
    await expect(page).toHaveURL(/login/)
  })

  test('protected route preserves the requested redirect target', async ({ page }) => {
    await page.goto('/account/security')
    await expect(page).toHaveURL(/login\?redirect=\/account\/security/)
  })

  test('unknown route redirects to login', async ({ page }) => {
    await page.goto('/nonexistent-page')
    await expect(page).toHaveURL(/login/)
  })
})
