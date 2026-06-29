import { test, expect } from '@playwright/test'

test.describe('Admin pages (unauthenticated)', () => {
  test('admin route redirects to login when not authenticated', async ({ page }) => {
    await page.goto('/admin')
    await expect(page).toHaveURL(/login/)
  })

  test('admin members route redirects to login', async ({ page }) => {
    await page.goto('/admin/members')
    await expect(page).toHaveURL(/login/)
  })

  test('admin documents route redirects to login', async ({ page }) => {
    await page.goto('/admin/documents')
    await expect(page).toHaveURL(/login/)
  })

  test('admin settings route redirects to login', async ({ page }) => {
    await page.goto('/admin/settings')
    await expect(page).toHaveURL(/login/)
  })
})
