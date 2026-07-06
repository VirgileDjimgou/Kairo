import { expect, test, type Page } from '@playwright/test'

type ModuleToggles = {
  membership: boolean
  contributions: boolean
  policies: boolean
  disciplinary: boolean
  events: boolean
  announcements: boolean
  chat: boolean
  notifications: boolean
}

type RoleCase = {
  role: 'member' | 'secretary_general' | 'treasurer' | 'auditor' | 'censor' | 'sports_manager' | 'president' | 'vice_president' | 'principal_admin'
  email: string
  displayName: string
  profileType: 'member' | 'staff' | 'admin'
  landingPath: string
  landingHeading: string
  roleLinkLabel?: string
  landingTitleTestId?: string
  landingTitleText?: string
  deniedPath?: string
}

const modules: ModuleToggles = {
  membership: true,
  contributions: true,
  policies: true,
  disciplinary: true,
  events: true,
  announcements: true,
  chat: true,
  notifications: true,
}

function makeMeResponse(caseItem: RoleCase) {
  return {
    id: `user-${caseItem.role}-1`,
    email: caseItem.email,
    display_name: caseItem.displayName,
    status: 'active',
    tenant_id: 'tenant-demo-1',
    roles: [caseItem.role],
    last_login_at: null,
    memberships: [
      {
        tenant_id: 'tenant-demo-1',
        slug: 'demo',
        name: 'Demo Organization',
        roles: [caseItem.role],
        branding: {
          primary_color: '#1f4f8f',
          logo_url: '',
        },
        modules,
        profile_type: caseItem.profileType,
      },
    ],
  }
}

async function installBaseRoutes(page: Page, caseItem: RoleCase) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-release-candidate-token')
  })

  await page.route('**/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeMeResponse(caseItem)),
    })
  })

  await page.route('**/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('**/api/v1/memberships/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        {
          id: 'member-1',
          tenant_id: 'tenant-demo-1',
          user_id: 'user-member-1',
          member_code: 'M001',
          first_name: 'Alice',
          last_name: 'Example',
          display_name: 'Alice Example',
          email: 'alice@example.org',
          phone: null,
          status: 'active',
          joined_at: '2026-06-01T00:00:00Z',
          created_at: '2026-06-01T00:00:00Z',
          updated_at: '2026-06-01T00:00:00Z',
        },
      ]),
    })
  })

  await page.route('**/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('**/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
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
        branding: {
          primary_color: '#1f4f8f',
          logo_url: '',
        },
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

async function installRoleRoutes(page: Page, caseItem: RoleCase) {
  switch (caseItem.role) {
    case 'member':
      await page.route('**/api/v1/memberships/me/statement', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            profile: {
              id: 'profile-member-1',
              tenant_id: 'tenant-demo-1',
              user_id: 'user-member-1',
              member_code: 'M-100',
              first_name: 'Member',
              last_name: 'User',
              display_name: 'Member User',
              email: caseItem.email,
              phone: null,
              status: 'active',
              joined_at: '2026-01-01T00:00:00Z',
              created_at: '2026-01-01T00:00:00Z',
              updated_at: '2026-01-01T00:00:00Z',
            },
            summary: {
              profile: {
                id: 'profile-member-1',
                tenant_id: 'tenant-demo-1',
                user_id: 'user-member-1',
                member_code: 'M-100',
                first_name: 'Member',
                last_name: 'User',
                display_name: 'Member User',
                email: caseItem.email,
                phone: null,
                status: 'active',
                joined_at: '2026-01-01T00:00:00Z',
                created_at: '2026-01-01T00:00:00Z',
                updated_at: '2026-01-01T00:00:00Z',
              },
              total_expected: '120.00',
              total_paid: '45.00',
              total_balance: '75.00',
              contribution_count: 1,
            },
            contributions: [],
          }),
        })
      })
      break
    case 'secretary_general':
      await page.route('**/api/v1/policies/categories', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ categories: ['governance', 'communications'] }),
        })
      })
      await page.route('**/api/v1/policies/', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        })
      })
      await page.route('**/api/v1/announcements/', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        })
      })
      break
    case 'treasurer':
      await page.route('**/api/v1/contributions/summary**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            total_count: 2,
            total_expected: '200.00',
            total_paid: '125.00',
            total_balance: '75.00',
          }),
        })
      })
      await page.route('**/api/v1/contributions/payments', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        })
      })
      await page.route('**/api/v1/contributions/?**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        })
      })
      break
    case 'auditor':
      await page.route('**/api/v1/contributions/summary**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            total_count: 2,
            total_expected: '200.00',
            total_paid: '125.00',
            total_balance: '75.00',
          }),
        })
      })
      await page.route('**/api/v1/contributions/payments', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        })
      })
      await page.route('**/api/v1/contributions/report/export**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'text/csv',
          body: 'contribution_id,membership_profile_id,year\n',
        })
      })
      await page.route('**/api/v1/contributions/?**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        })
      })
      break
    case 'censor':
      await page.route('**/api/v1/policies/', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              id: 'policy-1',
              tenant_id: 'tenant-demo-1',
              title: 'Attendance Rule',
              category: 'conduct',
              description: 'Members must attend scheduled meetings.',
              status: 'published',
              document_id: null,
              created_at: '2026-02-01T09:00:00Z',
              updated_at: '2026-02-01T09:00:00Z',
            },
          ]),
        })
      })
      await page.route('**/api/v1/disciplinary/', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        })
      })
      break
    case 'sports_manager':
      await page.route('**/api/v1/sports/events', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([
            {
              id: 'sports-1',
              tenant_id: 'tenant-demo-1',
              title: 'Weekly Training',
              description: 'Open training session.',
              start_at: '2026-07-10T18:00:00Z',
              end_at: '2026-07-10T20:00:00Z',
              location: 'Pitch 1',
              visibility_scope: 'members_only',
              status: 'published',
              metadata_json: { workspace: 'sports', sport_type: 'training' },
              created_by: 'user-sports-1',
              created_at: '2026-07-01T10:00:00Z',
              updated_at: '2026-07-01T10:00:00Z',
            },
          ]),
        })
      })
      break
    case 'president':
      await page.route('**/api/v1/admin/audit/events**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        })
      })
      await page.route('**/api/v1/contributions/summary**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            total_count: 2,
            total_expected: '200.00',
            total_paid: '125.00',
            total_balance: '75.00',
          }),
        })
      })
      break
    case 'vice_president':
      await page.route('**/api/v1/contributions/summary**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            total_count: 2,
            total_expected: '200.00',
            total_paid: '125.00',
            total_balance: '75.00',
          }),
        })
      })
      break
    case 'principal_admin':
      await page.route('**/api/v1/admin/audit/events**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        })
      })
      await page.route('**/api/v1/admin/ingestion-jobs/health**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            queued_count: 0,
            processing_count: 0,
            failed_count: 0,
            completed_count: 0,
            retried_count: 0,
            recent_failures: [],
          }),
        })
      })
      await page.route('**/api/v1/notifications/channels', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([]),
        })
      })
      await page.route('**/api/v1/contributions/summary**', async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            total_count: 2,
            total_expected: '200.00',
            total_paid: '125.00',
            total_balance: '75.00',
          }),
        })
      })
      break
  }
}

