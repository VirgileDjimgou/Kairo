import { test, expect } from '@playwright/test'

test.describe('Application health', () => {
  test('application root redirects to login', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveURL(/login/)
  })

  test('404 page redirects gracefully', async ({ page }) => {
    const response = await page.goto('/api/nonexistent')
    expect(response?.status?.()).toBeLessThan(500)
  })
})
