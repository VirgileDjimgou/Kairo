# Kairo Frontend — Architecture & Inventory

**Last updated:** 2026-07-24  
**Purpose:** Single-file reference for any AI agent to understand, compile, and extend the Kairo frontend.  
**Language:** TypeScript 5.7, Vue 3.5, Vite 6, Bootstrap 5.3, SCSS, Pinia 2.3, Vue Router 4

---

## 1. Stack & Entry Point

| Layer | Package | File |
|-------|---------|------|
| Entry HTML | — | `apps/web/index.html` |
| JS entry | — | `apps/web/src/main.ts` |
| Root component | Vue 3 | `apps/web/src/App.vue` |
| Router | vue-router 4 | `apps/web/src/router/index.ts` |
| State | pinia 2.3 | `apps/web/src/stores/auth.store.ts`, `locale.store.ts`, `tenant.store.ts`, `chat.store.ts` |
| HTTP | axios 1.7 | `apps/web/src/api/http.ts` (baseURL `/api/v1`, 30s timeout, Bearer auth interceptor) |
| i18n | Custom | `apps/web/src/i18n/messages.ts` (~1130 lines, 3 locales: fr/en/de) |
| Build | Vite 6 | `apps/web/vite.config.ts` (includes VitePWA plugin) |

### Startup sequence in `main.ts`:
1. `createApp(App)` → `use(createPinia())` → `use(router)` → mount `#app`
2. Imports: `bootstrap/dist/css/bootstrap.min.css`, `bootstrap-icons/font/bootstrap-icons.css`, `bootstrap/dist/js/bootstrap.bundle.min.js`
3. Import custom SCSS: `@/styles/main.scss`
4. App.vue `onMounted`: `localeStore.initialize()` → `authStore.restoreSession()`

---

## 2. File Inventory — Complete

### 2.1 Styles (`apps/web/src/styles/`)
| File | Role |
|------|------|
| `variables.scss` | All CSS custom properties (40+ tokens): colors, spacing, typography, radii, shadows, transitions, layout |
| `main.scss` | Entry point: imports all partials + Bootstrap overrides (buttons, cards, forms, focus, tables) |
| `_typography.scss` | Typographic scale (`.om-text-display` through `.om-text-caption`), heading reset, desktop scale-up at 768px |
| `_animations.scss` | Transitions (120/200/250ms), Vue transitions (fade, slide-up, slide-right), skeleton pulse, spinner, `prefers-reduced-motion` |
| `_safe-areas.scss` | `100dvh` fallback, `safe-area-inset-*` utility classes, fixed-bottom/top containers, content offset for bottom nav |
| `_mobile-utils.scss` | Touch targets 44px, tap highlight, text-size-adjust, scroll-behavior, responsive visibility, card-list pattern, responsive grid, bottom-sheet modal, data-card pattern |

### 2.2 Components (`apps/web/src/components/`)
| Path | Role |
|------|------|
| `LanguageSelector.vue` | Locale dropdown (fr/en/de) |
| `ConfirmModal.vue` | Reusable confirmation modal |
| `chat/ChatSidebar.vue` | Chat conversation list sidebar (280px desktop, fullscreen overlay mobile via `visible` prop) |
| `chat/ChatMessage.vue` | Single chat message bubble |
| `chat/FollowUpChips.vue` | Suggested follow-up prompt chips |
| `ui/MobileBottomNavigation.vue` | Bottom tab bar, 3-5 items, icon+label, active indicator, badge, safe-area bottom |
| `ui/PageHeader.vue` | Page title + optional kicker/subtitle/back button/action buttons, responsive |
| `ui/EmptyState.vue` | Icon + title + description + optional action button or RouterLink |
| `ui/StatusBadge.vue` | Inline badge: neutral/success/warning/danger/info, optional dot |
| `ui/AppButton.vue` | Fully typed button: primary/secondary/danger/ghost/outline, sm/md/lg, block, loading, icon, icon-only |
| `ui/ResponsiveDataView.vue` | Table on desktop (≥992px), card-list on mobile. Slots: thead, rows, card, empty-mobile, header, footer |
| `ui/SkeletonLoader.vue` | Configurable rows/columns skeleton pulse animation |

