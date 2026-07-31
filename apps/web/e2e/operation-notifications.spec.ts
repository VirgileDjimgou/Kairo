import { expect, test } from '@playwright/test'

test('shows closable operation feedback in the top-right corner', async ({ page, browserName }) => {
  await page.goto('/login')
  await expect(page.getByRole('heading', { name: 'Accéder à votre espace' })).toBeVisible()

  await page.evaluate(() => {
    window.dispatchEvent(new CustomEvent('kairo:operation-notification', {
      detail: { level: 'success', messageKey: 'toast.operationSucceeded' },
    }))
    window.dispatchEvent(new CustomEvent('kairo:operation-notification', {
      detail: { level: 'error', messageKey: 'toast.operationFailed', detail: 'Validation serveur indisponible.' },
    }))
  })

  await expect(page.getByText('Opération effectuée avec succès.')).toBeVisible()
  await expect(page.getByText('L’opération a échoué. Validation serveur indisponible.')).toBeVisible()
  await expect(page.locator('.Vue-Toastification__container.top-right')).toBeVisible()
  await expect(page.locator('.Vue-Toastification__toast')).toHaveCount(2)
  await page.screenshot({ path: `artifacts/role-workflow-proof/2026-07-29/${browserName}-operation-notifications-top-right.png`, fullPage: true })
  await page.locator('.Vue-Toastification__toast').nth(0).screenshot({ path: `artifacts/role-workflow-proof/2026-07-29/${browserName}-operation-notification-success.png` })
  await page.locator('.Vue-Toastification__toast').nth(1).screenshot({ path: `artifacts/role-workflow-proof/2026-07-29/${browserName}-operation-notification-error.png` })
})
