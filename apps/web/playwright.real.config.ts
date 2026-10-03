import { defineConfig, devices } from '@playwright/test'

// Real-stack browser gate (Roadmap V2 Sprint 128). The production-like stack
// must already be running; no web server is started and no API is mocked.
const baseURL = process.env.KAIRO_GATE_BASE_URL || 'http://localhost:8080'

export default defineConfig({
  testDir: './e2e-real',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: 'html',
  timeout: 60_000,
  use: {
    baseURL,
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
