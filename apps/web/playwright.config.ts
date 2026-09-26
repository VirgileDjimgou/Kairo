import { defineConfig, devices } from '@playwright/test'

// The application stack in docker-compose.yml publishes 5173 (web) and 8000
// (api). Reusing those ports made Playwright silently run against the
// containerised build instead of the working tree. The E2E suite therefore
// defaults to a dedicated port; override with PLAYWRIGHT_WEB_PORT if needed.
const webPort = process.env.PLAYWRIGHT_WEB_PORT || '5273'
const webUrl = process.env.PLAYWRIGHT_WEB_URL || `http://localhost:${webPort}`
const npmCommand = process.platform === 'win32' ? 'npm.cmd' : 'npm'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: 'html',
  globalSetup: './e2e/global-setup.ts',
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
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
})
