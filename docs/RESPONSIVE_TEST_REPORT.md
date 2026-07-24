# Kairo — Rapport de refonte Mobile-First

**Date :** 2026-07-24  
**Build :** OK (TypeScript + Vite, 285 modules, 94 entrées PWA)
**Tests E2E responsive :** OK (25/25 sur 5 viewports)

---

## 1. Résumé exécutif

La refonte mobile-first de l'interface Kairo a transformé l'application d'un design desktop-centrique vers une expérience véritablement responsive, inspirée du Style suisse international. Les changements majeurs incluent :

- **Navigation mobile** : Barre de navigation inférieure (bottom tab bar) pour les membres, offcanvas pour les layouts admin/secrétaire
- **Design system** : Palette neutre raffinée, typographie système, grille 4/6/12 colonnes, espacement basé sur 4px
- **Chat** : Refonte complète — liste des conversations / chat en vues séparées sur mobile
- **Safe areas** : Gestion iOS/Android des notch, barres systèmes, et `100dvh`
- **7 composants UI** réutilisables créés, 3 layouts refondus

---

## 2. Modifications réalisées

### 2.1 Design System (fichiers créés/modifiés)

| Fichier | Action |
|---------|--------|
| `src/styles/variables.scss` | Refonte — tokens CSS complets (neutres, sémantiques, espacement, typo, ombres) |
| `src/styles/_typography.scss` | Création — échelle typographique mobile/desktop, classes `.om-text-*` |
| `src/styles/_animations.scss` | Création — transitions 120/200/250ms, `prefers-reduced-motion` |
| `src/styles/_safe-areas.scss` | Création — safe-area padding, `dvh` fallback, bottom/top nav containers |
| `src/styles/_mobile-utils.scss` | Création — touch targets 44px, card-list pattern, responsive grid, modal sheet |
| `src/styles/main.scss` | Refonte — imports réorganisés, Bootstrap overrides unifiés |

### 2.2 Composants UI (créés)

| Composant | Fichier |
|-----------|---------|
| `MobileBottomNavigation` | `src/components/ui/MobileBottomNavigation.vue` |
| `PageHeader` | `src/components/ui/PageHeader.vue` |
| `EmptyState` | `src/components/ui/EmptyState.vue` |
| `StatusBadge` | `src/components/ui/StatusBadge.vue` |
| `AppButton` | `src/components/ui/AppButton.vue` |
| `ResponsiveDataView` | `src/components/ui/ResponsiveDataView.vue` |
| `SkeletonLoader` | `src/components/ui/SkeletonLoader.vue` |

### 2.3 Composables (créés)

| Composable | Fichier |
|-----------|---------|
| `useMobileDetect` | `src/composables/useMobileDetect.ts` |

### 2.4 Layouts (refondus)

| Layout | Changements |
|--------|------------|
| `AppLayout` | Bottom navigation mobile, `100dvh`, safe areas, tenant switcher masqué sur mobile étroit |
| `AdminLayout` | `100dvh`, sidebar-link styles migrés vers global |
| `SecretaryLayout` | Offcanvas mobile ajouté (était absent), `100dvh`, lien "back to portal" dans header |

### 2.5 Vues modifiées

| Vue | Changements |
|-----|------------|
| `ChatView.vue` | Refonte mobile : sidebar/conversation en vues séparées, back button, `100dvh`, resize listener |
| `ChatSidebar.vue` | Prop `visible` pour toggle mobile |
| `DashboardView.vue` | `col-xl` → `col-lg`, padding responsive, meilleur wrapping |
| `ForgotPasswordView.vue` | `min-vh-100` → `om-min-viewport-height` + safe bottom |
| `ResetPasswordView.vue` | Idem |
| `AcceptInviteView.vue` | Idem |
| `index.html` | Meta viewport-fit, theme-color, apple-mobile-web-app, format-detection |

---

## 3. Expérience mobile

