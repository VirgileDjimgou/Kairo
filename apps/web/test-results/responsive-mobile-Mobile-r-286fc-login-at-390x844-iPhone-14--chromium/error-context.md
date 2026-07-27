# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: responsive-mobile.spec.ts >> Mobile responsive — Login >> login at 390x844 (iPhone 14)
- Location: e2e\responsive-mobile.spec.ts:125:5

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator:  locator('input[type="email"]').last()
Expected: visible
Received: hidden
Timeout:  5000ms

Call log:
  - Expect "toBeVisible" with timeout 5000ms
  - waiting for locator('input[type="email"]').last()
    14 × locator resolved to <input id="email" required="" type="email" data-v-409777eb="" class="form-control" autocomplete="email" placeholder="vous@organisation.org"/>
       - unexpected value "hidden"

```

```yaml
- banner:
  - text: 
  - strong: Kairo
  - text: Votre espace numérique
  - combobox "Langue":
    - option "FR" [selected]
    - option "EN"
    - option "DE"
- main:
  - text: 
  - heading "Accéder à votre espace" [level=2]
  - paragraph: Utilisez les identifiants fournis par votre association.
  - text: Adresse e-mail
  - textbox "Adresse e-mail Adresse e-mail":
    - /placeholder: vous@organisation.org
  - text: Mot de passe
  - textbox "Mot de passe Mot de passe":
    - /placeholder: ••••••••
  - link "Mot de passe oublié ?":
    - /url: /forgot-password
  - button "Se connecter"
  - paragraph:  Identifiants de développement
  - code: admin@demo.org / Admin123!
  - button "Remplir les identifiants démo"
