import { expect, test, type Page } from '@playwright/test'

function makeTreasurerMeResponse() {
  return {
    id: 'user-treasurer-1',
    email: 'treasurer@demo.org',
    display_name: 'Treasurer Demo',
    preferred_language: 'en',
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
        profile_type: 'treasurer',
      },
    ],
  }
}

async function mockFinanceWorkspace(page: Page) {
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

  let contributions = [
    {
      id: 'contrib-1',
      tenant_id: 'tenant-demo-1',
      membership_profile_id: 'member-1',
      year: 2026,
      expected_amount: '120.00',
      paid_amount: '40.00',
      balance: '80.00',
      currency: 'EUR',
      status: 'partial',
      due_date: null,
      created_at: '2026-03-01T10:00:00Z',
      updated_at: '2026-03-15T10:00:00Z',
    },
  ]

  let payments = [
    {
      id: 'payment-seed-1',
      tenant_id: 'tenant-demo-1',
      contribution_record_id: 'contrib-1',
      amount: '40.00',
      currency: 'EUR',
      paid_at: '2026-03-15T10:00:00Z',
      payment_method: 'bank_transfer',
      reference: 'INV-001',
      recorded_by: 'user-treasurer-1',
      created_at: '2026-03-15T10:00:00Z',
    },
  ]

  let reminders = [
    {
      id: 'reminder-seed-1',
      tenant_id: 'tenant-demo-1',
      contribution_record_id: 'contrib-1',
      membership_profile_id: 'member-1',
      member_display_name: 'Alice Example',
      member_code: 'M001',
      balance_snapshot: '80.00',
      due_date_snapshot: '2026-01-31T00:00:00Z',
      channel: 'email',
      delivery_status: 'sent',
      recipient: 'alice@example.org',
      subject: 'Contribution reminder for 2026',
      body: 'Reminder body',
      provider_message: 'Reminder email accepted by fake provider.',
      reminded_by: 'user-treasurer-1',
      sent_at: '2026-03-18T10:00:00Z',
      created_at: '2026-03-18T10:00:00Z',
    },
  ]

  function buildSummary(year?: number) {
    const scoped = contributions.filter((item) => !year || item.year === year)
    const totalExpected = scoped.reduce((sum, item) => sum + Number(item.expected_amount), 0)
    const totalPaid = scoped.reduce((sum, item) => sum + Number(item.paid_amount), 0)
    const totalBalance = scoped.reduce((sum, item) => sum + Number(item.balance), 0)
    return {
      total_count: scoped.length,
      total_expected: totalExpected.toFixed(2),
      total_paid: totalPaid.toFixed(2),
      total_balance: totalBalance.toFixed(2),
    }
  }

  function buildMemberBalance(profileId: string) {
    const profile = members.find((member) => member.id === profileId)
    const scoped = contributions.filter((item) => item.membership_profile_id === profileId)
    const totalExpected = scoped.reduce((sum, item) => sum + Number(item.expected_amount), 0)
    const totalPaid = scoped.reduce((sum, item) => sum + Number(item.paid_amount), 0)
    const totalBalance = scoped.reduce((sum, item) => sum + Number(item.balance), 0)
    return {
      profile,
      total_expected: totalExpected.toFixed(2),
      total_paid: totalPaid.toFixed(2),
      total_balance: totalBalance.toFixed(2),
      contribution_count: scoped.length,
    }
  }

  await page.addInitScript(() => {
    window.localStorage.setItem('access_token', 'playwright-treasurer-token')
  })

  await page.route(/http:\/\/localhost:8000\/api\/v1\/auth\/me$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(makeTreasurerMeResponse()),
    })
  })

  await page.route(/http:\/\/localhost:8000\/api\/v1\/memberships\/?$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(members),
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

  await page.route(/http:\/\/localhost:8000\/api\/v1\/memberships\/([^/]+)\/balance$/, async (route) => {
    const match = route.request().url().match(/memberships\/([^/]+)\/balance$/)
    const profileId = match?.[1] ?? ''
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(buildMemberBalance(profileId)),
    })
  })

  await page.route(/http:\/\/localhost:8000\/api\/v1\/contributions\/summary(?:\?.*)?$/, async (route) => {
    const url = new URL(route.request().url())
    const year = Number(url.searchParams.get('year') ?? '0') || undefined
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(buildSummary(year)),
    })
  })

  await page.route(/http:\/\/localhost:8000\/api\/v1\/contributions\/payments$/, async (route) => {
    if (route.request().method() === 'GET') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(payments),
      })
      return
    }

    const payload = route.request().postDataJSON() as {
      contribution_record_id: string
      amount: string
      payment_method: string
      reference?: string | null
    }
    contributions = contributions.map((item) => {
      if (item.id !== payload.contribution_record_id) return item
      const paidAmount = Number(item.paid_amount) + Number(payload.amount)
      const balance = Math.max(Number(item.expected_amount) - paidAmount, 0)
      return {
        ...item,
        paid_amount: paidAmount.toFixed(2),
        balance: balance.toFixed(2),
        status: balance === 0 ? 'paid' : 'partial',
        updated_at: '2026-06-30T12:00:00Z',
      }
    })
    const createdPayment = {
      id: `payment-${payments.length + 1}`,
      tenant_id: 'tenant-demo-1',
      contribution_record_id: payload.contribution_record_id,
      amount: payload.amount,
      currency: 'EUR',
      paid_at: '2026-06-30T12:00:00Z',
      payment_method: payload.payment_method,
      reference: payload.reference ?? null,
      recorded_by: 'user-treasurer-1',
      created_at: '2026-06-30T12:00:00Z',
    }
    payments = [createdPayment, ...payments]

    await route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify(createdPayment),
    })
  })

  await page.route(/http:\/\/localhost:8000\/api\/v1\/contributions\/reminders(?:\?.*)?$/, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(reminders),
    })
  })

  await page.route(/http:\/\/localhost:8000\/api\/v1\/contributions\/reminders\/send$/, async (route) => {
    const payload = route.request().postDataJSON() as {
      year?: number
      due_scope?: string
      limit?: number
    }
    const selected = contributions
      .filter((item) => Number(item.balance) > 0 && (!payload.year || item.year === payload.year))
      .slice(0, payload.limit || 25)
      .map((item, index) => {
        const member = members.find((entry) => entry.id === item.membership_profile_id)
        return {
          id: `reminder-batch-${index + 1}`,
          tenant_id: 'tenant-demo-1',
          contribution_record_id: item.id,
          membership_profile_id: item.membership_profile_id,
          member_display_name: member?.display_name || 'Unknown member',
          member_code: member?.member_code || 'N/A',
          balance_snapshot: item.balance,
          due_date_snapshot: item.due_date,
          channel: 'email',
          delivery_status: 'sent',
          recipient: member?.email || 'missing@example.org',
          subject: `Contribution reminder for ${item.year}`,
          body: 'Batch reminder body',
          provider_message: 'Reminder email accepted by fake provider.',
          reminded_by: 'user-treasurer-1',
          sent_at: '2026-06-30T13:00:00Z',
          created_at: '2026-06-30T13:00:00Z',
        }
      })
    reminders = [...selected, ...reminders]
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        attempted_count: selected.length,
        reminder_count: selected.length,
        reminders: selected,
      }),
    })
  })

  await page.route(/http:\/\/localhost:8000\/api\/v1\/contributions\/([^/]+)\/reminders\/send$/, async (route) => {
    const contributionId = route.request().url().match(/contributions\/([^/]+)\/reminders\/send$/)?.[1] || 'unknown'
    const contribution = contributions.find((item) => item.id === contributionId)
    const member = members.find((entry) => entry.id === contribution?.membership_profile_id)
    const created = {
      id: `reminder-${reminders.length + 1}`,
      tenant_id: 'tenant-demo-1',
      contribution_record_id: contributionId,
      membership_profile_id: contribution?.membership_profile_id || 'member-1',
      member_display_name: member?.display_name || 'Unknown member',
      member_code: member?.member_code || 'N/A',
      balance_snapshot: contribution?.balance || '0.00',
      due_date_snapshot: contribution?.due_date || null,
      channel: 'email',
      delivery_status: 'sent',
      recipient: member?.email || 'missing@example.org',
      subject: `Contribution reminder for ${contribution?.year || 2026}`,
      body: 'Single reminder body',
      provider_message: 'Reminder email accepted by fake provider.',
      reminded_by: 'user-treasurer-1',
      sent_at: '2026-06-30T12:30:00Z',
      created_at: '2026-06-30T12:30:00Z',
    }
    reminders = [created, ...reminders]
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(created),
    })
  })

  await page.route(/http:\/\/localhost:8000\/api\/v1\/contributions\/?(?:\?.*)?$/, async (route) => {
    const request = route.request()
    const url = new URL(request.url())

    if (request.method() === 'GET') {
      const year = Number(url.searchParams.get('year') ?? '0') || undefined
      const scoped = contributions.filter((item) => !year || item.year === year)
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(scoped),
      })
      return
    }

    if (request.method() === 'POST') {
      const payload = request.postDataJSON() as {
        membership_profile_id: string
        year: number
        expected_amount: string
        status: string
      }
      const created = {
        id: `contrib-${contributions.length + 1}`,
        tenant_id: 'tenant-demo-1',
        membership_profile_id: payload.membership_profile_id,
        year: payload.year,
        expected_amount: Number(payload.expected_amount).toFixed(2),
        paid_amount: '0.00',
        balance: Number(payload.expected_amount).toFixed(2),
        currency: 'EUR',
        status: payload.status,
        due_date: null,
        created_at: '2026-06-30T09:00:00Z',
        updated_at: '2026-06-30T09:00:00Z',
      }
      contributions = [created, ...contributions]
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify(created),
      })
    }
  })
}

