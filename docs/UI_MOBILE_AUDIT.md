# Kairo — Audit Mobile-First & Responsive

**Date:** 2026-07-24  
**Auditeur:** Lead Frontend Engineer  
**Périmètre:** 35 vues Vue 3, 3 layouts, 3 composables, 23 specs E2E  
**Viewport cible:** 320px (Galaxy Fold / iPhone SE)

---

## 1. État actuel

| Aspect | État |
|---|---|
| Framework | Vue 3.5 + TypeScript 5.7 + Vite 6 |
| CSS | Bootstrap 5.3 + Sass/SCSS |
| Icônes | Bootstrap Icons 1.11 |
| State | Pinia 2.3 (4 stores) |
| Routing | Vue Router 4, HTML5 History mode |
| i18n | Custom (localeStore), 3 locales (fr/en/de) |
| Responsive | Classes utilitaires Bootstrap uniquement, 1 media query dans LoginView |
| PWA | Aucune |
| Mobile natif | Aucun wrapper |
| Tests mobile | 1 seul test E2E à 390x844 (login) |

**Verdict global :** L'application fonctionne sur mobile grâce à Bootstrap mais reste une interface desktop administratif réduite. Les utilisateurs membres (cible mobile principale) subissent une expérience dégradée.

---

## 2. Problèmes critiques (bloquants)

| # | Fichier | Ligne | Problème |
|---|---------|-------|----------|
| C1 | `layouts/SecretaryLayout.vue` | 3 | Sidebar cachée sous 992px sans alternative de navigation mobile. Les utilisateurs secrétaires sur téléphone n'ont aucune navigation. |
| C2 | `views/chat/ChatView.vue` | 220 | `height: calc(100vh - 60px)` — `100vh` ne tient pas compte de la barre d'adresse dynamique des navigateurs mobiles. Contenu coupé. |
| C3 | `views/auth/ForgotPasswordView.vue` | tout | Vue entière en anglais hardcodé. Aucune i18n. Première interaction utilisateur = défaut majeur. |
| C4 | `views/auth/ResetPasswordView.vue` | tout | Idem — vue entièrement non localisée. |
| C5 | `views/auth/AcceptInviteView.vue` | tout | Idem. |
| C6 | `views/auth/ForgotPasswordView.vue` | 2 | `min-vh-100` (Bootstrap = `100vh`, pas `100dvh`). Problématique sur mobile. |
| C7 | `views/auth/ResetPasswordView.vue` | 2 | Idem. |
| C8 | `views/auth/AcceptInviteView.vue` | 2 | Idem. |
| C9 | `layouts/SecretaryLayout.vue` | 2 | `min-vh-100` — idem. |

---

## 3. Problèmes élevés (UX mobile très dégradée)

### 3.1 Cibles tactiles trop petites (< 44px)

| Fichier | Lignes | Composant |
|---------|--------|-----------|
| `AdminMembersView.vue` | 78-84 | Boutons icônes `.btn-sm` (31px) |
| `AdminEventsView.vue` | 60-64 | Idem |
| `AdminContributionsView.vue` | 97-104 | Idem |
| `AdminPoliciesView.vue` | 146-151 | `.btn-group-sm` |
| `CensorWorkspaceView.vue` | 253-259 | `.btn-group-sm` |
| `AdminAnnouncementsView.vue` | 67-70 | Icônes `.btn-sm` |
| `FinanceWorkspaceView.vue` | 347-358 | `.btn-sm` boutons |
| `AdminDisciplinaryView.vue` | 109 | Icônes `.btn-sm` |
| `SportsWorkspaceView.vue` | 149 | Icônes `.btn-sm` |

### 3.2 Tableaux avec scroll horizontal (15 vues)

Toutes utilisent `table-responsive` (Bootstrap 5). C'est correct pour des tableaux à 3-4 colonnes, mais les tableaux à 7-8 colonnes nécessitent un scroll important. Vues concernées :

