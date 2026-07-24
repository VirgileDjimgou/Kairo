# PROMPT UNIVERSEL — Déploiement et ajustements du frontend Kairo

## Contexte

Tu travailles sur le projet Kairo, une application de gestion d'association multi-tenant avec backend Python/FastAPI et frontend Vue 3. Le dépôt est à `C:\Users\djimg\source\repos\Kairo` (ou équivalent Linux `/opt/kairo`).

Une refonte mobile-first complète du frontend a été effectuée. **Le code est prêt, compilé, et testé.** Ta mission est de :

1. Lire la documentation pour comprendre l'architecture
2. Reconstruire l'application (vérifier que tout compile)
3. Déployer ou redéployer en production
4. Identifier et corriger les éventuels problèmes résiduels

---

## Fichiers à lire en premier (dans cet ordre)

```
docs/FRONTEND_ARCHITECTURE.md   ← INVENTAIRE COMPLET (à lire impérativement)
docs/RESPONSIVE_TEST_REPORT.md  ← Rapport avant/après, fichiers modifiés
docs/UI_MOBILE_AUDIT.md         ← Audit initial des problèmes
docs/DESIGN_SYSTEM.md           ← Design tokens, grille, typographie
AGENTS.md                       ← Règles du projet
```

---

## État actuel du code

### Build vérifié
```
apps/web/
  npm run type-check   → 0 erreur TypeScript
  npm run build        → 285 modules compilés, PWA 90 entrées precache, 2.1s
```

### Fichiers modifiés (20 tracked)
```
apps/web/index.html              — PWA meta tags, viewport-fit=cover, theme-color
apps/web/vite.config.ts          — Plugin VitePWA ajouté
apps/web/package.json            — Dépendance vite-plugin-pwa
apps/web/nginx.conf              — Règles cache PWA (sw.js 24h, manifest 7d + MIME)
apps/web/src/styles/variables.scss — 40+ design tokens (legacy --om-* préservés)
apps/web/src/styles/main.scss    — Imports réorganisés, Bootstrap overrides, touch targets
apps/web/src/i18n/messages.ts    — +52 clés auth/layout (fr/en/de)
apps/web/src/layouts/AppLayout.vue      — Bottom nav mobile, 100dvh, safe areas
apps/web/src/layouts/AdminLayout.vue    — 100dvh
apps/web/src/layouts/SecretaryLayout.vue — Offcanvas mobile ajouté, i18n nav
apps/web/src/views/chat/ChatView.vue    — Split view mobile (liste OU chat)
apps/web/src/components/chat/ChatSidebar.vue — Prop `visible`
apps/web/src/views/dashboard/DashboardView.vue — col-xl → col-lg, padding
apps/web/src/views/auth/ForgotPasswordView.vue — i18n complète
apps/web/src/views/auth/ResetPasswordView.vue  — i18n complète
apps/web/src/views/auth/AcceptInviteView.vue   — i18n complète
apps/web/src/views/auth/MfaSetupView.vue       — i18n complète
infra/reverse-proxy/Caddyfile   — Headers PWA + Permissions-Policy
```

### Fichiers créés (19 untracked)
```
docs/FRONTEND_ARCHITECTURE.md
docs/DESIGN_SYSTEM.md
docs/UI_MOBILE_AUDIT.md
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

---

## Déploiement

### Option 1 — Build local simple
```bash
cd apps/web
npm install          # installer les dépendances (dont vite-plugin-pwa)
npm run type-check   # doit retourner 0 erreur
npm run build        # doit générer dist/ + sw.js + manifest.webmanifest
```

### Option 2 — Docker (recommandé)
```bash
# Depuis la racine du projet
docker compose -f docker-compose.yml -f docker-compose.prod.yml build api web worker
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Option 3 — Docker + Caddy + Cloudflare Tunnel
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml \
  -f infra/reverse-proxy/docker-compose.caddy.yml up -d --build

# Si tunnel Cloudflare (CLOUDFLARE_TUNNEL_TOKEN dans .env)
docker compose --profile tunnel up -d cloudflared
```

### Option 4 — Script de release automatisé
```bash
bash scripts/deploy_release.sh preflight    # Vérifications
bash scripts/deploy_release.sh upgrade      # Déploiement + backup + migration + smoke test
```

### Vérification post-déploiement
```bash
bash scripts/production_smoke.sh https://app.combissportverein.org
# Vérifie: /health (200), /metrics (200), / (200), /docs (404), /redoc (404), /openapi.json (404)
```

Vérifier aussi que la PWA est servie :
```bash
curl -I https://app.combissportverein.org/sw.js
# → Content-Type: application/javascript; Cache-Control: public, max-age=86400