function financeNavLink(page: Page) {
  return page.locator('aside a[href="/finance"]').first()
}

test.describe('Finance workspace', () => {
  test('shows the dedicated finance workspace to the treasurer role', async ({ page }) => {
    await mockFinanceWorkspace(page)
    await page.goto('/login')
    await page.evaluate(() => {
      window.localStorage.setItem('access_token', 'playwright-treasurer-token')
    })
    await page.goto('/dashboard')
    await expect(financeNavLink(page)).toBeVisible()
    await financeNavLink(page).click()

    await expect(page).toHaveURL(/\/finance$/)
    await expect(page.getByRole('heading', { name: 'Treasury operations' })).toBeVisible()
    await expect(financeNavLink(page)).toBeVisible()
    await expect(page.getByRole('link', { name: 'Admin' })).toHaveCount(0)

    await page.getByLabel('Member').first().selectOption('member-1')
    await expect(page.getByTestId('finance-member-balance')).toContainText('80.00 EUR')
  })

  test('records a payment and creates a new contribution from the finance workspace', async ({ page }) => {
    await mockFinanceWorkspace(page)
    await page.goto('/login')
    await page.evaluate(() => {
      window.localStorage.setItem('access_token', 'playwright-treasurer-token')
    })
    await page.goto('/dashboard')
    await expect(financeNavLink(page)).toBeVisible()
    await financeNavLink(page).click()

    await page.getByRole('button', { name: 'Record payment' }).first().click()
    await page.getByLabel('Amount (EUR)', { exact: true }).fill('80.00')
    await page.getByRole('button', { name: 'Record payment', exact: true }).first().click()

    await expect(page.getByRole('cell', { name: '0.00' }).first()).toBeVisible()
    await expect(page.getByText('paid').first()).toBeVisible()

    await page.getByLabel('Member').nth(1).selectOption('member-2')
    await page.getByLabel('Expected amount (EUR)', { exact: true }).fill('150.00')
    await page.getByRole('button', { name: 'Create contribution' }).click()

    await expect(page.getByRole('cell', { name: 'Bob Example (M002)' }).first()).toBeVisible()
    await expect(page.getByRole('cell', { name: '150.00' }).first()).toBeVisible()
  })

  test('sends reminder workflows and shows reminder history', async ({ page }) => {
    await mockFinanceWorkspace(page)
    await page.goto('/dashboard')
    await financeNavLink(page).click()

    await expect(page.getByRole('heading', { name: 'Reminders' })).toBeVisible()
    await expect(page.getByTestId('finance-reminder-history')).toContainText('Alice Example')

    await page.getByRole('button', { name: 'Remind' }).first().click()
    await expect(page.getByRole('status')).toContainText('Sent reminder for Alice Example.')
    await expect(page.getByTestId('finance-reminder-history')).toContainText('Contribution reminder for 2026')

    await page.getByRole('button', { name: 'Send batch' }).click()
    await expect(page.getByRole('status')).toContainText('Processed 1 reminder target(s).')
  })
})