### 2.3 Composables (`apps/web/src/composables/`)
| File | Exports |
|------|---------|
| `useRoleNavigation.ts` | `appNavigation`, `adminNavigation`, `appHomeLabel`, `adminConsoleLabel`, role checks |
| `useTenantOnboarding.ts` | `checklist`, `progressPercent`, `summaryMetrics`, `nextStep`, `refresh` |
| `useAdminOverview.ts` | `modules`, `summaryMetrics`, `riskItems`, `quickActions`, `ingestionHealth`, `contributionSummary` |
| `useGovernanceCockpit.ts` | Governance overview composable |
| `useRecoveryState.ts` | Error recovery state pattern |
| `useCsvExport.ts` | CSV export utility |
| `useMobileDetect.ts` | `isMobile` (ref), `isDesktop()`, `breakpoint` (768px) — window resize listener with debounce |

### 2.4 Layouts (`apps/web/src/layouts/`)
| File | Breakpoint | Mobile Navigation |
|------|-----------|-------------------|
| `AppLayout.vue` | Sidebar at ≥768px (`d-none d-md-flex`) | Bottom navigation bar (MobileBottomNavigation) + hamburger offcanvas |
| `AdminLayout.vue` | Sidebar at ≥992px (`d-none d-lg-flex`) | Hamburger offcanvas only |
| `SecretaryLayout.vue` | Sidebar at ≥992px (`d-none d-lg-flex`) | Hamburger offcanvas (was missing before refactor) |

### 2.5 Views (`apps/web/src/views/`) — 35 files, 14 directories
| Directory | Files | Auth Required |
|-----------|-------|---------------|
| `auth/` | LoginView, ForgotPasswordView, ResetPasswordView, AcceptInviteView, MfaSetupView | Guest routes |
| `dashboard/` | DashboardView | Auth |
| `chat/` | ChatView | Auth |
| `members/` | MyProfileView, AdminMembersView | Auth |
| `account/` | AccountSecurityView | Auth |
| `events/` | EventsView, AdminEventsView | Auth |
| `announcements/` | AnnouncementsView, AdminAnnouncementsView | Auth |
| `policies/` | PoliciesView, AdminPoliciesView | Auth |
| `disciplinary/` | MyDisciplinaryView, AdminDisciplinaryView, CensorWorkspaceView | Auth |
| `finance/` | FinanceWorkspaceView, AuditorFinanceView | Auth |
| `governance/` | GovernanceCockpitView | Auth |
| `sports/` | SportsWorkspaceView | Auth |
| `secretary/` | SecretaryOverviewView | Auth |
| `admin/` | AdminOverviewView, AdminAccessView, AdminDocumentsView, AdminChatQueriesView, AuditTrailView, TenantOperationsView, AdminSettingsView, AdminOnboardingWizardView, AdminHealthCenterView, AdminNotificationsView | Auth |

### 2.6 API modules (`apps/web/src/api/`) — 15 files
`admin.api.ts`, `announcements.api.ts`, `audit.api.ts`, `auth.api.ts`, `chat.api.ts`, `contributions.api.ts`, `disciplinary.api.ts`, `documents.api.ts`, `events.api.ts`, `http.ts`, `membership.api.ts`, `notifications.api.ts`, `policies.api.ts`, `settings.api.ts`, `system.api.ts`

### 2.7 Stores (`apps/web/src/stores/`) — 4 Pinia stores
`auth.store.ts` (token, login/MFA, session restore), `locale.store.ts` (fr/en/de with localStorage + `t()` function), `tenant.store.ts` (memberships, tenant switching, module checks), `chat.store.ts` (conversations, messages, streaming)

### 2.8 Router (`apps/web/src/router/index.ts`)
- HTML5 history mode
- Route guard: `requiresAuth`, `requiresGuest`, `allowedRoles`, `requiresFinanceWorkspace`, `module`
- 30+ routes, catch-all redirects to `/dashboard`

