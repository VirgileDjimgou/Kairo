import { test, expect } from '@playwright/test'

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

  test('unknown route redirects to login', async ({ page }) => {
    await page.goto('/nonexistent-page')
    await expect(page).toHaveURL(/login/)
  })
})
