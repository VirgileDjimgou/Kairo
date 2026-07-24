import { test, expect } from '@playwright/test'

const MOBILE_VIEWPORTS = [
  { width: 320, height: 568, label: 'iPhone SE / Galaxy Fold' },
  { width: 360, height: 800, label: 'Galaxy S8 / Pixel 2' },
  { width: 390, height: 844, label: 'iPhone 14' },
  { width: 412, height: 915, label: 'Pixel 7 / Galaxy S20' },
  { width: 430, height: 932, label: 'iPhone 14 Pro Max' },
]

const TABLET_VIEWPORTS = [
  { width: 768, height: 1024, label: 'iPad Mini' },
  { width: 820, height: 1180, label: 'iPad Air' },
]

const DESKTOP_VIEWPORTS = [
  { width: 1280, height: 720, label: 'Desktop HD' },
  { width: 1440, height: 900, label: 'Desktop WXGA+' },
]

function makeMemberAuth() {
  return {
    access_token: 'test-access-token-member',
    token_type: 'bearer',
    user: {
      id: 'user-member-1',
      email: 'member@demo.org',
      display_name: 'Jean Dupont',
      roles: ['member'],
      locale: 'fr',
    },
    memberships: [
      {
        tenant_id: 'tenant-demo-1',
        slug: 'demo',
        name: 'Combis Sport Verein',
        roles: ['member'],
        branding: { primary_color: '#1a3f6b', logo_url: '' },
        modules: {
          membership: true, contributions: true, policies: true,
          disciplinary: true, events: true, announcements: true,
          chat: true, notifications: true,
        },
        profile_type: 'member',
      },
    ],
    requires_mfa: false,
  }
}

async function assertNoHorizontalOverflow(page: any) {
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth + 1,
  )
  expect(overflow).toBe(false)
}

async function setupAuth(page: any) {
  await page.route('**/api/v1/auth/profile', (route: any) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeMemberAuth().user),
    })
  })
  await page.evaluate(
    (auth: any) => {
      localStorage.setItem('access_token', auth.access_token)
      localStorage.setItem('tenant_id', auth.memberships[0].tenant_id)
    },
    makeMemberAuth(),
  )
}

test.describe('Mobile responsive — Login', () => {
  for (const vp of MOBILE_VIEWPORTS) {
    test(`login at ${vp.width}x${vp.height} (${vp.label})`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height })
      await page.goto('/login')

      await expect(page.locator('#signin-card')).toBeVisible()
      await expect(page.locator('input[type="email"]')).toBeVisible()
      await expect(page.locator('input[type="password"]')).toBeVisible()
      await expect(page.locator('button[type="submit"]')).toBeVisible()

      await assertNoHorizontalOverflow(page)

      // Verify the form is above the hero on mobile (order swap)
      const formCard = page.locator('#signin-card')
      const formRect = await formCard.boundingBox()
      const heroTitle = page.getByTestId('commercial-hero-title')
      if (await heroTitle.isVisible()) {
        const heroRect = await heroTitle.boundingBox()
        // Form should be above hero on mobile
        if (formRect && heroRect) {
          expect(formRect.y + formRect.height).toBeLessThanOrEqual(heroRect.y + heroRect.height)
        }
      }
    })
  }
})

test.describe('Mobile responsive — Auth recovery views', () => {
  const recoveryRoutes = [
    { path: '/forgot-password', keyElement: 'input[type="email"]' },
    { path: '/reset-password', keyElement: 'input[type="password"]' },
    { path: '/accept-invite', keyElement: 'input[type="text"]' },
  ]

  for (const vp of MOBILE_VIEWPORTS.slice(0, 2)) {
    for (const route of recoveryRoutes) {
      test(`${route.path} at ${vp.width}x${vp.height}`, async ({ page }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height })
        await page.goto(route.path)

        await expect(page.locator(route.keyElement).first()).toBeVisible()
        await assertNoHorizontalOverflow(page)
      })
    }
  }
})

