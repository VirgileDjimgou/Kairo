#!/usr/bin/env node
/**
 * Real full-stack release gate (Roadmap V2 Sprint 128).
 *
 * Runs against the real production-like stack (nginx -> Vue/PWA -> FastAPI ->
 * PostgreSQL -> domain events -> notification outbox -> Celery worker -> inbox)
 * with seeded COMBIS and Tenant X data. No API mocking.
 *
 * Environment:
 *   KAIRO_GATE_BASE_URL  Web/nginx origin (default http://localhost:8080)
 *
 * Exit code 0 only when every scenario step passes.
 */
import http from 'node:http'

const baseUrl = (process.env.KAIRO_GATE_BASE_URL || 'http://localhost:8080').replace(/\/$/, '')
const apiUrl = `${baseUrl}/api/v1`
const proxy = new URL(baseUrl)

const PASSED = []
const FAILED = []

function record(ok, label, detail = '') {
  if (ok) {
    PASSED.push(label)
    console.log(`PASS ${label}`)
  } else {
    FAILED.push(label)
    console.error(`FAIL ${label}${detail ? ` :: ${detail}` : ''}`)
  }
}

function assert(condition, label, detail = '') {
  record(Boolean(condition), label, detail)
}

async function request(method, path, { token, body, headers } = {}) {
  const response = await fetch(`${apiUrl}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(headers || {}),
    },
    ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
  })
  let payload = null
  const text = await response.text()
  if (text) {
    try {
      payload = JSON.parse(text)
    } catch {
      payload = text
    }
  }
  return { status: response.status, body: payload }
}

async function login(email, password) {
  const response = await request('POST', '/auth/login', { body: { email, password } })
  if (response.status !== 200 || !response.body?.access_token) {
    throw new Error(`Login failed for ${email}: ${response.status} ${JSON.stringify(response.body)}`)
  }
  return response.body.access_token
}

async function waitForInboxEvent(token, eventType, timeoutMs = 90_000) {
  const deadline = Date.now() + timeoutMs
  while (Date.now() < deadline) {
    const response = await request('GET', '/notifications/inbox', { token })
    if (response.status === 200) {
      const item = (response.body.items || []).find((entry) => entry.event_type === eventType)
      if (item) return item
    }
    await new Promise((resolve) => setTimeout(resolve, 3000))
  }
  return null
}

function resolveHost(host) {
  return new Promise((resolve, reject) => {
    const req = http.request(
      {
        hostname: proxy.hostname,
        port: proxy.port || 80,
        path: '/api/v1/tenants/public/resolve',
        method: 'GET',
        headers: { Host: host },
      },
      (res) => {
        let data = ''
        res.on('data', (chunk) => { data += chunk })
        res.on('end', () => resolve({ status: res.statusCode, body: data ? JSON.parse(data) : null }))
      },
    )
    req.on('error', reject)
    req.end()
  })
}

async function requestRoot(path, { token } = {}) {
  const response = await fetch(`${baseUrl}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  })
  return { status: response.status, body: null }
}

