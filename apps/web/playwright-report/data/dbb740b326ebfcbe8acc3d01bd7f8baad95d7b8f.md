# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: auditor-finance.spec.ts >> Auditor finance workspace >> mobile export controls use full-width rows without clipped labels
- Location: e2e\auditor-finance.spec.ts:261:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('button', { name: 'Export Excel' })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByRole('button', { name: 'Export Excel' })

```

```yaml
- main:
  - text: Finance audit Demo Organization
  - button "Toggle navigation": 
  - combobox:
    - option "Français"
    - option "English" [selected]
    - option "Deutsch"
  - button " Auditor Demo"
  - text: Finance audit
  - heading "Read-only finance oversight" [level=1]
  - paragraph: Review tenant-level contribution totals, member balances, and payment activity without any mutation controls.
  - combobox:
    - option "2025"
    - option "2026" [selected]
    - option "2027"
  - button "Refresh"
  - button "Export finance report"
  - text: Expected 210.00 EUR Paid 130.00 EUR Outstanding balance 80.00 EUR Payments logged 2 Member balances
  - heading "Tenant-wide contribution exposure" [level=2]
  - text: 2 members
  - table "Auditor member balances":
    - rowgroup:
      - row "Member Expected Paid Balance records":
        - columnheader "Member"
        - columnheader "Expected"
        - columnheader "Paid"
        - columnheader "Balance"
        - columnheader "records"
    - rowgroup:
      - row "Alice Example M001 120.00 40.00 80.00 1":
        - cell "Alice Example M001"
        - cell "120.00"
        - cell "40.00"
        - cell "80.00"
        - cell "1"
      - row "Bob Example M002 90.00 90.00 0.00 1":
        - cell "Bob Example M002"
        - cell "90.00"
        - cell "90.00"
        - cell "0.00"
        - cell "1"
  - text: Payment activity
  - heading "Recent recorded payments" [level=2]
  - text: 2 shown Alice Example (M001) 40.00 EUR · bank transfer 3/15/2026 INV-001 Bob Example (M002) 90.00 EUR · cash 3/20/2026 No reference