- contentinfo: Kairo Votre association, simplement.
```

# Test source

```ts
  32  |       locale: "fr",
  33  |     },
  34  |     memberships: [
  35  |       {
  36  |         tenant_id: "tenant-demo-1",
  37  |         slug: "demo",
  38  |         name: "Combis Sport Verein",
  39  |         roles: ["member"],
  40  |         branding: { primary_color: "#1a3f6b", logo_url: "" },
  41  |         modules: {
  42  |           membership: true,
  43  |           contributions: true,
  44  |           policies: true,
  45  |           disciplinary: true,
  46  |           events: true,
  47  |           announcements: true,
  48  |           chat: true,
  49  |           notifications: true,
  50  |         },
  51  |         profile_type: "member",
  52  |       },
  53  |     ],
  54  |     requires_mfa: false,
  55  |   };
  56  | }
  57  | 
  58  | function makeRoleAuth(role: string) {
  59  |   const auth = makeMemberAuth();
  60  |   auth.user.roles = [role];
  61  |   auth.user.email = `${role}@demo.org`;
  62  |   auth.user.display_name = role.replace("_", " ");
  63  |   auth.memberships[0].roles = [role];
  64  |   auth.memberships[0].profile_type = role === "member" ? "member" : "staff";
  65  |   return auth;
  66  | }
  67  | 
  68  | async function assertNoHorizontalOverflow(page: any) {
  69  |   const dimensions = await page.evaluate(() => ({
  70  |     scrollWidth: document.documentElement.scrollWidth,
  71  |     clientWidth: document.documentElement.clientWidth,
  72  |   }));
  73  |   expect(dimensions.scrollWidth).toBeLessThanOrEqual(
  74  |     dimensions.clientWidth + 1,
  75  |   );
  76  | }
  77  | 
  78  | async function setupAuth(page: any, auth = makeMemberAuth()) {
  79  |   const profile = {
  80  |     ...auth.user,
  81  |     tenant_id: auth.memberships[0].tenant_id,
  82  |     preferred_language: auth.user.locale,
  83  |     status: "active",
  84  |     last_login_at: null,
  85  |     memberships: auth.memberships,
  86  |   };
  87  | 
  88  |   await page.route("**/api/v1/auth/me", (route: any) => {
  89  |     route.fulfill({
  90  |       status: 200,
  91  |       contentType: "application/json",
  92  |       body: JSON.stringify(profile),
  93  |     });
  94  |   });
  95  |   await page.addInitScript((auth: any) => {
  96  |     localStorage.setItem("access_token", auth.access_token);
  97  |     localStorage.setItem("tenant_id", auth.memberships[0].tenant_id);
  98  |   }, auth);
  99  | }
  100 | 
  101 | async function mockDashboardApi(page: any) {
  102 |   await page.route("**/api/v1/dashboard/**", (route: any) => {
  103 |     route.fulfill({
  104 |       status: 200,
  105 |       contentType: "application/json",
  106 |       body: JSON.stringify({ modules: {}, checklist: [], metrics: {} }),
  107 |     });
  108 |   });
  109 |   await page.route("**/api/v1/chat/**", (route: any) => {
  110 |     route.fulfill({
  111 |       status: 200,
  112 |       contentType: "application/json",
  113 |       body: JSON.stringify({ conversations: [] }),
  114 |     });
  115 |   });
  116 | }
  117 | 
  118 | async function openAuthenticatedPage(page: any, path: string) {
  119 |   await page.goto(path, { waitUntil: "domcontentloaded" });
  120 |   await expect(page.locator(".app-shell")).toBeVisible();
  121 | }
  122 | 
  123 | test.describe("Mobile responsive — Login", () => {
  124 |   for (const vp of MOBILE_VIEWPORTS) {
  125 |     test(`login at ${vp.width}x${vp.height} (${vp.label})`, async ({
  126 |       page,
  127 |     }) => {
  128 |       await page.setViewportSize({ width: vp.width, height: vp.height });
  129 |       await page.goto("/login");
  130 | 
  131 |       await expect(page.locator("#signin-card")).toBeAttached();
> 132 |       await expect(page.locator('input[type="email"]').last()).toBeVisible();
      |                                                                ^ Error: expect(locator).toBeVisible() failed
  133 |       await expect(page.locator('input[type="password"]').last()).toBeVisible();
  134 |       await expect(page.locator('button[type="submit"]').last()).toBeVisible();
  135 | 
  136 |       await assertNoHorizontalOverflow(page);
  137 | 
  138 |       // Verify the form is above the hero on mobile (order swap)
  139 |       const formCard = page.locator("#signin-card").last();
  140 |       const formRect = await formCard.boundingBox();
  141 |       const heroTitle = page.getByTestId("commercial-hero-title");
  142 |       if (await heroTitle.isVisible()) {
  143 |         const heroRect = await heroTitle.boundingBox();
  144 |         // Form should be above hero on mobile
  145 |         if (formRect && heroRect) {
  146 |           expect(formRect.y + formRect.height).toBeLessThanOrEqual(
  147 |             heroRect.y + heroRect.height,
  148 |           );
  149 |         }
  150 |       }
  151 |     });
  152 |   }
  153 | });
  154 | 
  155 | test.describe("Mobile responsive — Auth recovery views", () => {
  156 |   const recoveryRoutes = [
  157 |     { path: "/forgot-password", keyElement: 'input[type="email"]' },
  158 |     {
  159 |       path: "/reset-password?token=responsive-test-token",
  160 |       keyElement: 'input[type="password"]',
  161 |     },
  162 |     {
  163 |       path: "/accept-invite?token=responsive-test-token",
  164 |       keyElement: 'input[type="text"]',
  165 |     },
  166 |   ];
  167 | 
  168 |   for (const vp of MOBILE_VIEWPORTS.slice(0, 2)) {
  169 |     for (const route of recoveryRoutes) {
  170 |       test(`${route.path} at ${vp.width}x${vp.height}`, async ({ page }) => {
  171 |         await page.setViewportSize({ width: vp.width, height: vp.height });
  172 |         await page.goto(route.path);
  173 | 
  174 |         await expect(page.locator(route.keyElement).first()).toBeVisible();
  175 |         await assertNoHorizontalOverflow(page);
  176 |       });
  177 |     }
  178 |   }
  179 | });
  180 | 
  181 | test.describe("Mobile responsive — Dashboard", () => {
  182 |   for (const vp of MOBILE_VIEWPORTS) {
  183 |     test(`dashboard at ${vp.width}x${vp.height} (${vp.label})`, async ({
  184 |       page,
  185 |     }) => {
  186 |       await page.setViewportSize({ width: vp.width, height: vp.height });
  187 |       await setupAuth(page);
  188 | 
  189 |       await mockDashboardApi(page);
  190 |       await openAuthenticatedPage(page, "/dashboard");
  191 | 
  192 |       await assertNoHorizontalOverflow(page);
  193 | 
  194 |       // Bottom navigation should be visible on mobile
  195 |       if (vp.width < 768) {
  196 |         const bottomNav = page.locator(".bottom-nav");
  197 |         await expect(bottomNav).toBeVisible();
  198 |       }
  199 |     });
  200 |   }
  201 | });
  202 | 
  203 | test.describe("Mobile responsive — Chat", () => {
  204 |   const mobileVps = MOBILE_VIEWPORTS.slice(0, 3);
  205 | 
  206 |   for (const vp of mobileVps) {
  207 |     test(`chat at ${vp.width}x${vp.height}`, async ({ page }) => {
  208 |       await page.setViewportSize({ width: vp.width, height: vp.height });
  209 |       await setupAuth(page);
  210 | 
  211 |       await page.route("**/api/v1/chat/**", (route: any) => {
  212 |         route.fulfill({
  213 |           status: 200,
  214 |           contentType: "application/json",
  215 |           body: JSON.stringify({
  216 |             conversations: [
  217 |               {
  218 |                 id: "conv-1",
  219 |                 title: "Test conversation",
  220 |                 message_count: 3,
  221 |                 last_message_preview: "Hello",
  222 |               },
  223 |             ],
  224 |             allowed_domains: ["governance", "member_finance"],
  225 |           }),
  226 |         });
  227 |       });
  228 | 
  229 |       await openAuthenticatedPage(page, "/chat");
  230 | 
  231 |       await assertNoHorizontalOverflow(page);
  232 | 
```