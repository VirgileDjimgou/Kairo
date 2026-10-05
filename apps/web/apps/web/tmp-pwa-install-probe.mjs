import { chromium, devices } from '@playwright/test'
import fs from 'node:fs'

const baseURL = fs.readFileSync(process.env.TEMP + '\\opencode\\kairo-demo-url.txt', 'utf8').trim()
const browser = await chromium.launch()
const context = await browser.newContext({ ...devices['Pixel 7'] })
const page = await context.newPage()

await page.addInitScript(() => {
  window.__installEvent = false
  window.addEventListener('beforeinstallprompt', () => {
    window.__installEvent = true
  })
})

await page.goto(baseURL + '/login')
await page.waitForLoadState('networkidle')
console.log('URL:', page.url())
console.log('secure context:', await page.evaluate(() => window.isSecureContext))

await page.locator('#email:visible').fill('alice@demo.org')
await page.locator('#password:visible').fill('Member123!')
await page.locator('button[type="submit"]:visible').click()
await page.waitForURL(/\/dashboard$/, { timeout: 30000 })

await page.waitForFunction(() => Boolean(navigator.serviceWorker.controller), null, { timeout: 30000 })
const swCount = await page.evaluate(async () => (await navigator.serviceWorker.getRegistrations()).length)
const manifestHref = await page.locator('link[rel="manifest"]').getAttribute('href')
const standalone = await page.evaluate(() => window.matchMedia('(display-mode: standalone)').matches)
const installEvent = await page.evaluate(() => window.__installEvent)
const promptBanner = await page.locator('.install-prompt').count()

console.log('service workers actifs:', swCount)
console.log('manifest après connexion:', manifestHref)
console.log('beforeinstallprompt capturé:', installEvent)
console.log('bandeau install visible:', promptBanner > 0)
console.log('mode standalone (pas encore installé):', standalone)

await browser.close()