### Navigation
- **Membres/tous rôles (AppLayout)** : Bottom navigation bar 5 onglets (Dashboard + 3-4 workspaces + Plus) visible sur écran <768px. Sur desktop, sidebar 260px.
- **Admins (AdminLayout)** : Offcanvas hamburger conservé.
- **Secrétaires (SecretaryLayout)** : Offcanvas hamburger ajouté (absent auparavant).
- **Chat** : Sur mobile, la liste des conversations et le chat actif sont des vues séparées (une seule visible à la fois).

### Safe areas
- `env(safe-area-inset-*)` utilisé partout
- `100dvh` avec fallback `100vh`
- `viewport-fit=cover` dans le meta viewport
- Bottom nav respecte la barre de navigation système

### Touch
- `touch-action: manipulation` global
- `-webkit-tap-highlight-color: transparent` global
- `overscroll-behavior: none` sur body
- `-webkit-text-size-adjust: 100%`
- Cibles tactiles minimum 44px (composants AppButton, MobileBottomNavigation)

---

## 4. Responsive

### Breakpoints testés (design system)

| Nom | Min-width | Appareils |
|-----|-----------|-----------|
| xs | 320px | Galaxy Fold, iPhone SE |
| sm | 375px | iPhone 6/7/8/SE |
| md | 414px | iPhone 11, Pixel 5 |
| lg | 768px | iPad Mini portrait |
| xl | 1024px | iPad paysage |
| 2xl | 1280px | Desktop |

### Comportements
- **320-767px** : Single column, bottom nav, cartes empilées, formulaires single column
- **768-1023px** : Sidebar apparait, bottom nav disparait, grille 2 colonnes
- **1024px+** : Sidebar + contenu, grille 12 colonnes, largeur max 1280px

---

## 5. Accessibilité

| Critère | État |
|---------|------|
| Cibles tactiles ≥44px | Composants UI oui, vues legacy partiel |
| Focus visible | Oui (`:focus-visible` avec outline 2px) |
| Contrastes | Améliorés (palette neutre raffinée) |
| `prefers-reduced-motion` | Respecté (animations désactivées) |
| ARIA labels | Ajoutés sur MobileBottomNavigation, AppButton |
| `aria-current="page"` | Sur l'onglet actif de la bottom nav |

---

## 6. Performance

| Métrique | Avant | Après |
|----------|-------|-------|
| CSS bundle (global) | 313 KB | 323 KB (+10 KB, nouveau design system) |
| JS bundle (global) | 290.79 KB | 290.81 KB (+0.02 KB) |
| Build time | 2.00s | 2.05s |
| Nouveaux composants | — | 7 composants (lazy-loadés via routes) |
| Polices | Bootstrap Icons (180 KB woff) | Inchangé (pas de nouvelle police chargée) |

---

## 7. Fichiers modifiés/créés

### Créés (12)
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
```

### Modifiés (13)
```
apps/web/src/styles/variables.scss
apps/web/src/styles/main.scss
apps/web/src/layouts/AppLayout.vue
apps/web/src/layouts/AdminLayout.vue
apps/web/src/layouts/SecretaryLayout.vue
apps/web/src/views/chat/ChatView.vue
apps/web/src/components/chat/ChatSidebar.vue
apps/web/src/views/dashboard/DashboardView.vue
apps/web/src/views/auth/ForgotPasswordView.vue
apps/web/src/views/auth/ResetPasswordView.vue
apps/web/src/views/auth/AcceptInviteView.vue
apps/web/index.html
```

---

## 8. Travaux restants

### Priorité haute
1. **i18n des vues auth** : ForgotPassword, ResetPassword, AcceptInvite, MfaSetup — entièrement en anglais hardcodé. Critique pour l'expérience mobile.
2. **i18n des vues admin** : AdminAccess, AuditTrail, AdminChatQueries, TenantOperations, MyDisciplinary — partiellement non localisées.
3. **Cibles tactiles dans les tableaux** : Les boutons `.btn-sm` icône-seule dans les tableaux admin (31px) doivent passer à 44px minimum.

### Priorité moyenne
4. **Transformation tableaux → cartes** : Les 15 vues utilisant `table-responsive` gagneraient à utiliser `ResponsiveDataView` pour une expérience carte sur mobile.
5. **i18n résiduelle** : le contrôle automatisé signale encore 116 chaînes potentielles dans 12 fichiers historiques. Elles doivent être qualifiées puis migrées progressivement vers les clés trilingues.

### Priorité basse
6. **Pattern `copy` computed** : Migrer progressivement vers `localeStore.t()` pour réduire la duplication.

---

## 9. Validation PWA et production

La PWA est intégrée et déployée sur `https://app.combissportverein.org`.

