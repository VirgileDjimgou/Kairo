import { expect, test, type Page } from '@playwright/test'

function makeCensorMeResponse() {
  return {
    id: 'user-censor-1',
    email: 'censor@demo.org',
    display_name: 'Censor Demo',
    status: 'active',
    tenant_id: 'tenant-demo-1',
    roles: ['censor'],
    last_login_at: null,
    memberships: [
      {
        tenant_id: 'tenant-demo-1',
        slug: 'demo',
        name: 'Demo Organization',
        roles: ['censor'],
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
    display_name: 'Treasurer Demo',
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

async function mockDisciplinaryWorkspace(page: Page) {
  const members = [
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
      joined_at: '2026-01-10T09:00:00Z',
      created_at: '2026-01-10T09:00:00Z',
      updated_at: '2026-01-10T09:00:00Z',
    },
    {
      id: 'member-2',
      tenant_id: 'tenant-demo-1',
      user_id: 'user-member-2',
      member_code: 'M002',
      first_name: 'Bob',
      last_name: 'Example',
      display_name: 'Bob Example',
      email: 'bob@example.org',
      phone: null,
      status: 'active',
      joined_at: '2026-02-15T09:00:00Z',
      created_at: '2026-02-15T09:00:00Z',
      updated_at: '2026-02-15T09:00:00Z',
    },
  ]

  const policies = [
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
  ]

  let records = [
    {
      id: 'disc-1',
      tenant_id: 'tenant-demo-1',
      membership_profile_id: 'member-1',
      membership_display_name: 'Alice Example',
      policy_record_id: 'policy-1',
      policy_title: 'Attendance Rule',
      title: 'Late arrival warning',
      description: 'Repeated late arrivals to the general assembly.',
      amount: '25.00',
      currency: 'EUR',
      status: 'open',
      recorded_by: 'user-censor-1',
      recorded_at: '2026-06-30T08:30:00Z',
      created_at: '2026-06-30T08:30:00Z',
      updated_at: '2026-06-30T08:30:00Z',
    },
  ]

  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-censor-token')
  })

  await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeCensorMeResponse()),
    })
  })

  await page.route('http://localhost:8000/api/v1/memberships/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(members),
    })
  })

  await page.route('http://localhost:8000/api/v1/policies/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(policies),
    })
  })

  await page.route('http://localhost:8000/api/v1/disciplinary/', async (route) => {
    const request = route.request()
    if (request.method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(records),
      })
      return
    }

    if (request.method() === 'POST') {
      const payload = request.postDataJSON() as {
        membership_profile_id: string
        policy_record_id?: string | null
        title: string
        description?: string | null
        amount?: string
        currency?: string
        status?: string
      }
      const created = {
        id: `disc-${records.length + 1}`,
        tenant_id: 'tenant-demo-1',
        membership_profile_id: payload.membership_profile_id,
        membership_display_name: members.find((member) => member.id === payload.membership_profile_id)?.display_name ?? 'Unknown member',
        policy_record_id: payload.policy_record_id ?? null,
        policy_title: payload.policy_record_id ? 'Attendance Rule' : null,
        title: payload.title,
        description: payload.description ?? null,
        amount: payload.amount ?? '0.00',
        currency: payload.currency ?? 'EUR',
        status: payload.status ?? 'open',
        recorded_by: 'user-censor-1',
        recorded_at: '2026-07-01T10:00:00Z',
        created_at: '2026-07-01T10:00:00Z',
        updated_at: '2026-07-01T10:00:00Z',
      }
      records = [created, ...records]
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(created),
      })
      return
    }
  })

  await page.route(/http:\/\/localhost:8000\/api\/v1\/disciplinary\/([^/]+)$/, async (route) => {
    const match = route.request().url().match(/disciplinary\/([^/]+)$/)
    const recordId = match?.[1]

    if (route.request().method() === 'PATCH') {
      const payload = route.request().postDataJSON() as {
        policy_record_id?: string | null
        title?: string
        description?: string | null
        amount?: string
        currency?: string
        status?: string
      }
      records = records.map((record) =>
        record.id === recordId
          ? {
              ...record,
              ...payload,
              updated_at: '2026-07-01T10:30:00Z',
            }
          : record,
      )
      const updated = records.find((record) => record.id === recordId)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(updated),
      })
      return
    }

    if (route.request().method() === 'DELETE') {
      records = records.filter((record) => record.id !== recordId)
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

test.describe('Censor workspace', () => {
  test('censor sees the dedicated disciplinary console and can create records', async ({ page }) => {
    await mockDisciplinaryWorkspace(page)
    await page.goto('/censor')

    await expect(page).toHaveURL(/\/censor$/)
    await expect(page.getByRole('heading', { name: 'Censor workspace' })).toBeVisible()
    await expect(page.getByTestId('censor-workspace-hero')).toContainText('explicit privacy boundaries')
    await expect(page.getByText('Late arrival warning')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Create record' })).toBeVisible()

    await page.getByLabel('Member').selectOption('member-2')
    await page.getByLabel('Policy').selectOption('policy-1')
    await page.getByLabel('Title').fill('Attendance follow-up')
    await page.getByLabel('Description').fill('Escalation for repeated absence.')
    await page.getByLabel('Amount').fill('15.00')
    await page.getByRole('button', { name: 'Create record' }).click()

    await expect(page.getByText('Attendance follow-up')).toBeVisible()
    await expect(page.getByText('Bob Example', { exact: true })).toBeVisible()
  })

  test('treasurer cannot enter the censor workspace route', async ({ page }) => {
    await mockTreasurerDenied(page)
    await page.goto('/censor')

    await expect(page.getByRole('heading', { name: 'Welcome back, Treasurer Demo' })).toBeVisible()
    await expect(page).toHaveURL(/\/dashboard$/)
    await expect(page.getByRole('link', { name: 'Disciplinary Console' })).toHaveCount(0)
  })
})
