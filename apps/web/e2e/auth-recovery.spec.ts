import { expect, test } from '@playwright/test'

test.describe('Authentication recovery', () => {
  test('accept invitation shows a clear expired-link message', async ({ page }) => {
    await page.route('http://localhost:8000/api/v1/auth/accept-invite', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invitation has expired' }),
      })
    })

    await page.goto('/accept-invite?token=expired-token')
    await page.getByLabel('Display name').fill('Expired Invite User')
    await page.getByLabel('Password').fill('StrongPass123!')
    await page.getByRole('button', { name: 'Accept invitation & sign in' }).click()

    await expect(
      page.getByText('This invitation link has expired. Ask an administrator for a new one.'),
    ).toBeVisible()
  })

  test('reset password shows a clear already-used-link message', async ({ page }) => {
    await page.route('http://localhost:8000/api/v1/auth/reset-password', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Reset token has already been used' }),
      })
    })

    await page.goto('/reset-password?token=used-token')
    await page.getByLabel('New password').fill('StrongPass123!')
    await page.getByLabel('Confirm password').fill('StrongPass123!')
    await page.getByRole('button', { name: 'Reset password' }).click()

    await expect(
      page.getByText('This reset link has already been used. Request a new one to continue.'),
    ).toBeVisible()
  })

  test('forgot password shows a stable fallback error when delivery is unavailable', async ({ page }) => {
    await page.route('http://localhost:8000/api/v1/auth/forgot-password', async (route) => {
      await route.fulfill({
        status: 503,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Password recovery service unavailable' }),
      })
    })

    await page.goto('/forgot-password')
    await page.getByLabel('Email address').fill('member@test.com')
    await page.getByRole('button', { name: 'Send reset link' }).click()

    await expect(page.getByText('Password recovery service unavailable')).toBeVisible()
  })
})
