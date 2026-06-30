import { test, expect } from '@playwright/test'

test.describe('Application health', () => {
  test('application root redirects to login', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveURL(/login/)
  })

  test('404 page redirects gracefully', async ({ page }) => {
    await page.goto('/this-route-does-not-exist')
    await expect(page).toHaveURL(/login/)
  })
})
