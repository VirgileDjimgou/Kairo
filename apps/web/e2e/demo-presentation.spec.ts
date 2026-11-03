import { expect, test } from '@playwright/test'

const locales = ['fr', 'en', 'de'] as const
const viewports = [
  { width: 320, height: 568, name: 'mobile' },
  { width: 390, height: 844, name: 'phone' },
  { width: 1280, height: 720, name: 'desktop' },
]

for (const viewport of viewports) {
  for (const locale of locales) {
    test(`demo presentation stays readable in ${locale} on ${viewport.name}`, async ({ page }) => {
      await page.setViewportSize(viewport)
      await page.goto('/demo', { waitUntil: 'networkidle' })
      await page.locator('.demo-header .language-select').selectOption(locale)

      await expect(page.locator('.demo-title')).toBeVisible()
      await expect(page.locator('.demo-actions .btn')).toBeVisible()
      await expect(page.getByTestId('demo-role-picker')).toBeVisible()

      const layout = await page.evaluate(() => {
        const overflow = document.documentElement.scrollWidth - document.documentElement.clientWidth
        const buttons = [...document.querySelectorAll<HTMLButtonElement>('.demo-role-card .btn')]
        const buttonHeights = buttons.map((button) => button.getBoundingClientRect().height)
        const clippedButton = buttons.some((button) => button.scrollWidth > button.clientWidth + 1)
        const clippedCopy = [...document.querySelectorAll<HTMLElement>('.demo-role-card h3, .demo-role-card p')]
          .some((element) => element.scrollWidth > element.clientWidth + 1)

        return { overflow, buttonHeights, clippedButton, clippedCopy }
      })

      expect(layout.overflow).toBeLessThanOrEqual(1)
      expect(layout.clippedButton).toBe(false)
      expect(layout.clippedCopy).toBe(false)
      expect(new Set(layout.buttonHeights.map((height) => Math.round(height))).size).toBe(1)
    })
  }
}
