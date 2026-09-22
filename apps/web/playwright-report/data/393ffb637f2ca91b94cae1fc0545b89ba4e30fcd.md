# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: censor-workspace.spec.ts >> Censor workspace >> secretary general can review disciplinary records without mutation controls
- Location: e2e\censor-workspace.spec.ts:446:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('heading', { name: 'Read-only oversight' })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByRole('heading', { name: 'Read-only oversight' })

```

```yaml
- complementary:
  - text:  Demo Organization
  - navigation:
    - text: Personal
    - link " Dashboard":
      - /url: /dashboard
    - link " My profile":
      - /url: /members/profile
    - link " Account security":
      - /url: /account/security
    - link " Chat":
      - /url: /chat
    - text: Workspaces
    - link " Secretary workspace":
      - /url: /secretary
    - text: Community
    - link " Events":
      - /url: /events
    - link " Announcements":
      - /url: /announcements
    - link " Policies and rules":
      - /url: /policies
  - text:  Secretary General Demo secretary@demo.org
  - button " Sign out"
- main:
  - text: Secretary workspace Demo Organization
  - combobox:
    - option "Français"
    - option "English" [selected]
    - option "Deutsch"
  - button " Secretary General Demo"
  - text: Secretary workspace
  - heading "Welcome back, Secretary General Demo" [level=1]
  - paragraph: Your current tenant is Demo Organization. Keep documents, policies, and announcements tidy from the secretary workspace.
  - text:  Setup mode Secretary workspace
  - heading "Documents, policies, and announcements" [level=2]
  - paragraph: Stay inside the secretary workspace to update documents, maintain policies, and publish association announcements.
  - link "Open secretary workspace":
    - /url: /secretary
  - link "Review documents":
    - /url: /secretary/documents
  - link "Review policies":
    - /url: /secretary/policies
  - link "Review announcements":
    - /url: /secretary/announcements
  - text: First-run checklist
  - heading "This tenant is still in setup mode" [level=2]
  - paragraph: Use the checklist below to move from a blank tenant into a working environment with documents, members, and first communications.
  - text: 0% complete
  - progressbar
  - text:  Next best action
  - paragraph: "Publish a first announcement: Share a welcome message, launch note, or support contact so people see the tenant as active."
  - link "Create announcement":
    - /url: /announcements
  - article:
    - text:  Publish a first announcement
    - paragraph: Share a welcome message, launch note, or support contact so people see the tenant as active.
    - text: Pending
    - link "Create announcement":
      - /url: /announcements
  - article:
    - text:  Schedule the first event
    - paragraph: Add a meeting, onboarding call, or community event to give the tenant an immediate rhythm.
    - text: Pending
    - link "Create event":
      - /url: /events
  - text: Tenant snapshot
  - heading "Live usage signals" [level=2]
  - button "Refresh"
  - text: Documents 0 Knowledge base readiness Members 0 Operational directory Announcements 0 Public communication Events 0 Community cadence
  - separator
  - text: Current tenant Tenant Demo Organization Role secretary_general Checklist complete 0 / 2 Last refresh Aug 20, 2026, 11:17 PM Quick actions
  - link " Open secretary workspace":
    - /url: /secretary
  - link " Review documents":
    - /url: /secretary/documents
  - link " Review policies":
    - /url: /secretary/policies
  - link " Review announcements":
    - /url: /secretary/announcements
  - link " Open health center":
    - /url: /admin/health
  - link " Review events":
    - /url: /events
