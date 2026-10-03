# Tenant Domains And Host-Based Resolution

Status: Active — Roadmap V2 Sprint 125
Related: `docs/pwa/WHITE_LABEL_BRANDING.md`, `docs/pwa/PWA_ARCHITECTURE.md`,
`docs/notifications/NOTIFICATION_INSTALLATION_MODEL.md`

Kairo serves every association from one deployment. Association-specific
addresses are **configuration**, resolved by the backend from the request host;
no per-association deployment or frontend exists.

## Mapping rules (server-authoritative)

`GET /api/v1/tenants/public/resolve` reads the request `Host` header (nginx
forwards `Host $host` for `/api/`) and resolves a tenant only through:

1. **Exact custom domain** — `tenants.custom_domain` (unique, indexed) must equal
   the normalized host, e.g. `app.customer-domain.de`.
2. **Direct platform subdomain** — `<slug>.<PLATFORM_BASE_DOMAIN>`, e.g.
   `combis.kairo.example` when `PLATFORM_BASE_DOMAIN=kairo.example`. Nested
   subdomains (`extra.combis.kairo.example`) do not resolve.

Hosts are normalized to lowercase, port-stripped and trailing-dot-stripped.
Unknown hosts, inactive tenants and client-supplied overrides (`?tenant=`,
`?slug=`) never select a tenant: the endpoint has no parameters and returns
`404` when the host is unmapped. The response exposes branding-only data plus
the tenant manifest URL.

- The custom domain is set through tenant settings branding
  (`custom_domain`) and mirrored into the indexed column. Saving a domain that
  another tenant already uses returns `409`.
- The frontend never sends a tenant identifier for host resolution. It applies
  the resolved tenant branding and manifest pre-authentication and seeds
  `tenant_slug` for the login request; the backend still validates membership.

## HTTPS, cookies, CORS, CSRF and Service Worker review

| Concern | Kairo behavior |
| --- | --- |
| HTTPS | Every tenant host must terminate TLS (Cloudflare/nginx). The PWA refuses obsolete HTTP API URLs on HTTPS pages; production uses the same-origin `/api/` proxy. |
| Cookies | Kairo authenticates with Bearer tokens in storage, not cookies. There is no cross-domain cookie scope to leak between tenants. |
| CORS | Production is same-origin per host (nginx proxies `/api/`). `CORS_ORIGINS` stays explicit for development; adding a tenant host does not add a wildcard. |
| CSRF | No cookie-authenticated state-changing endpoint exists; Bearer tokens are not sent automatically by the browser. |
| Service Worker scope | One worker per origin, scope `/`. A tenant host is a distinct origin with its own worker, cache and precache manifest. |
| Web Push origin | Push subscriptions are origin-bound. A subscription created on `combis.kairo.example` can never be delivered through another tenant origin, and backend recipient resolution remains authoritative. |
| Manifest | Each host serves its own tenant manifest; the launcher identity follows the host. |

## Tenant onboarding runbook

1. **Create the tenant** — provision the organization record (slug, name,
   default language).
2. **Configure branding** — `PUT /api/v1/tenants/{id}/settings` with the
   `branding` object: `display_name`, `short_name`, `notification_name`, colors,
   logos, icons (192/512/maskable), favicon, support contact.
3. **Assign the domain** — set `branding.custom_domain` (exact host) and/or rely
   on the platform subdomain `<slug>.<PLATFORM_BASE_DOMAIN>`. Confirm `409`
   conflicts are resolved.
4. **DNS and TLS** — point the hostname at the deployment (Cloudflare Tunnel or
   reverse proxy) and confirm a valid certificate; verify `https://<host>/api/v1/tenants/public/resolve`
   returns the tenant.
5. **Principal administrator** — create the tenant's principal admin account and
   complete the first-login password change.
6. **Roles and permissions** — verify the canonical role catalog and any
   tenant-specific role bundles; confirm module toggles.
7. **PWA installation** — open the tenant host, sign in, confirm the branded
   title/favicon/manifest, install through the in-app CTA, and verify the
   launcher name. Notification opt-in stays an explicit, separate action.
8. **Verification** — run `test_tenant_domains.py`, the white-label Playwright
   pack and, for a real pilot, the S128 device checklist.

## Verification

- Backend: `services/api/tests/test_tenant_domains.py` covers custom-domain and
  subdomain resolution, host normalization, unknown/nested/inactive rejection,
  client-override immunity and cross-tenant uniqueness.
- Web: `apps/web/e2e/host-tenant.spec.ts` covers pre-auth branding/manifest from
  the resolved host, safe defaults for unmapped hosts and login tenant seeding.
- Commands: `python -m pytest services/api/tests/test_tenant_domains.py -q` and
  `cd apps/web && npm run test:e2e:whitelabel`.
- Real stack (S128): `node scripts/run-full-stack-gate.mjs` resolves the
  `combis.kairo.test` subdomain and the `app.combis.test` custom domain through
  the real gateway and proves an unknown host is rejected with `404`; the manual
  custom-domain device step is in `docs/pwa/COMBIS_PILOT_CHECKLIST.md`.