async function main() {
  // 1. Health and readiness through the real gateway.
  const live = await requestRoot('/health/live')
  assert(live.status === 200, 'gateway serves /health/live', String(live.status))
  const ready = await requestRoot('/health/ready')
  assert(ready.status === 200, 'gateway serves /health/ready', String(ready.status))

  // 2. Seeded accounts authenticate against the real API.
  const admin = await login('combis-admin@gate.kairo.app', 'GateAdmin1!')
  const secretary = await login('combis-secretary@gate.kairo.app', 'GateSecretary1!')
  const treasurer = await login('combis-treasurer@gate.kairo.app', 'GateTreasurer1!')
  const tenantX = await login('tenantx-admin@gate.kairo.app', 'GateTenantX1!')
  record(true, 'seeded COMBIS and Tenant X accounts authenticate')

  // 3. Finance lifecycle: member -> receipt declared -> validated.
  const member = await request('POST', '/memberships/', {
    token: admin,
    body: {
      first_name: 'Gate',
      last_name: 'Member',
      display_name: 'Gate Member',
      email: 'gate-member@combis.kairo.app',
      membership_type: 'individual',
    },
  })
  assert(member.status === 201 && member.body?.id, 'principal admin creates a member', `${member.status}`)
  const memberId = member.body?.id

  const declaration = await request('POST', '/contributions/receipt-declarations', {
    token: secretary,
    body: {
      membership_profile_id: memberId,
      income_type: 'membership_contribution',
      amount: '25.00',
      currency: 'EUR',
      payment_method: 'cash',
      note: 'Release gate cash receipt',
    },
  })
  assert(declaration.status === 201 && declaration.body?.id, 'secretary declares a cash receipt', `${declaration.status}`)
  const declarationId = declaration.body?.id

  const submitted = await request('POST', `/contributions/receipt-declarations/${declarationId}/submit`, { token: secretary })
  assert(submitted.status === 200, 'declaration is submitted', `${submitted.status}`)

  const contribution = await request('POST', '/contributions/', {
    token: treasurer,
    body: {
      membership_profile_id: memberId,
      year: new Date().getFullYear(),
      expected_amount: '25.00',
      currency: 'EUR',
      status: 'pending',
    },
  })
  assert(contribution.status === 201 && contribution.body?.id, 'treasurer creates the member contribution record', `${contribution.status}`)
  const contributionId = contribution.body?.id

  const processed = await request('POST', `/contributions/receipt-declarations/${declarationId}/process`, {
    token: treasurer,
    body: {
      action: 'validated',
      contribution_record_id: contributionId,
      processed_amount: '25.00',
      handover_reminder_days: 2,
    },
  })
  assert(processed.status === 200, 'treasurer validates the receipt', `${processed.status} ${JSON.stringify(processed.body)}`)

  const payment = await request('POST', '/contributions/payments', {
    token: treasurer,
    body: {
      contribution_record_id: contributionId,
      amount: '25.00',
      currency: 'EUR',
      payment_method: 'cash',
    },
  })
  assert(payment.status === 201, 'treasurer records the payment', `${payment.status}`)

  const budget = await request('GET', `/contributions/annual-budget?year=${new Date().getFullYear()}`, { token: treasurer })
  const income = Number(budget.body?.income_total ?? 0)
  assert(budget.status === 200 && income >= 25, 'recorded income reaches the annual budget', `${income}`)

  // 4. Domain event -> outbox -> worker -> authenticated inbox.
  const declaredNotification = await waitForInboxEvent(treasurer, 'finance.receipt_declared')
  assert(Boolean(declaredNotification), 'treasurer receives the receipt-declared inbox event via the worker')
  assert(declaredNotification?.target_path === '/finance', 'notification deep link targets /finance', declaredNotification?.target_path)
  assert(Boolean(declaredNotification?.event_id), 'inbox event carries the domain event id', String(declaredNotification?.event_id))

  const validatedNotification = await waitForInboxEvent(secretary, 'finance.receipt_validated')
  assert(Boolean(validatedNotification), 'declarant receives the receipt-validated inbox event via the worker')

  // 5. Installation registration, preferences and revocation.
  const installationId = 'gate-installation-0000000000000001'
  const registered = await request('POST', '/notifications/devices', {
    token: treasurer,
    body: { installation_id: installationId, platform: 'Linux', browser: 'Gate', device_metadata: { display_mode: 'browser' } },
  })
  assert(registered.status === 204, 'installation registration succeeds', `${registered.status}`)

  const preferences = await request('GET', '/notifications/preferences', { token: treasurer })
  assert(preferences.status === 200, 'notification preferences are readable', `${preferences.status}`)
  const updatedPreferences = await request('PUT', '/notifications/preferences', {
    token: treasurer,
    body: { ...preferences.body, finance_enabled: true },
  })
  assert(updatedPreferences.status === 200 && updatedPreferences.body?.finance_enabled === true, 'notification preferences update')

  const revoked = await request('POST', `/notifications/devices/${installationId}/revoke`, { token: treasurer })
  assert(
    revoked.status === 200 && Number(revoked.body?.revoked_profiles ?? 0) >= 1,
    'installation revocation disables the profile binding',
    JSON.stringify(revoked.body),
  )

  // 6. Branding, manifest and host-based tenant resolution.
  const me = await request('GET', '/auth/me', { token: treasurer })
  const combisMembership = (me.body?.memberships || []).find((entry) => entry.slug === 'combis')
  assert(combisMembership?.branding?.display_name === 'COMBIS App', 'COMBIS branding reaches /auth/me')

  const manifest = await request('GET', '/tenants/public/combis/manifest')
  assert(manifest.status === 200 && manifest.body?.name === 'COMBIS App', 'tenant manifest serves COMBIS branding')
  assert((manifest.body?.icons || []).length >= 2, 'tenant manifest exposes launcher icons')

  const subdomain = await resolveHost('combis.kairo.test')
  assert(subdomain.status === 200 && subdomain.body?.slug === 'combis', 'platform subdomain resolves the tenant', JSON.stringify(subdomain.body))
  const customDomain = await resolveHost('app.combis.test')
  assert(
    customDomain.status === 200 && customDomain.body?.slug === 'combis',
    'custom domain resolves the tenant',
    `${customDomain.status} ${JSON.stringify(customDomain.body)}`,
  )
  const unknownHost = await resolveHost('unknown.gate.kairo.app')
  assert(unknownHost.status === 404, 'unknown host cannot select a tenant', String(unknownHost.status))

  // 7. Tenant isolation and authorization boundaries.
  const tenantXMe = await request('GET', '/auth/me', { token: tenantX })
  const tenantXSlugs = (tenantXMe.body?.memberships || []).map((entry) => entry.slug)
  assert(tenantXSlugs.length === 1 && tenantXSlugs[0] === 'tenant-x', 'Tenant X sees only its own membership', JSON.stringify(tenantXSlugs))

  const crossTenantMember = await request('GET', `/memberships/${memberId}`, { token: tenantX })
  assert([403, 404].includes(crossTenantMember.status), 'Tenant X cannot read a COMBIS member', String(crossTenantMember.status))

  const crossTenantProcess = await request('POST', `/contributions/receipt-declarations/${declarationId}/process`, {
    token: tenantX,
    body: { action: 'validated' },
  })
  assert([403, 404].includes(crossTenantProcess.status), 'cross-tenant receipt processing is denied', String(crossTenantProcess.status))

  const crossTenantInbox = await request('GET', '/notifications/inbox', { token: tenantX })
  const tenantXItems = Array.isArray(crossTenantInbox.body?.items) ? crossTenantInbox.body.items : []
  const leakedNotification = tenantXItems.some((entry) => String(entry.event_type).startsWith('finance.receipt'))
  assert(!leakedNotification, 'Tenant X inbox contains no COMBIS finance notification')

  const unauthorizedProcess = await request('POST', `/contributions/receipt-declarations/${declarationId}/process`, {
    token: secretary,
    body: { action: 'validated' },
  })
  assert(unauthorizedProcess.status === 403, 'declarant cannot process their own declaration', String(unauthorizedProcess.status))

  const unauthorizedFinance = await request('GET', `/contributions/annual-budget?year=${new Date().getFullYear()}`, { token: tenantX })
  assert(unauthorizedFinance.status === 403, 'unauthorized role cannot read the annual budget', String(unauthorizedFinance.status))

  console.log('')
  console.log(`Full-stack release gate: ${PASSED.length} passed, ${FAILED.length} failed`)
  if (FAILED.length > 0) {
    console.error('Failed steps:')
    for (const failure of FAILED) console.error(`- ${failure}`)
    process.exit(1)
  }
  console.log('FULL-STACK GATE PASS')
}

main().catch((error) => {
  console.error(`Full-stack gate crashed: ${error.message}`)
  process.exit(1)
})