```

# Test source

```ts
  351 | 
  352 |   await page.route('http://localhost:8000/api/v1/documents', async (route) => {
  353 |     await route.fulfill({
  354 |       status: 200,
  355 |       contentType: 'application/json',
  356 |       body: JSON.stringify([]),
  357 |     })
  358 |   })
  359 | 
  360 |   await page.route('http://localhost:8000/api/v1/announcements/active', async (route) => {
  361 |     await route.fulfill({
  362 |       status: 200,
  363 |       contentType: 'application/json',
  364 |       body: JSON.stringify([]),
  365 |     })
  366 |   })
  367 | 
  368 |   await page.route('http://localhost:8000/api/v1/events/public', async (route) => {
  369 |     await route.fulfill({
  370 |       status: 200,
  371 |       contentType: 'application/json',
  372 |       body: JSON.stringify([]),
  373 |     })
  374 |   })
  375 | }
  376 | 
  377 | test.describe('Censor workspace', () => {
  378 |   test('censor sees the dedicated disciplinary console and can create records', async ({ page }) => {
  379 |     const { policyRequests } = await mockDisciplinaryWorkspace(page)
  380 |     await page.goto('/censor')
  381 | 
  382 |     await expect(page).toHaveURL(/\/censor$/)
  383 |     await expect(page.getByRole('heading', { name: 'Censor workspace' })).toBeVisible()
  384 |     await expect(page.getByTestId('censor-workspace-hero')).toContainText('explicit privacy boundaries')
  385 |     await expect(page.locator('.desktop-data-table').getByText('Late arrival warning')).toBeVisible()
  386 |     await expect(page.getByRole('button', { name: 'Create record' })).toBeVisible()
  387 | 
  388 |     const memberSearch = page.getByPlaceholder('Search for a member…')
  389 |     await expect(memberSearch).toHaveCount(1)
  390 |     await memberSearch.fill('bob@example')
  391 |     const memberResults = page.locator('.discipline-member-results')
  392 |     await expect(memberResults).toHaveCount(1)
  393 |     const bobResult = memberResults.getByText('Bob Example', { exact: true })
  394 |     await expect(bobResult).toHaveCount(1)
  395 |     await bobResult.click()
  396 |     await expect(page.getByRole('heading', { name: 'Bob Example' })).toBeVisible()
  397 |     await expect(page.getByText('No sanction is recorded for this member.')).toBeVisible()
  398 | 
  399 |     await page.getByLabel('Member', { exact: true }).selectOption('member-2')
  400 |     await page.getByLabel('Policy').selectOption('policy-1')
  401 |     await page.getByLabel('Title').fill('Attendance follow-up')
  402 |     await page.getByLabel('Description').fill('Escalation for repeated absence.')
  403 |     await page.getByLabel('Amount').fill('15.00')
  404 |     await page.getByRole('button', { name: 'Create record' }).click()
  405 | 
  406 |     await expect(page.locator('.desktop-data-table').getByText('Attendance follow-up')).toBeVisible()
  407 |     await expect(page.locator('.desktop-data-table').getByText('Bob Example', { exact: true })).toBeVisible()
  408 |     await expect(page.locator('.discipline-history-table').getByText('Attendance follow-up')).toBeVisible()
  409 |     expect(policyRequests.length).toBeGreaterThan(0)
  410 |     expect(policyRequests.every((request) => request.endsWith('/api/v1/policies/public'))).toBe(true)
  411 |     await captureRoleProof(page, 'discipline-censor-read-write.png')
  412 |   })
  413 | 
  414 |   test('treasurer cannot enter the censor workspace route', async ({ page }) => {
  415 |     await mockTreasurerDenied(page)
  416 |     await page.goto('/censor')
  417 | 
  418 |     await expect(page.getByRole('heading', { name: 'Welcome back, Treasurer Demo' })).toBeVisible()
  419 |     await expect(page).toHaveURL(/\/dashboard$/)
  420 |     await expect(page.getByRole('link', { name: 'Disciplinary Console' })).toHaveCount(0)
  421 |   })
  422 | 
  423 |   test('president can review disciplinary records without requesting policy management data', async ({ page }) => {
  424 |     const { policyRequests } = await mockDisciplinaryWorkspace(page, makePresidentMeResponse())
  425 |     await page.goto('/censor')
  426 | 
  427 |     await expect(page).toHaveURL(/\/censor$/)
  428 |     await expect(page.getByRole('heading', { name: 'Censor workspace' })).toBeVisible()
  429 |     await expect(page.getByRole('heading', { name: 'Read-only oversight' })).toBeVisible()
  430 |     await expect(page.locator('.desktop-data-table').getByText('Late arrival warning')).toBeVisible()
  431 |     await expect(page.getByRole('button', { name: 'Create record' })).toHaveCount(0)
  432 |     expect(policyRequests).toEqual([])
  433 | 
  434 |     const memberSearch = page.getByPlaceholder('Search for a member…')
  435 |     await expect(memberSearch).toHaveCount(1)
  436 |     await memberSearch.fill('M001')
  437 |     const memberResults = page.locator('.discipline-member-results')
  438 |     const aliceResult = memberResults.getByText('Alice Example', { exact: true })
  439 |     await expect(aliceResult).toHaveCount(1)
  440 |     await aliceResult.click()
  441 |     await expect(page.getByRole('heading', { name: 'Alice Example' })).toBeVisible()
  442 |     await expect(page.locator('.discipline-history-table').getByText('Late arrival warning')).toBeVisible()
  443 |     await captureRoleProof(page, 'discipline-president-read-only.png')
  444 |   })
  445 | 
  446 |   test('secretary general can review disciplinary records without mutation controls', async ({ page }) => {
  447 |     const { policyRequests } = await mockDisciplinaryWorkspace(page, makeSecretaryMeResponse())
  448 |     await page.goto('/censor')
  449 | 
  450 |     await expect(page).toHaveURL(/\/censor$/)
> 451 |     await expect(page.getByRole('heading', { name: 'Read-only oversight' })).toBeVisible()
      |                                                                              ^ Error: expect(locator).toBeVisible() failed
  452 |     await expect(page.locator('.desktop-data-table').getByText('Late arrival warning')).toBeVisible()
  453 |     await expect(page.getByRole('button', { name: 'Create record' })).toHaveCount(0)
  454 |     expect(policyRequests).toEqual([])
  455 |     await captureRoleProof(page, 'discipline-secretary-read-only.png')
  456 |   })
  457 | 
  458 |   test('censor cannot enter the treasurer finance workspace or load contribution data', async ({ page }) => {
  459 |     const { financeRequests } = await mockDisciplinaryWorkspace(page)
  460 | 
  461 |     await page.goto('/finance')
  462 | 
  463 |     await expect(page).toHaveURL(/\/dashboard$/)
  464 |     await expect(page.getByRole('heading', { name: 'Welcome back, Censor Demo' })).toBeVisible()
  465 |     expect(financeRequests).toEqual([])
  466 |   })
  467 | })
  468 | 
```