import { expect, test } from '@playwright/test'

/**
 * Roadmap V2 Sprint 129: the public demo page must expose the white-label
 * studio without any password so a visitor can test the tenant identity
 * (name, colors, logo, launcher icons) and read the generated manifest.
 */
test('the public demo exposes a password-free white-label studio', async ({ page }) => {
  await page.goto('/demo')

  const studio = page.getByTestId('white-label-studio')
  await studio.scrollIntoViewIfNeeded()
  await expect(studio).toBeVisible()

  // Identity is applied live to the page title and preview.
  await page.locator('#studio-display-name').fill('Association Demo')
  await expect(page).toHaveTitle('Association Demo')
  await page.locator('#studio-short-name').fill('AD')
  await expect(studio.getByText('AD', { exact: true })).toBeVisible()

  // The optional tagline/slogan is part of the identity and the manifest.
  await page.locator('#studio-tagline').fill('Le club qui avance ensemble')
  await expect(studio.locator('.studio-preview').getByText('Le club qui avance ensemble')).toBeVisible()

  // Colors are applied live to the semantic CSS variables.
  await page.locator('#studio-primary_color').fill('#7a3ea1')
  await expect
    .poll(async () => page.evaluate(() => document.documentElement.style.getPropertyValue('--om-primary')))
    .toBe('#7a3ea1')

  // The generated manifest follows the studio values.
  const manifest = page.getByTestId('studio-manifest')
  await expect(manifest).toContainText('"name": "Association Demo"')
  await expect(manifest).toContainText('"short_name": "AD"')
  await expect(manifest).toContainText('"description": "Le club qui avance ensemble"')

  // The install icon preview and the Apple touch icon follow the configured asset.
  await page.locator('#studio-icon-192').fill('/favicon.svg')
  await expect(studio.locator('.studio-icon img').first()).toHaveAttribute('src', '/favicon.svg')
  await expect(page.locator('link[rel="apple-touch-icon"]')).toHaveAttribute('href', '/favicon.svg')

  // A preset applies a complete identity in one click.
  await page.getByTestId('studio-preset').nth(1).click()
  await expect(page).toHaveTitle('Club Sportif Horizon')

  // Reset restores the platform defaults.
  await page.getByTestId('studio-reset').click()
  await expect(page).toHaveTitle('Kairo')
})