- `AdminAccessView` — 5-6 colonnes
- `AdminDocumentsView` — 7 colonnes
- `AdminHealthCenterView` — 3 colonnes (acceptable)
- `MyProfileView` — 6 colonnes
- `AdminMembersView` — 6 colonnes
- `AdminEventsView` — 7 colonnes
- `AdminAnnouncementsView` — 5 colonnes
- `AdminPoliciesView` — 6 colonnes
- `AdminContributionsView` — 8 colonnes
- `CensorWorkspaceView` — 7 colonnes
- `AdminDisciplinaryView` — 7 colonnes
- `FinanceWorkspaceView` — 8 colonnes
- `AuditorFinanceView` — 5 colonnes
- `SportsWorkspaceView` — 7 colonnes

### 3.3 Navigation mobile utilisateur (bottom nav absente)

La navigation actuelle repose soit sur :
- Sidebar desktop fixe (260px)
- Offcanvas Bootstrap en hamburger

Sur mobile, le hamburger est fonctionnel mais peu pratique pour des changements fréquents de section. Une **bottom navigation bar** (3-5 onglets) est le standard mobile moderne.

### 3.4 ChatSidebar fixe (280px) non adaptée au mobile

Le composant `ChatSidebar.vue` a `width: 280px; min-width: 280px`. Sur un écran 320px, la sidebar + la zone de chat ne peuvent coexister. Aucune adaptation pour afficher la liste des conversations en plein écran sur mobile.

---

## 4. Problèmes moyens (sous-optimal)

| # | Fichier | Problème |
|---|---------|----------|
| M1 | `AdminOverviewView.vue:13-29` | 5 boutons + refresh dans une rangée qui déborde entre 768-1200px |
| M2 | `AdminHealthCenterView.vue:13-23` | 4 boutons en rangée, crowding identique |
| M3 | `TenantOperationsView.vue:13-23` | Idem |
| M4 | `AuditTrailView.vue:56-121` | 8 filtres qui deviennent 8 inputs empilés sur 320px |
| M5 | `AdminAccessView.vue:384-401` | Cartes summary pouvant atteindre 6+ items, scroll long |
| M6 | `DashboardView.vue` (multiples) | `flex-xl-row` au lieu de `flex-lg-row`, wrapping inutile entre 992-1200px |
| M7 | `AdminDocumentsView.vue:308` | 4-5 boutons d'action empilés verticalement par ligne sur mobile |
| M8 | `AuditTrailView.vue:300` | `.detail-pill` avec `min-width: 180px`, layout inégal sur 320px |

---

## 5. Problèmes faibles (cosmétiques)

- Auth recovery views : liens "Back to sign in" en `small text-muted` avec police 12px, difficile à taper
- `LoginView.vue` : orbes décoratives de 288px avec `right: -6rem` — compensé par `overflow-x: clip`
- 17 vues utilisent le pattern `copy` computed avec triple switch fr/en/de — fonctionnel mais lourd à maintenir
- Messages d'erreur vagues dans certaines vues ("Une erreur est survenue")

---

## 6. Vues non localisées (i18n manquante)

| Vue | Gravité |
|-----|---------|
| `auth/ForgotPasswordView.vue` | Critique |
| `auth/ResetPasswordView.vue` | Critique |
| `auth/AcceptInviteView.vue` | Critique |
| `auth/MfaSetupView.vue` | Élevée |
| `admin/AdminChatQueriesView.vue` | Élevée |
| `admin/AuditTrailView.vue` | Élevée |
| `admin/AdminAccessView.vue` | Élevée |
| `admin/TenantOperationsView.vue` | Moyenne |
| `members/MyDisciplinaryView.vue` | Élevée |
| `layouts/SecretaryLayout.vue` | Élevée |
| `disciplinary/CensorWorkspaceView.vue` | Moyenne |
| `account/AccountSecurityView.vue` | Moyenne |

---

## 7. Vues prioritaires pour la refonte

