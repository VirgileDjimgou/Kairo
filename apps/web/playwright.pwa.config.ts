import { defineConfig, devices } from '@playwright/test'

// Built-PWA verification. Runs against `vite preview` so the generated
// Service Worker is active; the dev-server config cannot exercise it.
const previewPort = process.env.PWA_PREVIEW_PORT || '5274'
const previewUrl = process.env.PWA_PREVIEW_URL || `http://localhost:${previewPort}`
const npmCommand = process.platform === 'win32' ? 'npm.cmd' : 'npm'

export default defineConfig({
  testDir: './e2e',
  testMatch: 'pwa-built.spec.ts',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: 'html',
  webServer: {
    command: `${npmCommand} run build && ${npmCommand} run preview -- --port ${previewPort} --strictPort`,
    url: previewUrl,
    reuseExistingServer: false,
    timeout: 240_000,
  },
  use: {
    baseURL: previewUrl,
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
