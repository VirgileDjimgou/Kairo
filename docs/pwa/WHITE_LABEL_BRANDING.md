# White-Label Tenant Branding

Status: Active — Roadmap V2 Sprint 123
Related: `docs/notifications/NOTIFICATION_INSTALLATION_MODEL.md`,
`docs/pwa/PWA_ARCHITECTURE.md`, ADR-014

Kairo separates **platform identity** from **tenant identity**. The platform
provides safe Kairo defaults; each tenant may override any subset through
configuration. No business logic, authorization decision or module toggle may
depend on a branding value.

## Canonical contract: `TenantBranding`

Stored in `tenants.branding_json`, exposed through `GET/PUT
/api/v1/tenants/{tenant_id}/settings` (`branding`) and through every
`/auth/me` membership, consumed by the Vue PWA. FastAPI's schema is the source of
truth (`services/api/app/modules/tenancy/schemas.py`).

| Field | Default | Purpose |
| --- | --- | --- |
| `display_name` | `Kairo` | Application name: page title, splash, app identity |
| `short_name` | `Kairo` | Launcher/install short label |
| `legal_name` | `""` | Legal entity name for documents/emails |
| `logo_url` / `logo_dark_url` | `""` | Shell and dark-surface logos |
| `favicon_url` | `""` | Browser favicon (falls back to `/favicon.svg`) |
| `icon_192_url` / `icon_512_url` / `maskable_icon_url` | `""` | PWA/launcher icons (applied by S124) |
| `primary_color` / `secondary_color` | `#1f4f8f` / `#2f6f55` | Semantic UI colors (`--om-primary`, `--om-secondary`) |
| `background_color` / `theme_color` | `#f8f9fb` / `#1a3f6b` | PWA/manifest and browser theme |
| `notification_name` | `Kairo` | Push sender title and transactional email sender |
| `support_name` / `support_email` | `Kairo Support` / `""` | Support contact in emails |
| `custom_domain` | `""` | Association hostname (resolved by S125) |

Validation:

- colors must be 3- or 6-digit hex;
- asset fields accept only `https(s)://` URLs or site-relative `/paths`
  (a `javascript:` or `data:` value is rejected with `422`);
- `custom_domain` must be a valid lowercase hostname.

## Applied surfaces

| Surface | Consumer |
| --- | --- |
| Authentication / shell / dashboard | `apps/web/src/services/branding.ts` applies `--om-primary`, `--om-secondary`, `--om-background`; `AppShell` renders the tenant logo in the top bar |
| Page title, favicon, theme-color, apple title | `applyBranding()` on every tenant change (safe defaults for missing values) |
| Navigation and layouts | Existing semantic CSS variables, so no component-specific branding code |
| Push sender | Outbox worker resolves `notification_name` per tenant for the push title; generic body unchanged |
| Transactional email | Invitation and password-reset subjects/bodies use `notification_name`, `support_name` and `support_email` when configured |
| PWA manifest and launcher identity | `GET /api/v1/tenants/public/{slug}/manifest` returns the tenant-aware manifest (name, short name, colors, absolute icons, `start_url`, `scope`); the PWA swaps the manifest link after sign-in and offers an explicit install CTA |
| Install UX | `beforeinstallprompt` CTA, `appinstalled` confirmation, dismissal persistence, standalone detection and browser-specific guidance; notification permission is never requested during installation |
| Host-based tenant resolution | `GET /api/v1/tenants/public/resolve` maps an exact `custom_domain` or a direct `<slug>.<PLATFORM_BASE_DOMAIN>` subdomain to a tenant (branding-only, server-authoritative); the PWA applies it pre-authentication and seeds `tenant_slug` for login. See `docs/pwa/TENANT_DOMAINS.md` |

## Configuring branding from the admin UI (S129)

An authorized tenant administrator configures the complete identity in
**Admin → Settings → Branding**: display/short/legal name, primary, secondary,
background and theme colors, light/dark logos, favicon, the launcher icons
(192×192, 512×512 and maskable), the notification sender name, the support
identity and the custom domain. The live preview shows the branded header, the
color swatches and the install-icon rendering before saving; the existing
`PUT /api/v1/tenants/{id}/settings` endpoint persists the values and they reach
`/auth/me`, the public tenant manifest and the installed PWA identity.

Installation icons are URLs: host the association assets at an https URL or a
site-relative path served by the deployment. Android Chrome mints the installed
WebAPK name/icon from the tenant manifest at install time; iOS reads the
`apple-touch-icon` that the PWA injects per tenant (manifest icons remain the
fallback). Because the installed app identity is bound to the origin, an
association that wants its own installable app alongside another must use its
custom domain (`docs/pwa/TENANT_DOMAINS.md`).

## Testing the identity from the public demo page (S129)

`/demo` includes a password-free **white-label studio**: change the name, short
name, colors, logo and launcher icons and the page title, CSS variables, favicon,
`apple-touch-icon`, install-icon previews and the generated manifest update
live. Presets, a manifest preview and install guidance are included; nothing is
persisted and the reset action restores the real branding. This lets an operator
test the white-label mode end to end without touching a tenant.

## Configuration only — no conditional code

The COMBIS pilot is configured entirely through data, for example:

```http
PUT /api/v1/tenants/{tenant_id}/settings
{
  "branding": {
    "display_name": "COMBIS App",
    "short_name": "COMBIS",
    "notification_name": "COMBIS",
    "primary_color": "#0a5c2e",
    "theme_color": "#0a5c2e",
    "favicon_url": "/favicon.svg",
    "support_email": "support@combis.example"
  }
}
```

There is no COMBIS-specific branch, constant or asset path anywhere in the
product source; the demo tenant and any association use the same contract.

## Verification

- Backend: `services/api/tests/test_tenant_branding.py` covers defaults,
  persistence, membership exposure, unsafe-value rejection, push sender naming
  and the fact that branding does not change roles/modules.
- Web: `apps/web/e2e/tenant-branding.spec.ts` covers title, favicon,
  theme-color, logo, primary color, defaults and unsafe-asset fallback.
- Commands: `python -m pytest services/api/tests/test_tenant_branding.py -q` and
  `cd apps/web && npm run test:e2e:whitelabel`.
- Real stack (S128): the release gate verifies COMBIS branding on `/auth/me`, the
  `COMBIS App` page title and the tenant manifest against the production-like
  stack (`node scripts/run-full-stack-gate.mjs`, `npm run test:e2e:real`); see
  `docs/pwa/COMBIS_PILOT_CHECKLIST.md`.
