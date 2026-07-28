import { expect, test } from '@playwright/test'

test('shows the application update notice', async ({ page, browserName }) => {
  await page.goto('/login')
  await expect(page.getByRole('heading', { name: 'Accéder à votre espace' })).toBeVisible()

  await page.evaluate(() => window.dispatchEvent(new Event('kairo:pwa-update-available')))

  await expect(page.getByText('Une nouvelle version de l’application est disponible.')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Mettre à jour' })).toBeVisible()
  await page.screenshot({ path: `artifacts/role-workflow-proof/2026-07-28/${browserName}-pwa-update-notice.png`, fullPage: true })
})
