import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'

const WCAG_22_AA_TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']

const modules = {
  membership: true,
  contributions: true,
  policies: true,
  disciplinary: true,
  events: true,
  announcements: true,
  chat: true,
  notifications: true,
}

function makeMemberMeResponse() {
  return {
    id: 'user-member-1',
    email: 'member@demo.org',
    display_name: 'Member User',
    preferred_language: 'en',
    status: 'active',
    tenant_id: 'tenant-demo-1',
    roles: ['member'],
    last_login_at: null,
    memberships: [
      {
        tenant_id: 'tenant-demo-1',
        slug: 'demo',
        name: 'Demo Organization',
        roles: ['member'],
        branding: { primary_color: '#1f4f8f', logo_url: '' },
        modules,
        profile_type: 'member',
      },
    ],
  }
}

async function installAuthenticatedMemberRoutes(page: Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-accessibility-token')
  })

  await page.route('**/api/v1/**', async (route) => {
    await route.fulfill({
      status: 404,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'No accessibility mock for this request' }),
    })
  })

  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeMemberMeResponse()),
    })
  })

  await page.route('**/api/v1/contributions/receipt-declarations/me', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
  })

  await page.route('**/api/v1/notifications/', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
  })

  await page.route('**/api/v1/memberships/me/statement', async (route) => {
    const profile = {
      id: 'profile-member-1',
      tenant_id: 'tenant-demo-1',
      user_id: 'user-member-1',
      member_code: 'M-100',
      first_name: 'Member',
      last_name: 'User',
      display_name: 'Member User',
      email: 'member@demo.org',
      phone: null,
      status: 'active',
      joined_at: '2026-01-01T00:00:00Z',
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    }
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        profile,
        summary: {
          profile,
          total_expected: '120.00',
          total_paid: '45.00',
          total_balance: '75.00',
          contribution_count: 1,
        },
        contributions: [],
      }),
    })
  })

  await page.route('**/api/v1/announcements/active', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
  })

  await page.route('**/api/v1/events/public', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
  })

  await page.route('**/api/v1/documents/', async (route) => {
    await route.fulfill({ status: 200, contentType: 'application/json', body: '[]' })
  })

  await page.route('**/api/v1/tenants/tenant-demo-1/settings', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        tenant_id: 'tenant-demo-1',
        name: 'Demo Organization',
        slug: 'demo',
        default_language: 'en',
        branding: { primary_color: '#1f4f8f', logo_url: '' },
        modules,
        operations: {
          last_backup_at: '2026-07-02T03:00:00Z',
          last_backup_status: 'completed',
          last_backup_reference: 'kairo-backup-20260702_030000.tar.gz',
          last_restore_drill_at: '2026-06-28T12:00:00Z',
          last_restore_drill_status: 'passed',
          alert_posture: 'healthy',
          alert_contacts_configured: true,
          backup_retention_days: 30,
          notes: 'Latest drill completed with a clean restore.',
          backup_is_stale: false,
          restore_drill_is_stale: false,
          alert_is_healthy: true,
          overall_status: 'healthy',
          status_message: 'Recovery evidence looks current and healthy.',
        },
        updated_at: '2026-07-04T12:00:00Z',
      }),
    })
  })
}

type AxeViolationSummary = {
  id: string
  nodes: {
    target: unknown[]
    html: string
    any: { data?: Record<string, unknown> }[]
  }[]
}

function violationSummary(violations: AxeViolationSummary[]): string[] {
  return violations.map((violation) => {
    const nodes = violation.nodes
      .map((node) => {
        const data = node.any[0]?.data ?? {}
        const contrast =
          data.fgColor !== undefined
            ? ` [${String(data.fgColor)} on ${String(data.bgColor)} = ${String(data.contrastRatio)}, needs ${String(data.expectedContrastRatio)}]`
            : ''
        return `${node.target.join(' ')}${contrast} => ${node.html.slice(0, 100)}`
      })
      .join('\n    ')
    return `${violation.id} (${violation.nodes.length} node(s)):\n    ${nodes}`
  })
}

