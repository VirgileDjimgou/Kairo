# Complete White-Label Customer Demo Tutorial

Status: active operator tutorial (Roadmap V2 Sprint 130). It describes the full
customer cycle: brand the application as a chosen association (for example
**Foot100**), persist the identity as an administrator, install it on Android and
PC, run the whole business simulation and verify notifications under the
association identity.

Related documents:

- `docs/pwa/WHITE_LABEL_BRANDING.md` — branding contract and configuration
- `docs/pwa/PWA_ARCHITECTURE.md` — manifest, Service Worker and install flow
- `docs/pwa/COMBIS_PILOT_CHECKLIST.md` — manual device checklist
- `docs/pwa/TENANT_DOMAINS.md` — custom domains and onboarding runbook

## 0. Prerequisites

- A reachable URL: the production host, a Cloudflare tunnel, or `http://localhost:8090`
  on the PC that runs the stack. **Installation requires HTTPS** on phones; the PC
  can install from `localhost`.
- Seeded demo accounts (the `demo` tenant):

| Role | Account | Password |
| --- | --- | --- |
| Principal administrator | admin@demo.org | Admin123! |
| Secretary general | secretary@demo.org | Secretary123! |
| Treasurer | treasurer@demo.org | Treasurer123! |
| President | president@demo.org | President123! |
| Auditor | auditor@demo.org | Auditor123! |
| Censor | censor@demo.org | Censor123! |
| Sports manager | sports@demo.org | Sports123! |
| Vice president | vice-president@demo.org | VicePresident123! |
| Member | alice@demo.org | Member123! |

The public `/demo` page opens every role with one click, including the principal
administrator (advanced section) — no password is typed during a demo.

## 1. Brand the application as Foot100 (administrator)

1. Open `<URL>/demo` and click **Tester le white-label** to explore the preview
   studio (optional, nothing is saved).
2. Expand **Rôles avancés** and click **Administrateur principal** to open the
   demo tenant as its administrator in one click.
3. Go to **Administration → Réglages** (`/admin/settings`) and fill the
   **Identité visuelle** card:
   - Application name: `Foot100`
   - Short name (icon): `Foot100`
   - Tagline: `Le club qui avance ensemble` (or any slogan)
   - Colors, logo, favicon, launcher icons 192/512/maskable, notification sender
     name, support identity and custom domain as needed.
   - The live preview shows the branded header, colors and install icon before
     saving.
4. **Save settings.** The page title, favicon, theme color, CSS variables, the
   notification sender and the tenant manifest now carry Foot100.
5. Verify from a terminal (no sign-in required):

   ```bash
   curl -s <URL>/api/v1/tenants/public/demo/manifest
   ```

   The manifest returns `"name": "Foot100"`, the tagline in `description` and the
   launcher icons.

The public studio on `/demo` is a local preview; only the admin settings persist
the identity for the tenant.

## 2. Install on Android with the Foot100 identity

1. Open the HTTPS URL in Chrome (or Samsung Internet / Edge / Brave) on the phone.
2. **Sign in first** (for example `alice@demo.org` / `Member123!`, or any
   one-click role). The tenant manifest is applied after sign-in.
3. Install:
   - the in-app banner **« Installer »** appears in Chromium browsers → tap it and
     confirm; or
   - Chrome menu **⋮ → Installer l'application** (sometimes « Ajouter à l'écran
     d'accueil »).
4. The home-screen name and icon come from the tenant manifest (`short_name`,
   192/512/maskable icons). Reinstall after a branding change: Chrome refreshes
   the installed WebAPK on later visits, and uninstalling/reinstalling forces it.

## 3. Install on PC

- **Edge or Chrome**: open the URL, sign in, then use the install icon in the
  address bar or **menu → Applications → Installer ce site en tant
  qu'application**. The app opens in its own window under the Foot100 name.
- **Safari (macOS)**: Fichier → Ajouter au Dock.

## 4. Full business simulation

1. **Member**: sign in as secretary (one click), open **Membres**, create
   `Jean Test` with a structured address. The backend generates the member code
   and the `@` address.
2. **Contributions**: as secretary, declare a cash receipt for Jean Test
   (finance receipt declaration). As treasurer, open the validation queue,
   validate the receipt, record the payment and check the annual budget.
3. **Sanction**: as censor, create a disciplinary record; as the member, open
   **Mes sanctions** and confirm only personal records are visible.
4. **Governance**: as secretary publish an announcement and an event; as
   president open the governance cockpit; as auditor confirm the read-only
   finance view.
5. **Cross-checks**: as Tenant X (gate stack) confirm the COMBIS data is not
   visible — tenant isolation is enforced by the backend.

## 5. Notifications and the association identity

- The authenticated inbox always works (tenant-isolated, durable).
- Push **titles** use the tenant `notification_name` (`Foot100`) for both Web
  Push (VAPID) and Android FCM; the outbox resolves the branding per tenant.
- The Service Worker stores the tenant notification identity; a push that
  arrives without a title is attributed to the association, never to the
  platform name.
- On Android the notification is attributed to the installed app, whose name and
  icon come from the tenant manifest at install time.
- **Firebase**: the FCM project name visible in the Firebase console is a
  developer-side label; end-user notifications show the tenant identity. Each
  association can use its own Firebase project through the deployment
  configuration (`FIREBASE_*` variables), without code changes.
- Local demo limitation: when Firebase/VAPID are not configured on the stack,
  push delivery is disabled but the inbox and the tenant notification name
  remain verifiable; the release-gate environment validates installation
  registration, revocation and inbox delivery.

## 6. Known constraints

- The installed app identity is bound to the **origin**: two associations can run
  side by side only when each uses its own custom domain
  (`docs/pwa/TENANT_DOMAINS.md`).
- Branding assets are URLs (https or site-relative); host them yourself.
- The manual Android device steps (closed-app push, deep link, revocation,
  application update) are tracked in `docs/pwa/COMBIS_PILOT_CHECKLIST.md`.