curl -I https://app.combissportverein.org/manifest.webmanifest
# → Content-Type: application/manifest+json
```

---

## Ajustements potentiels à vérifier/corriger

### 1. Icônes PWA (manquantes)
Le manifest référence `/pwa-192x192.png` et `/pwa-512x512.png` mais ces fichiers n'existent pas dans `public/`. **Action** : générer des icônes PNG 192×192 et 512×512 et les placer dans `apps/web/public/`. En attendant, le PWA fonctionne sans (juste pas d'icône d'installation).

### 2. i18n résiduelle (vues partiellement en anglais)
Certaines vues admin ont encore du texte anglais hardcodé dans les templates. Les vues concernées :
- `AdminAccessView.vue` — labels et placeholders
- `AuditTrailView.vue` — filtres et en-têtes
- `AdminChatQueriesView.vue` — titres et labels
- `MyDisciplinaryView.vue` — titres

**Action si temps** : ajouter les clés manquantes dans `messages.ts` (section `admin.*`, `audit.*`) et remplacer les strings hardcodés par `t('admin.xxx')`. Le pattern exact est visible dans les 4 vues auth déjà refaites.

### 3. 15 tableaux utilisent `table-responsive` (scroll horizontal)
Le composant `ResponsiveDataView.vue` est prêt à l'emploi pour remplacer les tableaux par des cartes sur mobile. **Action** : remplacer progressivement `<div class="table-responsive"><table>...</table></div>` par `<ResponsiveDataView :items="..." >` dans les vues admin. Priorité : `AdminContributionsView` (8 colonnes), `FinanceWorkspaceView` (8 colonnes).

### 4. Pattern `copy` computed (17 vues)
Les vues utilisent un pattern `copy` computed avec switch manuel fr/en/de au lieu de `localeStore.t()`. C'est fonctionnel mais duplique les chaînes hors de `messages.ts`. **Action** : migration progressive, pas bloquante.

### 5. LoginView orbes décoratives
Les orbes `.login-orb-one` (288px) et `.login-orb-two` (224px) peuvent être simplifiées pour mobile. `overflow-x: clip` compense déjà.

### 6. Tests E2E responsive
Le fichier `apps/web/e2e/responsive-mobile.spec.ts` contient 22 tests sur 9 viewports. Pour les exécuter :
```bash
cd apps/web
npx playwright test e2e/responsive-mobile.spec.ts --project=chromium
```
Nécessite que le backend tourne sur `localhost:8000`.

---

## Commandes essentielles (rappel)

```bash
# Frontend uniquement
cd apps/web
npm install
npm run type-check      # TypeScript
npm run build           # Vite + PWA
npm run preview         # Prévisualiser le build

# Backend
cd services/api
pip install -r requirements.txt
uvicorn app.main:app --reload

# Docker (tout)
docker compose up -d --build
docker compose logs -f web api

# Tests E2E
cd apps/web
npx playwright install chromium
npx playwright test
```

---

## Règles non négociables (rappel du projet)

- Toute requête backend doit inclure `tenant_id`
- Le backend est le seul point d'application des politiques
- Le LLM ne décide jamais des contrôles d'accès
- Le filtrage de retrieval doit avoir lieu avant l'assemblage du prompt
- Les clés i18n doivent exister dans les 3 locales (fr, en, de)
- Utiliser `localeStore.t('key')` pour tout texte visible
- Bootstrap 5 est conservé — ne pas le remplacer
- Pas de nouvelle dépendance lourde sans justification

---

## Instructions d'exécution

1. **Lis** `docs/FRONTEND_ARCHITECTURE.md` en premier
2. **Vérifie** que le build frontend passe : `cd apps/web && npm run build`
3. **Déploie** selon l'option appropriée (Docker recommandé)
4. **Exécute** le smoke test : `bash scripts/production_smoke.sh [URL]`
5. **Vérifie** les endpoints PWA : `sw.js` et `manifest.webmanifest`
6. **Corrige** les problèmes résiduels listés ci-dessus (section "Ajustements potentiels")
7. **Met à jour** `docs/RESPONSIVE_TEST_REPORT.md` avec les corrections effectuées
8. **Rapporte** le résultat : build OK/KO, déploiement OK/KO, corrections faites