test.describe('Accessibility audit (WCAG 2.2 AA target)', () => {
  test('public login has no detectable WCAG 2.2 AA violations on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 })
    await page.goto('/login')
    await expect(page.locator('#signin-card')).toBeVisible()

    const results = await new AxeBuilder({ page }).withTags(WCAG_22_AA_TAGS).analyze()
    expect(violationSummary(results.violations)).toEqual([])
  })

  test('public login passes at the 320px mobile viewport without horizontal overflow', async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 568 })
    await page.goto('/login')
    await expect(page.locator('#email:visible')).toBeVisible()

    const hasHorizontalOverflow = await page.evaluate(
      () => document.documentElement.scrollWidth > window.innerWidth + 1,
    )
    expect(hasHorizontalOverflow).toBe(false)

    const results = await new AxeBuilder({ page }).withTags(WCAG_22_AA_TAGS).analyze()
    expect(violationSummary(results.violations)).toEqual([])
  })

  test('authenticated shell exposes landmarks and passes at phone and desktop widths', async ({ page }) => {
    await installAuthenticatedMemberRoutes(page)

    for (const viewport of [
      { width: 390, height: 844 },
      { width: 1280, height: 900 },
    ]) {
      await page.setViewportSize(viewport)
      await page.goto('/dashboard')
      await expect(page.locator('main#kairo-main-content')).toBeVisible()

      const hasHorizontalOverflow = await page.evaluate(
        () => document.documentElement.scrollWidth > window.innerWidth + 1,
      )
      expect(hasHorizontalOverflow).toBe(false)

      const results = await new AxeBuilder({ page }).withTags(WCAG_22_AA_TAGS).analyze()
      expect(violationSummary(results.violations)).toEqual([])
    }
  })

  test('keyboard users can skip to the main content with a visible skip link', async ({ page }) => {
    await installAuthenticatedMemberRoutes(page)
    await page.goto('/dashboard')
    await expect(page.locator('main#kairo-main-content')).toBeVisible()

    const firstTabbableIsSkipLink = await page.evaluate(() => {
      const candidates = Array.from(
        document.querySelectorAll<HTMLElement>(
          'a[href], button, input, select, textarea, [tabindex]',
        ),
      ).filter((element) => {
        if (element.tabIndex < 0 || element.hasAttribute('disabled')) return false
        const rect = element.getBoundingClientRect()
        return rect.width > 0 && rect.height > 0
      })
      return candidates[0]?.classList.contains('skip-link') ?? false
    })
    expect(firstTabbableIsSkipLink).toBe(true)

    const skipLink = page.locator('a.skip-link')
    await skipLink.focus()
    await expect(skipLink).toBeFocused()
    const skipLinkVisible = await skipLink.evaluate((element) => {
      const rect = element.getBoundingClientRect()
      return rect.width > 0 && rect.height > 0 && getComputedStyle(element).position === 'fixed'
    })
    expect(skipLinkVisible).toBe(true)

    await page.keyboard.press('Enter')
    const focusedMain = await page.evaluate(
      () => document.activeElement?.id === 'kairo-main-content',
    )
    expect(focusedMain).toBe(true)
  })

  test('keyboard focus stays visible on the login form', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 900 })
    await page.goto('/login')
    const email = page.locator('#email:visible')
    await email.focus()
    const focusStyle = await email.evaluate((element) => {
      const style = getComputedStyle(element)
      return { outlineStyle: style.outlineStyle, outlineWidth: style.outlineWidth, boxShadow: style.boxShadow }
    })
    expect(focusStyle.outlineStyle !== 'none' || focusStyle.boxShadow !== 'none').toBe(true)
    expect(Number.parseFloat(focusStyle.outlineWidth) > 0 || focusStyle.boxShadow !== 'none').toBe(true)

    await page.keyboard.press('Tab')
    await expect(page.locator('#password:visible')).toBeFocused()
  })

  test('reduced motion disables infinite animations', async ({ page }) => {
    await page.emulateMedia({ reducedMotion: 'reduce' })
    await page.goto('/login')
    await expect(page.locator('#signin-card')).toBeVisible()

    const offenders = await page.evaluate(() => {
      const problems: string[] = []
      for (const element of Array.from(document.querySelectorAll('*'))) {
        const style = getComputedStyle(element)
        if (style.animationName === 'none') continue
        if (style.animationIterationCount === 'infinite') {
          problems.push(`${element.tagName}.${element.className}: infinite iteration`)
        }
      }
      return problems
    })
    expect(offenders).toEqual([])
  })
})