---

## 3. Design Tokens Reference

```css
/* Colors — pick any of these in any component */
--om-primary           /* Dynamic per-tenant brand color */
--om-primary-hover
--om-neutral-0 through --om-neutral-900
--om-success / --om-warning / --om-danger / --om-info
--om-*-subtle          /* Each semantic has a subtle background variant */

/* Spacing — 4px baseline scale */
--om-space-xs (4px) through --om-space-3xl (64px)

/* Typography classes */
.om-text-display / .om-text-h1 / .om-text-h2 / .om-text-h3 / .om-text-h4
.om-text-body-lg / .om-text-body / .om-text-label / .om-text-caption
.om-text-strong / .om-text-muted / .om-text-accent / .om-text-mono

/* Layout */
--om-topbar-height: 56px
--om-bottomnav-height: 56px
--om-sidebar-width: 260px
--om-content-max-width: 1280px

/* Shapes */
--om-radius-sm (6px) / --om-radius-base (8px) / --om-radius-lg (12px) / --om-radius-xl (16px)

/* Shadows — minimal Swiss style */
--om-shadow-none / --om-shadow-card / --om-shadow-elevated / --om-shadow-overlay

/* Transitions */
--om-transition-fast (120ms) / --om-transition-base (200ms) / --om-transition-slow (250ms)
```

### Mobile utility classes
- `om-min-viewport-height` — replaces `min-vh-100` (uses 100dvh)
- `om-viewport-height` — replaces `vh-100`
- `om-safe-top/bottom/left/right` — safe-area padding
- `om-fixed-bottom-safe` — fixed bottom element with safe area
- `om-content-with-bottom-nav` — content padding for bottom nav
- `om-hide-mobile` / `om-show-mobile` — visibility at <768px
- `om-content-padding` — responsive padding (base/lg/xl)
- `om-content-constrain` — max-width 1280px + auto margins
- `om-card-list` / `om-card-list-item` — mobile card list pattern
- `om-responsive-grid` — 1 col mobile, 2 col ≥576px
- `om-responsive-form-row` — column mobile, row desktop
- `om-modal-bottom-sheet` — bottom sheet on mobile, modal on desktop
- `om-data-card` / `om-data-card-row` / `om-data-card-value` / `om-data-card-actions` — data row → card pattern
- `om-touch-target` — min 44×44px

---

## 4. i18n Coverage

| Category | Keys | Coverage |
|----------|------|----------|
| Login/Auth | 80+ | fr/en/de (all 4 auth views now localized) |
| Layouts/Navigation | 40+ | fr/en/de |
| Chat | 25+ | fr/en/de |
| Members | 30+ | fr/en/de |
| Contributions | 30+ | fr/en/de |
| Events | 12+ | fr/en/de |
| Policies | 15+ | fr/en/de |
| Disciplinary | 25+ | fr/en/de |
| Finance/Auditor | 40+ | fr/en/de |
| Censor | 20+ | fr/en/de |
| Common | 50+ | fr/en/de |
| **Total keys per locale** | **~380** | |

Translation function: `const t = (key: string) => localeStore.t(key)` (from `@/stores/locale.store`)

---

## 5. PWA Configuration

| File | Role |
|------|------|
| `vite.config.ts` | `VitePWA()` plugin: autoUpdate, manifest, workbox runtime caching |
| `public/favicon.svg` | SVG favicon |
| Generated in `dist/` | `sw.js`, `workbox-*.js`, `manifest.webmanifest`, `registerSW.js` |

### Manifest
- Name: "Kairo — Association Management"
- Short name: "Kairo"
- Theme: `#1a3f6b`, Background: `#f8f9fb`
- Display: standalone, Orientation: any
- Start URL: `/dashboard`

### Service Worker Strategy
- Precache: 90 entries (all JS, CSS, HTML, fonts, icons)
- API calls: `NetworkFirst`, 5 min cache, 10s network timeout
- `registerType: 'autoUpdate'` — updates automatically when new version detected

