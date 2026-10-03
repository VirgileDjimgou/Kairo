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
| PWA manifest, launcher icons, install UX | Planned in S124 (consumes the same contract) |
| Host-based tenant resolution | Planned in S125 (consumes `custom_domain`) |

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
