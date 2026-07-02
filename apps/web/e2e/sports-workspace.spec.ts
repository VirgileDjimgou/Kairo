import { expect, test, type Page } from '@playwright/test'

function makeSportsManagerMeResponse() {
  return {
    id: 'user-sports-1',
    email: 'sports@demo.org',
    display_name: 'Sports Manager',
    status: 'active',
    tenant_id: 'tenant-demo-1',
    roles: ['sports_manager'],
    last_login_at: null,
    memberships: [
      {
        tenant_id: 'tenant-demo-1',
        slug: 'demo',
        name: 'Demo Organization',
        roles: ['sports_manager'],
        branding: {
          primary_color: '#1f4f8f',
          logo_url: '',
        },
        modules: {
          membership: true,
          contributions: true,
          policies: true,
          disciplinary: true,
          events: true,
          announcements: true,
          chat: true,
          notifications: true,
        },
        profile_type: 'staff',
      },
    ],
  }
}

function makeTreasurerMeResponse() {
  return {
    id: 'user-treasurer-1',
    email: 'treasurer@demo.org',
    display_name: 'Treasurer User',
    status: 'active',
    tenant_id: 'tenant-demo-1',
    roles: ['treasurer'],
    last_login_at: null,
    memberships: [
      {
        tenant_id: 'tenant-demo-1',
        slug: 'demo',
        name: 'Demo Organization',
        roles: ['treasurer'],
        branding: {
          primary_color: '#1f4f8f',
          logo_url: '',
        },
        modules: {
          membership: true,
          contributions: true,
          policies: true,
          disciplinary: true,
          events: true,
          announcements: true,
          chat: true,
          notifications: true,
        },
        profile_type: 'staff',
      },
    ],
  }
}

async function mockSportsWorkspace(page: Page) {
  let events = [
    {
      id: 'sports-1',
      tenant_id: 'tenant-demo-1',
      title: 'Weekly Training',
      description: 'Open training for registered players.',
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
  ]

  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-sports-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeSportsManagerMeResponse()),
    })
  })

  await page.route('http://localhost:8000/api/v1/sports/events', async (route) => {
    const request = route.request()

    if (request.method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(events),
      })
      return
    }

    if (request.method() === 'POST') {
      const payload = request.postDataJSON() as {
        title: string
        description?: string | null
        start_at: string
        end_at?: string | null
        location?: string | null
        visibility_scope?: string
        status?: string
        metadata_json?: { sport_type?: string }
      }
      const created = {
        id: `sports-${events.length + 1}`,
        tenant_id: 'tenant-demo-1',
        title: payload.title,
        description: payload.description ?? null,
        start_at: payload.start_at,
        end_at: payload.end_at ?? null,
        location: payload.location ?? null,
        visibility_scope: payload.visibility_scope ?? 'members_only',
        status: payload.status ?? 'published',
        metadata_json: {
          workspace: 'sports',
          sport_type: payload.metadata_json?.sport_type ?? 'training',
        },
        created_by: 'user-sports-1',
        created_at: '2026-07-01T10:30:00Z',
        updated_at: '2026-07-01T10:30:00Z',
      }
      events = [created, ...events]
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(created),
      })
      return
    }
  })

  await page.route(/http:\/\/localhost:8000\/api\/v1\/sports\/events\/([^/]+)$/, async (route) => {
    const request = route.request()
    const match = request.url().match(/sports\/events\/([^/]+)$/)
    const eventId = match?.[1]

    if (request.method() === 'PATCH') {
      const payload = request.postDataJSON() as {
        title?: string
        description?: string | null
        start_at?: string
        end_at?: string | null
        location?: string | null
        visibility_scope?: string
        status?: string
        metadata_json?: { sport_type?: string }
      }
      events = events.map((event) =>
        event.id === eventId
          ? {
              ...event,
              ...payload,
              metadata_json: {
                workspace: 'sports',
                sport_type: payload.metadata_json?.sport_type ?? event.metadata_json.sport_type,
              },
              updated_at: '2026-07-01T11:00:00Z',
            }
          : event,
      )
      const updated = events.find((event) => event.id === eventId)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(updated),
      })
      return
    }

    if (request.method() === 'DELETE') {
      events = events.filter((event) => event.id !== eventId)
      await route.fulfill({
        status: 204,
        contentType: 'application/json',
        body: '',
      })
    }
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })
}

async function mockTreasurerDenied(page: Page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-treasurer-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeTreasurerMeResponse()),
    })
  })

  await page.route('http://localhost:8000/api/v1/documents', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })

  await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([]),
    })
  })
}

test.describe('Sports workspace', () => {
  test('sports manager can create a sports event from the dedicated workspace', async ({ page }) => {
    await mockSportsWorkspace(page)
    await page.goto('/sports')

    await expect(page).toHaveURL(/\/sports$/)
    await expect(page.getByRole('heading', { name: 'Sports workspace' })).toBeVisible()
    await expect(page.getByTestId('sports-workspace-hero')).toContainText('focused workspace')
    await expect(page.getByText('Weekly Training')).toBeVisible()

    await page.getByLabel('Title').fill('Club Championship')
    await page.getByLabel('Sport type').fill('match')
    await page.getByLabel('Description').fill('Club championship fixture.')
    await page.getByLabel('Start').fill('2026-07-20T18:00')
    await page.getByLabel('End').fill('2026-07-20T20:00')
    await page.getByLabel('Location').fill('Main Stadium')
    await page.getByRole('button', { name: 'Create event' }).click()

    await expect(page.getByText('Club Championship')).toBeVisible()
    await expect(page.getByText('match', { exact: true })).toBeVisible()

    await page.getByRole('button', { name: 'Edit sports event' }).first().click()
    await page.getByLabel('Title').fill('Club Championship Final')
    await page.getByRole('button', { name: 'Update event' }).click()
    await expect(page.getByText('Club Championship Final')).toBeVisible()
  })

  test('treasurer cannot enter the sports workspace route', async ({ page }) => {
    await mockTreasurerDenied(page)
    await page.goto('/sports')

    await expect(page.getByRole('heading', { name: 'Welcome back, Treasurer User' })).toBeVisible()
    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByRole('link', { name: 'Sports Workspace' })).toHaveCount(0)
  })
})