### Nginx PWA rules (in `nginx.conf`)
- `sw.js`: 24h cache, `Service-Worker-Allowed: /`
- `manifest.webmanifest`: 7d cache, MIME type `application/manifest+json`
- `registerSW.js`: 24h cache

---

## 6. Route Tree (Complete)

```
/login                          → auth/LoginView.vue              [guest]
/forgot-password                → auth/ForgotPasswordView.vue      [guest]
/reset-password                 → auth/ResetPasswordView.vue       [guest]
/accept-invite                  → auth/AcceptInviteView.vue        [guest]
/mfa/setup                      → redirect /account/security       [auth]

/  [AppLayout.vue]
  /dashboard                    → dashboard/DashboardView.vue
  /chat                         → chat/ChatView.vue
  /members/profile              → members/MyProfileView.vue
  /account/security             → account/AccountSecurityView.vue
  /policies                     → policies/PoliciesView.vue
  /disciplinary                 → disciplinary/MyDisciplinaryView.vue
  /censor                       → disciplinary/CensorWorkspaceView.vue
  /sports                       → sports/SportsWorkspaceView.vue
  /governance                   → governance/GovernanceCockpitView.vue
  /events                       → events/EventsView.vue
  /announcements                → announcements/AnnouncementsView.vue
  /finance                      → finance/FinanceWorkspaceView.vue
  /finance-audit                → finance/AuditorFinanceView.vue
  /secretary  [SecretaryLayout.vue]
    /secretary                  → secretary/SecretaryOverviewView.vue
    /secretary/documents        → admin/AdminDocumentsView.vue
    /secretary/policies         → policies/AdminPoliciesView.vue
    /secretary/announcements    → announcements/AdminAnnouncementsView.vue

/admin  [AdminLayout.vue]
  /admin                        → admin/AdminOverviewView.vue
  /admin/access                 → admin/AdminAccessView.vue
  /admin/documents              → admin/AdminDocumentsView.vue
  /admin/chat-queries           → admin/AdminChatQueriesView.vue
  /admin/audit                  → admin/AuditTrailView.vue
  /admin/tenants                → admin/TenantOperationsView.vue
  /admin/members                → members/AdminMembersView.vue
  /admin/contributions          → contributions/AdminContributionsView.vue
  /admin/policies               → policies/AdminPoliciesView.vue
  /admin/disciplinary           → disciplinary/AdminDisciplinaryView.vue
  /admin/events                 → events/AdminEventsView.vue
  /admin/announcements          → announcements/AdminAnnouncementsView.vue
  /admin/notifications          → admin/AdminNotificationsView.vue
  /admin/settings               → admin/AdminSettingsView.vue
  /admin/onboarding             → admin/AdminOnboardingWizardView.vue
  /admin/health                 → admin/AdminHealthCenterView.vue

/* (catch-all)                   → redirect /dashboard
```

---

## 7. Deployment

### Docker (local dev)
```bash
docker compose up -d --build       # starts all services + web dev server on :5173
```