test.describe('Mobile responsive — Dashboard', () => {
  for (const vp of MOBILE_VIEWPORTS) {
    test(`dashboard at ${vp.width}x${vp.height} (${vp.label})`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height })
      await setupAuth(page)

      // Mock dashboard API
      await page.route('**/api/v1/dashboard/**', (route: any) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ modules: {}, checklist: [], metrics: {} }),
        })
      })
      await page.route('**/api/v1/chat/**', (route: any) => {
        route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ conversations: [] }) })
      })

      await page.goto('/dashboard')
      await page.waitForLoadState('networkidle')

      await assertNoHorizontalOverflow(page)

      // Bottom navigation should be visible on mobile
      if (vp.width < 768) {
        const bottomNav = page.locator('.bottom-nav')
        await expect(bottomNav).toBeVisible()
      }
    })
  }
})

test.describe('Mobile responsive — Chat', () => {
  const mobileVps = MOBILE_VIEWPORTS.slice(0, 3)

  for (const vp of mobileVps) {
    test(`chat at ${vp.width}x${vp.height}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height })
      await setupAuth(page)

      await page.route('**/api/v1/chat/**', (route: any) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            conversations: [
              { id: 'conv-1', title: 'Test conversation', message_count: 3, last_message_preview: 'Hello' },
            ],
            allowed_domains: ['governance', 'member_finance'],
          }),
        })
      })

      await page.goto('/chat')
      await page.waitForLoadState('networkidle')

      await assertNoHorizontalOverflow(page)

      // On mobile, chat sidebar should be visible as full-screen list
      if (vp.width < 768) {
        const sidebar = page.locator('.chat-sidebar-wrapper')
        await expect(sidebar).toBeAttached()
      }
    })
  }
})

test.describe('Tablet responsive', () => {
  for (const vp of TABLET_VIEWPORTS) {
    test(`dashboard at ${vp.width}x${vp.height}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height })
      await setupAuth(page)

      await page.route('**/api/v1/dashboard/**', (route: any) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ modules: {}, checklist: [], metrics: {} }),
        })
      })
      await page.route('**/api/v1/chat/**', (route: any) => {
        route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ conversations: [] }) })
      })

      await page.goto('/dashboard')
      await page.waitForLoadState('networkidle')
      await assertNoHorizontalOverflow(page)
    })
  }
})

test.describe('Desktop responsive', () => {
  for (const vp of DESKTOP_VIEWPORTS) {
    test(`dashboard at ${vp.width}x${vp.height}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height })
      await setupAuth(page)

      await page.route('**/api/v1/dashboard/**', (route: any) => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ modules: {}, checklist: [], metrics: {} }),
        })
      })

      await page.goto('/dashboard')
      await page.waitForLoadState('networkidle')
      await assertNoHorizontalOverflow(page)

      // Sidebar should be visible on desktop
      const sidebar = page.locator('.sidebar').first()
      await expect(sidebar).toBeVisible()
    })
  }
})

test.describe('Safe areas and touch targets', () => {
  test('bottom nav has adequate touch targets', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })
    await setupAuth(page)

    await page.route('**/api/v1/dashboard/**', (route: any) => {
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ modules: {}, checklist: [], metrics: {} }) })
    })
    await page.route('**/api/v1/chat/**', (route: any) => {
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ conversations: [] }) })
    })

    await page.goto('/dashboard')
    await page.waitForLoadState('networkidle')

    const navItems = page.locator('.bottom-nav-item')
    const count = await navItems.count()

    for (let i = 0; i < count; i++) {
      const box = await navItems.nth(i).boundingBox()
      if (box) {
        // WCAG 2.2 AA: minimum 44×44px touch target
        expect(box.width).toBeGreaterThanOrEqual(44)
        expect(box.height).toBeGreaterThanOrEqual(44)
      }
    }
  })

  test('auth card is fully visible on small mobile', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 })
    await page.goto('/login')

    const card = page.locator('.auth-card').first()
    if (await card.isVisible()) {
      const box = await card.boundingBox()
      if (box) {
        // Card should fit within viewport
        expect(box.x).toBeGreaterThanOrEqual(0)
        expect(box.x + box.width).toBeLessThanOrEqual(320)
      }
    }

    await assertNoHorizontalOverflow(page)
  })
})
