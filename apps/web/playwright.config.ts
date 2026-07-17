import { defineConfig, devices } from '@playwright/test'

const webPort = process.env.PLAYWRIGHT_WEB_PORT || '5173'
const webUrl = process.env.PLAYWRIGHT_WEB_URL || `http://localhost:${webPort}`
const npmCommand = process.platform === 'win32' ? 'npm.cmd' : 'npm'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: 'html',
  webServer: {
    command: `${npmCommand} run dev -- --host 0.0.0.0 --port ${webPort}`,
    url: webUrl,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
  use: {
    baseURL: process.env.E2E_BASE_URL || webUrl,
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