### Docker (production)
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### With Caddy reverse proxy (TLS optional)
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  -f infra/reverse-proxy/docker-compose.caddy.yml up -d --build
```

### With Cloudflare Tunnel
```bash
# Set CLOUDFLARE_TUNNEL_TOKEN in .env
docker compose --profile tunnel up -d
```

### Production smoke check
```bash
bash scripts/production_smoke.sh [URL]
# Checks: /health (200), /metrics (200), / (200), /docs (404), /redoc (404), /openapi.json (404)
```

### Release deployment
```bash
bash scripts/deploy_release.sh install   # fresh install
bash scripts/deploy_release.sh upgrade   # upgrade with backup
```

---

## 8. Changes Made in Mobile-First Refactor (2026-07-24)

### New files created (18)
```
docs/UI_MOBILE_AUDIT.md
docs/DESIGN_SYSTEM.md
docs/RESPONSIVE_TEST_REPORT.md
apps/web/src/styles/_typography.scss
apps/web/src/styles/_animations.scss
apps/web/src/styles/_safe-areas.scss
apps/web/src/styles/_mobile-utils.scss
apps/web/src/composables/useMobileDetect.ts
apps/web/src/components/ui/MobileBottomNavigation.vue
apps/web/src/components/ui/PageHeader.vue
apps/web/src/components/ui/EmptyState.vue
apps/web/src/components/ui/StatusBadge.vue
apps/web/src/components/ui/AppButton.vue
apps/web/src/components/ui/ResponsiveDataView.vue
apps/web/src/components/ui/SkeletonLoader.vue
apps/web/public/favicon.svg
apps/web/e2e/responsive-mobile.spec.ts
```

### Existing files modified (17)
```
apps/web/index.html                    — PWA meta tags, viewport-fit
apps/web/vite.config.ts                — VitePWA plugin
apps/web/package.json                  — vite-plugin-pwa dependency
apps/web/package-lock.json
apps/web/nginx.conf                    — PWA cache rules
apps/web/src/styles/variables.scss     — 40+ design tokens
apps/web/src/styles/main.scss          — Reorganized, Bootstrap overrides, touch targets
apps/web/src/i18n/messages.ts          — 52 new keys (auth, layout)
apps/web/src/layouts/AppLayout.vue     — Bottom nav, 100dvh, safe areas
apps/web/src/layouts/AdminLayout.vue   — 100dvh
apps/web/src/layouts/SecretaryLayout.vue — Offcanvas added, 100dvh, i18n nav
apps/web/src/views/chat/ChatView.vue   — Mobile split view, resize listener
apps/web/src/components/chat/ChatSidebar.vue — visible prop
apps/web/src/views/dashboard/DashboardView.vue — Breakpoint improvements
apps/web/src/views/auth/ForgotPasswordView.vue — i18n complete
apps/web/src/views/auth/ResetPasswordView.vue — i18n complete
apps/web/src/views/auth/AcceptInviteView.vue — i18n complete
apps/web/src/views/auth/MfaSetupView.vue — i18n complete
infra/reverse-proxy/Caddyfile          — PWA headers
```

### Key architectural decisions
1. **Bottom nav on mobile** — AppLayout uses `MobileBottomNavigation` at <768px. Items are the first 5 from `appNavigation` (computed from `useRoleNavigation`). "Plus" item opens the existing offcanvas drawer via Bootstrap JS API.
2. **SecretaryLayout mobile** — Now has `#secretaryMobileSidebar` offcanvas with hamburger toggle (was completely missing before, sidebar was just `d-none d-lg-flex` with no fallback).
3. **Chat mobile split** — On <768px, ChatSidebar and ChatMain are mutually exclusive views. Selecting a conversation hides the sidebar. A back button in the chat header returns to the conversation list. On ≥768px, both are visible side by side.
4. **100vh → 100dvh** — All layouts and views now use `100dvh` with `100vh` fallback. The `.om-min-viewport-height` class is the canonical way to do this.
5. **Bootstrap preserved** — The refactor builds on top of Bootstrap 5, not replacing it. Custom CSS augments Bootstrap. No new CSS framework added.
6. **Zero new runtime dependencies** except `vite-plugin-pwa` (build-time only).

### Build verification
```
npm run type-check   → 0 errors
npm run build        → 285 modules, 2.25s, PWA: 90 precache entries
```

---

## 9. Remaining Known Issues

| Priority | Issue | Location |
|----------|-------|----------|
| HIGH | AdminAccess, AuditTrail, AdminChatQueries, TenantOperations, MyDisciplinary, SecretaryLayout nav labels partially hardcoded English | Multiple views |
| MEDIUM | 15 views use `table-responsive` (horizontal scroll); would benefit from `ResponsiveDataView` card pattern | Admin table views |
| MEDIUM | `inline copy` computed pattern in 17 views — functional but duplicates i18n strings outside messages.ts | Multiple views |
| LOW | LoginView hero orbs could be simplified for mobile | `LoginView.vue` |
| LOW | No PWA icons (192/512px PNG) — need real assets for production | `public/` — currently using placeholder config |
