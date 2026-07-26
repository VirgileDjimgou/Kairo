# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: login.spec.ts >> Login flow >> mfa flow keeps multi-tenant users on the organization picker
- Location: e2e\login.spec.ts:146:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('heading', { name: 'Two-factor authentication' })
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByRole('heading', { name: 'Two-factor authentication' })

```

```yaml
- text:  Combis Sport Verein L’espace numérique du Combis Sport Verein Langue
- combobox "Langue":
  - option "Français" [selected]
  - option "English"
  - option "Deutsch"
- paragraph: Bienvenue
- heading "Votre association, simplement." [level=1]
- paragraph: Retrouvez vos informations, vos cotisations et les services utiles à votre rôle, dans un espace clair et sécurisé.
- article:
  - text: 
  - heading "Votre espace personnel" [level=2]
  - paragraph: Consultez vos données et vos cotisations en quelques secondes.
- article:
  - text: 
  - heading "Un espace pour chaque rôle" [level=2]
  - paragraph: Chaque responsable retrouve les outils utiles à sa mission.
- article:
  - text: 
  - heading "Des données protégées" [level=2]
  - paragraph: Les accès sont contrôlés pour chaque membre et chaque organisation.
- text: 
- heading "Accéder à votre espace" [level=2]
- paragraph: Utilisez les identifiants fournis par votre association.
- text: 
- heading "Authentification à deux facteurs" [level=3]
- paragraph: Saisissez le code de votre application d'authentification.
- text: Code d'authentification
- textbox "Code d'authentification":
  - /placeholder: "000000"