| Contrôle | Résultat |
|----------|----------|
| Manifest web | `200 application/manifest+json` |
| Service worker | `200 application/javascript` |
| Icône 192x192 | `200 image/png` |
| Icône 512x512 | `200 image/png` |
| Audit npm | 0 vulnérabilité |
| Smoke test public | 6/6 |
| Services Docker | 9/9 actifs, services applicatifs sains |

Le déploiement a recréé uniquement le service `web`. PostgreSQL, les volumes, l'API, le worker et le tunnel Cloudflare n'ont pas été remplacés.

---

## 10. Commandes exécutées

```bash
npm run type-check
npm run build
npx playwright test e2e/responsive-mobile.spec.ts
npm audit
node scripts/check-i18n-coverage.mjs
```

- TypeScript : OK, 0 erreur.
- Build : OK, 285 modules et 94 entrées PWA précachées.
- Playwright responsive : OK, 25/25 tests.
- Audit npm : OK, 0 vulnérabilité.
- i18n : 116 chaînes potentielles dans 12 fichiers, suivi requis.

---

## 11. Avant / Après — Synthèse

| Aspect | Avant | Après |
|--------|-------|-------|
| Navigation mobile | Offcanvas hamburger seulement | Bottom tab bar + offcanvas |
| SecretaryLayout | Aucune navigation mobile | Offcanvas hamburger |
| Chat mobile | Sidebar 280px + chat côte à côte | Vues séparées (liste OU chat) |
| Viewport height | `100vh` (cassé sur mobile) | `100dvh` avec fallback |
| Safe areas | Aucune | `safe-area-inset-*` partout |
| Palette | 6 variables CSS | 40+ tokens design |
| Typographie | Bootstrap par défaut | Échelle complète mobile/desktop |
| Composants UI | 4 (ConfirmModal, chat seulement) | 11 (7 nouveaux) |
| Touch targets | 31px (boutons tableaux) | 44px (nouveaux composants) |
| Meta mobile | Viewport basic | theme-color, apple-mobile, viewport-fit |
| Design identity | Bootstrap standard | Style suisse raffiné |

---

## 12. Mobile-native shell follow-up (2026-07-24)

The first responsive pass made the screens fit mobile viewports. This follow-up changes the application shell so that phone use is the primary experience rather than a compressed desktop sidebar.

- Added `MobileShellHeader`, a compact safe-area-aware header shared by the member, administration, and secretary shells.
- Reworked `MobileBottomNavigation` as a five-destination thumb-friendly dock with an explicit active state, 44px-plus targets, safe-area spacing, and a dedicated `More` entry.
- Curated primary destinations by role. The complete role-scoped navigation remains available in the `More` drawer; no frontend rule grants access beyond the backend authorization model.
- Kept the full sidebar and desktop header at `lg` and above, while tablets and phones use the mobile shell.
- Added short route transitions using only opacity and transform, with reduced-motion support.
- Simplified the public sign-in surface on mobile: the form is first, decorative gradients are removed, and the product explanation is compact.
- Added Playwright coverage confirming the dock exposes five actions and opens the complete mobile menu.

Validation after this follow-up:

```bash
npm run type-check
npm run build
npx playwright test e2e/responsive-mobile.spec.ts --project=chromium
```

- TypeScript: OK.
- Production build: OK, 288 modules and 96 PWA precache entries.
- Responsive Playwright suite: OK, 26/26 tests across 320px to 1440px viewports.