const roleCases: RoleCase[] = [
  {
    role: 'member',
    email: 'member@demo.org',
    displayName: 'Member User',
    profileType: 'member',
    landingPath: '/members/profile',
    landingHeading: 'My profile and contribution statement',
    roleLinkLabel: 'My profile',
    deniedPath: '/finance',
  },
  {
    role: 'secretary_general',
    email: 'secretary@demo.org',
    displayName: 'Secretary General',
    profileType: 'staff',
    landingPath: '/secretary',
    landingHeading: 'Official records and communication workspace',
    roleLinkLabel: 'Secretary workspace',
    deniedPath: '/finance',
  },
  {
    role: 'treasurer',
    email: 'treasurer@demo.org',
    displayName: 'Treasurer User',
    profileType: 'staff',
    landingPath: '/finance',
    landingHeading: 'Treasury operations',
    roleLinkLabel: 'Finance workspace',
    deniedPath: '/secretary',
  },
  {
    role: 'auditor',
    email: 'auditor@demo.org',
    displayName: 'Auditor User',
    profileType: 'staff',
    landingPath: '/finance-audit',
    landingHeading: 'Read-only finance oversight',
    roleLinkLabel: 'Finance audit',
    deniedPath: '/finance',
  },
  {
    role: 'censor',
    email: 'censor@demo.org',
    displayName: 'Censor User',
    profileType: 'staff',
    landingPath: '/censor',
    landingHeading: 'Censor workspace',
    roleLinkLabel: 'Disciplinary console',
    deniedPath: '/finance',
  },
  {
    role: 'sports_manager',
    email: 'sports@demo.org',
    displayName: 'Sports Manager',
    profileType: 'staff',
    landingPath: '/sports',
    landingHeading: 'Sports workspace',
    roleLinkLabel: 'Sports workspace',
    deniedPath: '/admin',
  },
  {
    role: 'president',
    email: 'president@demo.org',
    displayName: 'President User',
    profileType: 'staff',
    landingPath: '/governance',
    landingHeading: 'President governance cockpit',
    roleLinkLabel: 'Governance cockpit',
    deniedPath: '/admin',
  },
  {
    role: 'vice_president',
    email: 'vice-president@demo.org',
    displayName: 'Vice President User',
    profileType: 'staff',
    landingPath: '/governance',
    landingHeading: 'Vice president governance cockpit',
    roleLinkLabel: 'Governance cockpit',
    deniedPath: '/admin',
  },
  {
    role: 'principal_admin',
    email: 'principal@demo.org',
    displayName: 'Principal Admin User',
    profileType: 'admin',
    landingPath: '/admin',
    landingHeading: 'Principal admin overview',
    landingTitleTestId: 'admin-layout-title',
    landingTitleText: 'Principal Admin Control Plane',
  },
]

test.describe('Release candidate regression matrix', () => {
  for (const caseItem of roleCases) {
    test(`${caseItem.role} lands in the expected workspace and keeps the right sidebar link`, async ({ page }) => {
      await installBaseRoutes(page, caseItem)
      await installRoleRoutes(page, caseItem)
      await page.goto(caseItem.landingPath)

      await expect(page.getByRole('heading', { name: caseItem.landingHeading })).toBeVisible()
      if (caseItem.roleLinkLabel) {
        await expect(page.locator('aside.sidebar').getByRole('link', { name: caseItem.roleLinkLabel })).toBeVisible()
      }
      if (caseItem.landingTitleTestId && caseItem.landingTitleText) {
        await expect(page.getByTestId(caseItem.landingTitleTestId)).toHaveText(caseItem.landingTitleText)
      }

      if (caseItem.deniedPath) {
        await page.goto(caseItem.deniedPath)
        await expect(page).toHaveURL(/\/dashboard$/)
      }
    })
  }
})