- button "Vérifier"
- button "Retour à la connexion"
```

# Test source

```ts
  94  |     await page.goto('/login')
  95  | 
  96  |     await expect(page.locator('#signin-card')).toBeVisible()
  97  |     await expect(page.getByTestId('commercial-hero-title')).toBeAttached()
  98  |     const hasHorizontalOverflow = await page.evaluate(
  99  |       () => document.documentElement.scrollWidth > window.innerWidth + 1,
  100 |     )
  101 |     expect(hasHorizontalOverflow).toBe(false)
  102 | 
  103 |     await page.getByTestId('commercial-hero-title').scrollIntoViewIfNeeded()
  104 |     await expect(page.getByTestId('commercial-hero-title')).toBeVisible()
  105 |   })
  106 | 
  107 |   test('login form shows validation on empty submit', async ({ page }) => {
  108 |     await page.goto('/login')
  109 |     await page.locator('button[type="submit"]').click()
  110 |     await expect(page.getByText('Email is required')).toBeVisible()
  111 |     await expect(page.locator('#email')).toHaveClass(/is-invalid/)
  112 |   })
  113 | 
  114 |   test('login with invalid credentials shows error', async ({ page }) => {
  115 |     await page.route('http://localhost:8000/api/v1/auth/login', async (route) => {
  116 |       await route.fulfill({
  117 |         status: 401,
  118 |         contentType: 'application/json',
  119 |         body: JSON.stringify({ detail: 'Invalid email or password' }),
  120 |       })
  121 |     })
  122 | 
  123 |     await page.goto('/login')
  124 |     await page.locator('input[type="email"]').fill('nonexistent@test.com')
  125 |     await page.locator('input[type="password"]').fill('wrongpassword')
  126 |     await page.locator('button[type="submit"]').click()
  127 |     await expect(page.locator('.alert-danger')).toBeVisible({ timeout: 10000 })
  128 |   })
  129 | 
  130 |   test('login shows a clear suspended-access message', async ({ page }) => {
  131 |     await page.route('http://localhost:8000/api/v1/auth/login', async (route) => {
  132 |       await route.fulfill({
  133 |         status: 403,
  134 |         contentType: 'application/json',
  135 |         body: JSON.stringify({ detail: 'You are not an active member of this organization' }),
  136 |       })
  137 |     })
  138 | 
  139 |     await page.goto('/login')
  140 |     await page.locator('input[type="email"]').fill('member@test.com')
  141 |     await page.locator('input[type="password"]').fill('StrongPass123!')
  142 |     await page.locator('button[type="submit"]').click()
  143 |     await expect(page.getByText('You do not currently have active access to an organization.')).toBeVisible()
  144 |   })
  145 | 
  146 |   test('mfa flow keeps multi-tenant users on the organization picker', async ({ page }) => {
  147 |     await page.route('http://localhost:8000/api/v1/auth/login', async (route) => {
  148 |       await route.fulfill({
  149 |         status: 200,
  150 |         contentType: 'application/json',
  151 |         body: JSON.stringify({
  152 |           mfa_required: true,
  153 |           mfa_token: 'mfa-token-123',
  154 |           expires_in: 300,
  155 |         }),
  156 |       })
  157 |     })
  158 | 
  159 |     await page.route('http://localhost:8000/api/v1/auth/mfa/complete', async (route) => {
  160 |       await route.fulfill({
  161 |         status: 200,
  162 |         contentType: 'application/json',
  163 |         body: JSON.stringify({
  164 |           access_token: 'access-token-123',
  165 |           token_type: 'bearer',
  166 |           expires_in: 1800,
  167 |           tenant_id: 'tenant-demo-1',
  168 |           user_id: 'user-1',
  169 |         }),
  170 |       })
  171 |     })
  172 | 
  173 |     await page.route('http://localhost:8000/api/v1/auth/me', async (route) => {
  174 |       await route.fulfill({
  175 |         status: 200,
  176 |         contentType: 'application/json',
  177 |         body: JSON.stringify({
  178 |           id: 'user-1',
  179 |           email: 'member@test.com',
  180 |           display_name: 'Member User',
  181 |           status: 'active',
  182 |           tenant_id: 'tenant-demo-1',
  183 |           roles: ['member'],
  184 |           last_login_at: null,
  185 |           memberships: makeMemberships(),
  186 |         }),
  187 |       })
  188 |     })
  189 | 
  190 |     await page.goto('/login')
  191 |     await page.locator('input[type="email"]').fill('member@test.com')
  192 |     await page.locator('input[type="password"]').fill('StrongPass123!')
  193 |     await page.locator('button[type="submit"]').click()
> 194 |     await expect(page.getByRole('heading', { name: 'Two-factor authentication' })).toBeVisible()
      |                                                                                    ^ Error: expect(locator).toBeVisible() failed
  195 | 
  196 |     await page.locator('#mfa-code').fill('123456')
  197 |     await page.getByRole('button', { name: 'Verify' }).click()
  198 | 
  199 |     await expect(page.getByRole('heading', { name: 'Choose organization' })).toBeVisible()
  200 |     await expect(page.getByRole('button', { name: /Demo Organization/ })).toBeVisible()
  201 |     await expect(page.getByRole('button', { name: /Ops Organization/ })).toBeVisible()
  202 |   })
  203 | 
  204 |   test('forgot password link is accessible', async ({ page }) => {
  205 |     await page.goto('/login')
  206 |     const forgotLink = page.locator('a[href*="forgot"], a:has-text("Forgot")')
  207 |     if (await forgotLink.isVisible()) {
  208 |       await forgotLink.click()
  209 |       await expect(page).toHaveURL(/forgot-password/)
  210 |     }
  211 |   })
  212 | })
  213 | 
  214 | test.describe('Unauthenticated access', () => {
  215 |   test('protected route redirects to login', async ({ page }) => {
  216 |     await page.goto('/dashboard')
  217 |     await expect(page).toHaveURL(/login/)
  218 |   })
  219 | 
  220 |   test('protected route preserves the requested redirect target', async ({ page }) => {
  221 |     await page.goto('/account/security')
  222 |     await expect(page).toHaveURL(/login\?redirect=\/account\/security/)
  223 |   })
  224 | 
  225 |   test('unknown route redirects to login', async ({ page }) => {
  226 |     await page.goto('/nonexistent-page')
  227 |     await expect(page).toHaveURL(/login/)
  228 |   })
  229 | })
  230 | 
```