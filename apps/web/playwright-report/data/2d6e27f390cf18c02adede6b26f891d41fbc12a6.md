# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: login.spec.ts >> Login flow >> login form shows validation on empty submit
- Location: e2e\login.spec.ts:107:3

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText('Email is required')
Expected: visible
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for getByText('Email is required')

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
- text: Adresse e-mail
- textbox "Adresse e-mail":
  - /placeholder: vous@organisation.org
- text: L'adresse e-mail est obligatoire Mot de passe
- textbox "Mot de passe":
  - /placeholder: ••••••••
- link "Mot de passe oublié ?":
  - /url: /forgot-password
- button "Se connecter"
- paragraph:  Identifiants de développement
- code: admin@demo.org
- code: Admin123!
- code: alice@demo.org
- code: Member123!
- button "Remplir les identifiants démo"
```

# Test source

```ts
  10  |       branding: {
  11  |         primary_color: '#1f4f8f',
  12  |         logo_url: '',
  13  |       },
  14  |       modules: {
  15  |         membership: true,
  16  |         contributions: true,
  17  |         policies: true,
  18  |         disciplinary: true,
  19  |         events: true,
  20  |         announcements: true,
  21  |         chat: true,
  22  |         notifications: true,
  23  |       },
  24  |       profile_type: 'member',
  25  |     },
  26  |     {
  27  |       tenant_id: 'tenant-ops-2',
  28  |       slug: 'ops',
  29  |       name: 'Ops Organization',
  30  |       roles: ['member'],
  31  |       branding: {
  32  |         primary_color: '#1f4f8f',
  33  |         logo_url: '',
  34  |       },
  35  |       modules: {
  36  |         membership: true,
  37  |         contributions: true,
  38  |         policies: true,
  39  |         disciplinary: true,
  40  |         events: true,
  41  |         announcements: true,
  42  |         chat: true,
  43  |         notifications: true,
  44  |       },
  45  |       profile_type: 'member',
  46  |     },
  47  |   ]
  48  | }
  49  | 
  50  | test.describe('Login flow', () => {
  51  |   test('login page renders correctly', async ({ page }) => {
  52  |     await page.goto('/login')
  53  |     await expect(page.getByTestId('commercial-hero-title')).toBeVisible()
  54  |     await expect(page.getByTestId('commercial-hero')).toContainText('Votre association, simplement.')
  55  |     await expect(page.locator('input[type="email"]')).toBeVisible()
  56  |     await expect(page.locator('input[type="password"]')).toBeVisible()
  57  |     await expect(page.locator('button[type="submit"]')).toBeVisible()
  58  |     await expect(page.locator('#signin-card')).toBeVisible()
  59  |     await expect(page.locator('#highlights .feature-card')).toHaveCount(3)
  60  |   })
  61  | 
  62  |   test('desktop login screen fits within the available viewport', async ({ page }) => {
  63  |     await page.setViewportSize({ width: 1440, height: 900 })
  64  |     await page.goto('/login')
  65  | 
  66  |     await expect(page.locator('#signin-card')).toBeVisible()
  67  |     for (const locale of ['fr', 'en', 'de']) {
  68  |       await page.locator('.language-select').selectOption(locale)
  69  |       const viewportFit = await page.evaluate(() => {
  70  |         const selectors = ['[data-testid="commercial-hero-title"]', '#highlights', '#signin-card']
  71  |         const allVisible = selectors.every((selector) => {
  72  |           const element = document.querySelector(selector)
  73  |           if (!element) return false
  74  |           const rect = element.getBoundingClientRect()
  75  |           return rect.top >= 0 && rect.bottom <= window.innerHeight
  76  |         })
  77  |         return {
  78  |           allVisible,
  79  |           noVerticalOverflow: document.documentElement.scrollHeight <= window.innerHeight + 1,
  80  |           noHorizontalOverflow: document.documentElement.scrollWidth <= window.innerWidth + 1,
  81  |         }
  82  |       })
  83  | 
  84  |       expect(viewportFit).toEqual({
  85  |         allVisible: true,
  86  |         noVerticalOverflow: true,
  87  |         noHorizontalOverflow: true,
  88  |       })
  89  |     }
  90  |   })
  91  | 
  92  |   test('mobile login keeps the form and presentation accessible without horizontal overflow', async ({ page }) => {
  93  |     await page.setViewportSize({ width: 390, height: 844 })
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
> 110 |     await expect(page.getByText('Email is required')).toBeVisible()
      |                                                       ^ Error: expect(locator).toBeVisible() failed
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
  194 |     await expect(page.getByRole('heading', { name: 'Two-factor authentication' })).toBeVisible()
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
```