```

# Test source

```ts
  170 |       status: 200,
  171 |       contentType: 'application/json',
  172 |       body: JSON.stringify([]),
  173 |     })
  174 |   })
  175 | 
  176 |   await page.route('**/api/v1/events/public', async (route) => {
  177 |     await route.fulfill({
  178 |       status: 200,
  179 |       contentType: 'application/json',
  180 |       body: JSON.stringify([]),
  181 |     })
  182 |   })
  183 | 
  184 |   await page.route('**/api/v1/contributions/summary?**', async (route) => {
  185 |     await route.fulfill({
  186 |       status: 200,
  187 |       contentType: 'application/json',
  188 |       body: JSON.stringify({
  189 |         total_count: 2,
  190 |         total_expected: '210.00',
  191 |         total_paid: '130.00',
  192 |         total_balance: '80.00',
  193 |       }),
  194 |     })
  195 |   })
  196 | 
  197 |   await page.route('**/api/v1/contributions/payments', async (route) => {
  198 |     await route.fulfill({
  199 |       status: 200,
  200 |       contentType: 'application/json',
  201 |       body: JSON.stringify(payments),
  202 |     })
  203 |   })
  204 | 
  205 |   await page.route('**/api/v1/contributions/report/export', async (route) => {
  206 |     await route.fulfill({
  207 |       status: 200,
  208 |       contentType: 'text/csv',
  209 |       body: 'contribution_id,membership_profile_id,year\ncontrib-1,member-1,2026\n',
  210 |     })
  211 |   })
  212 | 
  213 |   await page.route('**/api/v1/contributions/?**', async (route) => {
  214 |     if (route.request().method() !== 'GET') {
  215 |       await route.fulfill({
  216 |         status: 403,
  217 |         contentType: 'application/json',
  218 |         body: JSON.stringify({ detail: 'Finance write capability required' }),
  219 |       })
  220 |       return
  221 |     }
  222 |     await route.fulfill({
  223 |       status: 200,
  224 |       contentType: 'application/json',
  225 |       body: JSON.stringify(contributions),
  226 |     })
  227 |   })
  228 | 
  229 |   return { financeRequests }
  230 | }
  231 | 
  232 | test.describe('Auditor finance workspace', () => {
  233 |   test('auditor sees read-only finance oversight without mutation controls', async ({ page }) => {
  234 |     await mockAuditorFinance(page)
  235 |     await page.goto('/finance-audit')
  236 | 
  237 |     await expect(page).toHaveURL(/\/finance-audit$/)
  238 |     await expect(page.getByTestId('auditor-finance-overview')).toBeVisible()
  239 |     await expect(page.getByRole('heading', { name: 'Read-only finance oversight' })).toBeVisible()
  240 |     await expect(page.getByText('210.00 EUR')).toBeVisible()
  241 |     await expect(page.getByRole('button', { name: 'Export finance report' })).toBeVisible()
  242 |     await expect(page.getByRole('button', { name: 'Export Excel' })).toBeVisible()
  243 |     await expect(page.getByRole('button', { name: 'Export PDF' })).toBeVisible()
  244 |     await expect(page.getByRole('button', { name: 'Copy for WhatsApp' })).toBeVisible()
  245 |     await expect(page.getByText('Alice Example (M001)')).toBeVisible()
  246 |     await expect(page.getByText('40.00 EUR · bank transfer')).toBeVisible()
  247 |     await expect(page.getByRole('button', { name: 'Record payment' })).toHaveCount(0)
  248 |     await expect(page.getByRole('button', { name: 'Create contribution' })).toHaveCount(0)
  249 |   })
  250 | 
  251 |   test('auditor cannot enter the treasurer finance workspace or load contribution data', async ({ page }) => {
  252 |     const { financeRequests } = await mockAuditorFinance(page)
  253 | 
  254 |     await page.goto('/finance')
  255 | 
  256 |     await expect(page).toHaveURL(/\/dashboard$/)
  257 |     await expect(page.getByRole('heading', { name: 'Welcome back, Auditor Demo' })).toBeVisible()
  258 |     expect(financeRequests).toEqual([])
  259 |   })
  260 | 
  261 |   test('mobile export controls use full-width rows without clipped labels', async ({ page }, testInfo) => {
  262 |     await page.setViewportSize({ width: 390, height: 844 })
  263 |     await mockAuditorFinance(page)
  264 |     await page.goto('/finance-audit')
  265 | 
  266 |     const exportExcel = page.getByRole('button', { name: 'Export Excel' })
  267 |     const exportPdf = page.getByRole('button', { name: 'Export PDF' })
  268 |     const shareWhatsapp = page.getByRole('button', { name: 'Copy for WhatsApp' })
  269 | 
> 270 |     await expect(exportExcel).toBeVisible()
      |                               ^ Error: expect(locator).toBeVisible() failed
  271 |     await expect(exportPdf).toBeVisible()
  272 |     await expect(shareWhatsapp).toBeVisible()
  273 |     await expect(exportExcel).toHaveCSS('white-space', 'normal')
  274 |     await expect(exportPdf).toHaveCSS('white-space', 'normal')
  275 |     await expect(shareWhatsapp).toHaveCSS('white-space', 'normal')
  276 | 
  277 |     const excelBox = await exportExcel.boundingBox()
  278 |     const pdfBox = await exportPdf.boundingBox()
  279 |     const whatsappBox = await shareWhatsapp.boundingBox()
  280 |     expect(excelBox?.width).toBeGreaterThan(240)
  281 |     expect(pdfBox?.width).toBeGreaterThan(240)
  282 |     expect(whatsappBox?.width).toBeGreaterThan(240)
  283 |     expect(pdfBox?.y).toBeGreaterThan(excelBox?.y ?? 0)
  284 |     expect(whatsappBox?.y).toBeGreaterThan(pdfBox?.y ?? 0)
  285 | 
  286 |     await page.screenshot({ path: testInfo.outputPath('auditor-finance-mobile.png'), fullPage: true })
  287 |   })
  288 | })
  289 | 
```