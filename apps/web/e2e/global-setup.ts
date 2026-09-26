import { chromium } from '@playwright/test'

const webPort = process.env.PLAYWRIGHT_WEB_PORT || '5273'
const baseURL = process.env.E2E_BASE_URL || `http://localhost:${webPort}`

/**
 * Warm the Vite dev server once before the browser suite runs.
 *
 * On a cold server the first navigation pays the dependency pre-bundling cost,
 * which can consume the assertion timeouts of the first tests and make the pack
 * flaky on a fresh machine or CI runner. A single navigation here makes every
 * test start against an already compiled module graph.
 */
export default async function globalSetup() {
  const browser = await chromium.launch()
  const page = await browser.newPage()
  try {
    await page.goto(baseURL, { waitUntil: 'domcontentloaded', timeout: 120_000 })
    await page.waitForLoadState('networkidle', { timeout: 120_000 }).catch(() => undefined)
  } finally {
    await browser.close()
  }
}