1. **Login + Auth recovery** — Première impression, forte exposition mobile
2. **Dashboard (DashboardView)** — Page d'accueil, tous les rôles
3. **Chat (ChatView + ChatSidebar)** — Fonctionnalité clé membre
4. **Profil membre (MyProfileView)** — Usage fréquent
5. **Layouts (AppLayout, AdminLayout, SecretaryLayout)** — Fondations
6. **Événements (EventsView)** — Consultation mobile fréquente
7. **Annonces (AnnouncementsView)** — Lecture mobile

---

## 8. Risques de régression

- Modification des layouts : impacte toutes les vues enfants
- Changement de breakpoints Bootstrap : peut casser les mises en page desktop
- Remplacement de `100vh` par `100dvh` : nécessite fallback pour anciens navigateurs
- Ajout bottom navigation : redessine complètement l'expérience de navigation
- i18n des vues auth : touche au flux d'authentification

---

## 9. Quick wins (peuvent être faits immédiatement)

1. Remplacer tous les `100vh` par `100dvh` + fallback
2. Ajouter `-webkit-tap-highlight-color: transparent` global
3. Ajouter `touch-action: manipulation` sur tous les boutons
4. Passer les `.btn-sm` en `.btn` pour les icônes d'action dans les tableaux
5. Ajouter le meta `theme-color` pour Android
6. Ajouter `overscroll-behavior: none` sur le body pour éviter le pull-to-refresh parasite

---

## 10. Composants manquants identifiés

| Composant | Justification |
|-----------|---------------|
| `MobileBottomNavigation` | Navigation principale 3-5 onglets pour membres |
| `ResponsiveDataView` | Remplace `table-responsive` par cartes sur mobile |
| `MobileDataCard` | Représentation mobile d'une ligne de tableau |
| `AppShell` | Layout racine avec gestion safe-area |
| `PageHeader` | En-tête de page cohérent |
| `EmptyState` | État vide avec action |
| `SkeletonLoader` | État de chargement squelettes |
| `ToastContainer` | Notifications toast |

---

## 11. Plan d'implémentation proposé

### Étape A — Fondations (1-2 jours)
- Tokens CSS/SCSS centralisés
- Variables breakpoints, espacements, couleurs
- Corrections `100vh` → `100dvh`
- Safe areas CSS
- Quick wins tactiles

### Étape B — Design System (2-3 jours)
- Grille 4/6/12 colonnes
- Typographie définie
- Palette de couleurs
- Composants de base : AppShell, PageHeader, AppButton

### Étape C — Navigation mobile (2-3 jours)
- MobileBottomNavigation pour AppLayout
- Drawer pour AdminLayout
- Navigation pour SecretaryLayout

### Étape D — Vues prioritaires (3-5 jours)
- Login/Auth → mobile-first
- Dashboard → responsive cards
- Chat → mobile messaging UX
- Profil → carte adaptative

### Étape E — Vues secondaires (3-5 jours)
- Tableaux → ResponsiveDataView
- Formulaires → single-column mobile
- Modals → bottom sheets

### Étape F — Qualité (2-3 jours)
- Accessibilité WCAG AA
- Tests responsive
- Performance bundle
- Documentation

---

## 12. Critères de validation

- [ ] Aucune vue avec overflow horizontal à 320px
- [ ] Navigation mobile utilisable au pouce
- [ ] Cibles tactiles ≥ 44×44px
- [ ] Formulaires fonctionnels avec clavier Android ouvert
- [ ] Contenu non masqué par les barres fixes
- [ ] Layouts desktop préservés
- [ ] Cohérence visuelle entre toutes les vues
- [ ] Contraste suffisant (WCAG AA)
- [ ] Focus clavier visible
- [ ] Animations respectant `prefers-reduced-motion`
- [ ] Build TypeScript OK
- [ ] Tests E2E existants OK
- [ ] Nouveaux tests responsive sur 5 viewports mobiles
